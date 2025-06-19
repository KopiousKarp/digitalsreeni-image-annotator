#!/bin/bash


#####################################################################################
# detect system gpu architecture before building
# Initialize GPU_TYPE variable
GPU_TYPE="UNKNOWN"

# Check for NVIDIA GPU
if command -v nvidia-smi &> /dev/null; then
    echo "NVIDIA GPU detected"
    GPU_TYPE="cuda"
# Check for AMD GPU
elif command -v lspci &> /dev/null && lspci | grep -i "amd" | grep -i "vga\|3d\|display" &> /dev/null; then
    echo "AMD GPU detected"
    GPU_TYPE="rocm"
# Check for Apple Silicon (M1, M2, etc.)
elif [ "$(uname)" == "Darwin" ] && sysctl -n machdep.cpu.brand_string 2>/dev/null | grep -q "Apple M"; then
    echo "Apple Silicon detected"
    GPU_TYPE="apple"
fi

echo "Detected GPU architecture: $GPU_TYPE"
export GPU_TYPE
if [ "$GPU_TYPE" == "UNKNOWN" ]; then
    echo "No supported GPU detected. Exiting."
    exit 1
fi
###########################################################################################
# Check if Docker image already exists
echo "Checking if Docker image with tag sreeni_$GPU_TYPE already exists..."
if docker images "sreeni_$GPU_TYPE" | grep -q "sreeni_$GPU_TYPE"; then
    echo "Docker image with tag sreeni_$GPU_TYPE already exists. Skipping build."
else
    echo "Docker image with tag sreeni_$GPU_TYPE does not exist. Building new image."
    # Build the Docker image with the appropriate tag
    echo "Building Docker image with tag: sreeni_$GPU_TYPE"
    if docker build -t "sreeni_$GPU_TYPE" -f "./env/$GPU_TYPE.dockerfile" ./env; then
        echo "Docker image built successfully with tag: sreeni_$GPU_TYPE"

    else
        echo "Failed to build Docker image. Exiting."
        exit 1
    fi
fi





##############################################################################################
echo "running environment"
xhost +
docker run -it \
      --net=host \
      --cap-add=SYS_PTRACE \
      --security-opt seccomp=unconfined \
      --device=/dev/kfd \
      --device=/dev/dri \
      --group-add video \
      --ipc=host \
      --shm-size 8G \
      -v ./:/work \
      -v /media:/media \
      -v $HOME/.Xauthority:/root/.Xauthority \
      -v /tmp/.X11-unix:/tmp/.X11-unix \
      -e DISPLAY=$DISPLAY \
      sreeni_$GPU_TYPE bash


echo "docker command executed successfully."