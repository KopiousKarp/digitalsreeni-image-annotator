import numpy as np
from PyQt5.QtGui import QImage, QColor
from sam2.build_sam import build_sam2 
from sam2.sam2_image_predictor import SAM2ImagePredictor
import torch

class SAMUtils:
    def __init__(self):
        self.sam_models = {
            "SAM 2 tiny": "/opt/sam2/checkpoints/sam2.1_hiera_tiny.pt",
            "SAM 2 small": "/opt/sam2/checkpoints/sam2.1_hiera_small.pt",
            "SAM 2 base": "/opt/sam2/checkpoints/sam2.1_hiera_base_plus.pt",
            "SAM 2 large": "/opt/sam2/checkpoints/sam2.1_hiera_large.pt"
        }
        self.model_configs = {
            "SAM 2 tiny": "/opt/sam2/sam2/sam2_hiera_t.yaml",
            "SAM 2 small": "/opt/sam2/sam2/sam2_hiera_s.yaml",
            "SAM 2 base": "/opt/sam2/sam2/sam2_hiera_b+.yaml",
            "SAM 2 large": "/opt/sam2/sam2/sam2_hiera_l.yaml"
        }
        self.current_sam_model = None
        self.sam_model = None
        self.sam_predictor = None
        if torch.cuda.is_available():
            self.device = torch.device("cuda")
        elif torch.backends.mps.is_available():
            self.device = torch.device("mps")
        else:
            self.device = torch.device("cpu")

        if self.device.type == "cuda":
        # use bfloat16 for the entire notebook
            torch.autocast("cuda", dtype=torch.bfloat16).__enter__()
            # turn on tfloat32 for Ampere GPUs (https://pytorch.org/docs/stable/notes/cuda.html#tensorfloat-32-tf32-on-ampere-devices)
            if torch.cuda.get_device_properties(0).major >= 8:
                torch.backends.cuda.matmul.allow_tf32 = True
                torch.backends.cudnn.allow_tf32 = True

        
    def change_sam_model(self, model_name):
        if model_name != "Pick a SAM Model":
            self.current_sam_model = model_name
            self.sam_model = build_sam2(self.sam_configs[self.current_sam_model],self.sam_models[self.current_sam_model],device=self.device)
            self.sam_predictor = SAM2ImagePredictor(self.sam_model)
            print(f"Changed SAM model to: {model_name}")
        else:
            self.current_sam_model = None
            self.sam_model = None
            self.sam_predictor = None
            print("SAM model unset")

    def qimage_to_numpy(self, qimage):
        width = qimage.width()
        height = qimage.height()
        fmt = qimage.format()

        if fmt == QImage.Format_Grayscale16:
            buffer = qimage.constBits().asarray(height * width * 2)
            image = np.frombuffer(buffer, dtype=np.uint16).reshape((height, width))
            image_8bit = self.normalize_16bit_to_8bit(image)
            return np.stack((image_8bit,) * 3, axis=-1)
        
        elif fmt == QImage.Format_RGB16:
            buffer = qimage.constBits().asarray(height * width * 2)
            image = np.frombuffer(buffer, dtype=np.uint16).reshape((height, width))
            image_8bit = self.normalize_16bit_to_8bit(image)
            return np.stack((image_8bit,) * 3, axis=-1)

        elif fmt == QImage.Format_Grayscale8:
            buffer = qimage.constBits().asarray(height * width)
            image = np.frombuffer(buffer, dtype=np.uint8).reshape((height, width))
            return np.stack((image,) * 3, axis=-1)
        
        elif fmt in [QImage.Format_RGB32, QImage.Format_ARGB32, QImage.Format_ARGB32_Premultiplied]:
            buffer = qimage.constBits().asarray(height * width * 4)
            image = np.frombuffer(buffer, dtype=np.uint8).reshape((height, width, 4))
            return image[:, :, :3]
        
        elif fmt == QImage.Format_RGB888:
            buffer = qimage.constBits().asarray(height * width * 3)
            image = np.frombuffer(buffer, dtype=np.uint8).reshape((height, width, 3))
            return image
        
        elif fmt == QImage.Format_Indexed8:
            buffer = qimage.constBits().asarray(height * width)
            image = np.frombuffer(buffer, dtype=np.uint8).reshape((height, width))
            color_table = qimage.colorTable()
            rgb_image = np.zeros((height, width, 3), dtype=np.uint8)
            for y in range(height):
                for x in range(width):
                    rgb_image[y, x] = QColor(color_table[image[y, x]]).getRgb()[:3]
            return rgb_image
        
        else:
            converted_image = qimage.convertToFormat(QImage.Format_RGB32)
            buffer = converted_image.constBits().asarray(height * width * 4)
            image = np.frombuffer(buffer, dtype=np.uint8).reshape((height, width, 4))
            return image[:, :, :3]

    def normalize_16bit_to_8bit(self, array):
        return ((array - array.min()) / (array.max() - array.min()) * 255).astype(np.uint8)

    def apply_sam_prediction(self, image, bbox):
        try:
            image_np = self.qimage_to_numpy(image)
            self.sam_predictor.set_image(image_np)
            results = self.sam_predictor.predict(
                point_coords=None,
                point_labels=None,
                box=bbox,
                multimask_output=False,
                )  # Need to be able to pass in the numpy image and prompt
            mask = results[0].masks.data[0].cpu().numpy()

            if mask is not None:
                print(f"Mask shape: {mask.shape}, Mask sum: {mask.sum()}")
                contours = self.mask_to_polygon(mask)
                print(f"Contours generated: {len(contours)} contour(s)")

                if not contours:
                    print("No valid contours found")
                    return None

                prediction = {
                    "segmentation": contours[0],
                    "score": float(results[0].boxes.conf[0])
                }
                return prediction
            else:
                print("Failed to generate mask")
                return None
        except Exception as e:
            print(f"Error in applying SAM prediction: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

    def mask_to_polygon(self, mask):
        import cv2
        contours, _ = cv2.findContours((mask > 0).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        polygons = []
        for contour in contours:
            if cv2.contourArea(contour) > 200:
                polygon = contour.flatten().tolist()
                if len(polygon) >= 6:
                    polygons.append(polygon)
        print(f"Generated {len(polygons)} valid polygons")
        return polygons