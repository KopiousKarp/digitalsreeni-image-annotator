FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV LIBGL_ALWAYS_INDIRECT=1

# Core system tools
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      ca-certificates \
      curl \
      gnupg \
      sudo \
      libelf1 \
      libnuma-dev \
      build-essential \
      git \
      vim-nox \
      cmake-curses-gui \
      kmod \
      file \
      python3 \
      python3-pip \
      python3-venv \
      python3-pyqt5 \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# GUI libraries and fonts
RUN apt-get update \
 && apt-get install -y \
      libsm6 \
      libfontconfig1 \
      libfreetype6 \
      libpng16-16 \
      fontconfig-config \
      fonts-dejavu-core \
      ucf \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# Setup Python venv and core ML libraries
RUN python3 -m venv --system-site-packages /opt/sam2_env \
 && /opt/sam2_env/bin/pip install --upgrade pip \
 && /opt/sam2_env/bin/pip install \
      torch==2.5.0 \
      torchvision \
      torchaudio \
      virtualenv-clone


# ENV MAKEFLAGS="-j1"
# ENV MAX_JOBS=1 
# Install your image annotator
RUN git clone \
      https://github.com/KopiousKarp/digitalsreeni-image-annotator.git \
      /opt/digitalsreeni-image-annotator
RUN /opt/sam2_env/bin/pip install --no-deps -e /opt/digitalsreeni-image-annotator

# Replace OpenCV and install visualization libraries
RUN /opt/sam2_env/bin/pip uninstall -y opencv-python
RUN /opt/sam2_env/bin/pip install \
      opencv-python-headless \
      hydra-core>=1.3.2 \
      iopath>=0.1.10 \
      pillow>=9.4.0

# Install Segment Anything and download checkpoints
RUN git clone \
      https://github.com/facebookresearch/segment-anything-2.git \
      /opt/sam2 \
 && cd /opt/sam2 \
 && /opt/sam2_env/bin/pip install --no-deps -e ".[demo]" \
 && cd /opt/sam2/checkpoints \
 && ./download_ckpts.sh

# Final Python dependencies
RUN /opt/sam2_env/bin/pip install \
      matplotlib \
      pycocotools \
      scikit-learn \
      jupyter \
      segmentation-models-pytorch \
      pandas \
      ftfy \
      regex \
      git+https://github.com/openai/CLIP.git