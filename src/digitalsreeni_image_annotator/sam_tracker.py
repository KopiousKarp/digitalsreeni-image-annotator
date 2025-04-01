import os
from sam2.build_sam import build_sam2_video_predictor 
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, 
                             QLabel, QSpinBox, QRadioButton, QButtonGroup, QMessageBox)
from PyQt5.QtCore import Qt
import torch

class SAMTrackerTool(QDialog):
    def __init__(self, parent=None, annotations=None, image_paths=None):
        super().__init__(parent)
        self.setWindowTitle("Sam2 Tracker")
        self.setGeometry(100, 100, 500, 300)
        self.setWindowFlags(self.windowFlags() | Qt.Window)
        self.initUI()
        self.sam_models = {
            "SAM 2 tiny": "/opt/sam2/checkpoints/sam2.1_hiera_tiny.pt",
            "SAM 2 small": "/opt/sam2/checkpoints/sam2.1_hiera_small.pt",
            "SAM 2 base": "/opt/sam2/checkpoints/sam2.1_hiera_base_plus.pt",
            "SAM 2 large": "/opt/sam2/checkpoints/sam2.1_hiera_large.pt"
        }
        self.model_configs = {
            "SAM 2 tiny": "configs/sam2.1/sam2.1_hiera_t.yaml",
            "SAM 2 small": "configs/sam2.1/sam2.1_hiera_s.yaml",
            "SAM 2 base": "configs/sam2.1/sam2.1_hiera_b+.yaml",
            "SAM 2 large": "configs/sam2.1/sam2.1_hiera_l.yaml"
        }
        self.current_sam_model = "SAM 2 tiny"
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
    def initUI(self):
        layout = QVBoxLayout()
        
        # Header
        header_label = QLabel("SAM2 Video Segmentation Tool")
        header_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(header_label)
        
        # Description
        description = QLabel("This tool uses SAM2 to perform video object segmentation.")
        layout.addWidget(description)
        
        # Spacer
        layout.addSpacing(20)
        
        # Video selection button (Video must be in a folder of images)
        self.select_video_button = QPushButton("Select Image Folder")
        self.select_video_button.clicked.connect(self.select_image_folder)
        layout.addWidget(self.select_video_button)
        
        # File path display
        self.file_path_label = QLabel("No video selected")
        layout.addWidget(self.file_path_label)
        
        # Spacer
        layout.addSpacing(20)
        
        # Process button
        self.process_button = QPushButton("Process Video with SAM2")
        self.process_button.clicked.connect(self.process_video)
        self.process_button.setEnabled(False)  # Disabled until video is selected
        layout.addWidget(self.process_button)
        
        self.setLayout(layout)

    def select_image_folder(self):
        """Open dialog to select a folder containing images"""
        self.image_folder = QFileDialog.getExistingDirectory(
            self, 
            "Select Folder Containing Images", 
            ""
        )
        
        if self.image_folder:
            self.file_path_label.setText(os.path.basename(self.image_folder))
            self.process_button.setEnabled(True)
    
    #probably not needed
    # def get_conditional_frames(self, frame):
        

    def process_video(self):
        """Process the selected video with SAM2"""
        if not self.image_folder:
            QMessageBox.warning(self, "Error", "Please select a video file first.")
            return
            
        # This is where we would add SAM2 processing code
        # Get list of image files in the folder
        image_files = [f for f in os.listdir(self.image_folder) if f.endswith('.jpg')]
        
        # Sort files by datetime in filename
        image_files.sort(key=lambda x: os.path.splitext(x)[0].split('_')[1])
        
        # # Print sorted files (for debugging purposes)
        # for image_file in image_files:
        #     print(image_file)
        





        predictor = build_sam2_video_predictor(self.model_configs[self.current_sam_model], self.sam_models[self.current_sam_model], device=self.device)
        inference_state = predictor.init_state(video_path=self.image_folder)
        #Go through the .iap to get the conditioanl frames and the masks
        #or maybe go through COCO format instead 
        #Go through how the annotations get passed around normally 
        #loop through the annotations and add the masks to the annotation frame
        
        
        
        
        
        QMessageBox.information(
            self, 
            "Processing Started", 
            f"Starting SAM2 processing on video: {os.path.basename(self.image_folder)}"
        )
        # Call SAM2 processing logic here
        
    def show_centered(self, parent):
        parent_geo = parent.geometry()
        self.move(parent_geo.center() - self.rect().center())
        self.show()