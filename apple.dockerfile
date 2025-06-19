FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Add user
# RUN adduser --quiet --disabled-password qtuser && usermod -a -G audio qtuser

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
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
  python3-pip && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*
# This fix: libGL error: No matching fbConfigs or visuals found
ENV LIBGL_ALWAYS_INDIRECT=1

# Install Python 3, PyQt5
RUN apt-get update && apt-get install -y \
    libx11-xcb1 \
    libxcb1 \
    libx11-dev \
    libxcb-xinerama0 \
    libxcb-xinerama0-dev \
    libxcb-randr0 \
    libxcb-randr0-dev \
    libxcb-shape0 \
    libxcb-shape0-dev \
    libxcb-xfixes0 \
    libxcb-xfixes0-dev \
    libxcb-sync1 \
    libxcb-sync-dev \
    libxcb-xtest0 \
    libxcb-xtest0-dev \
    libxcb-xkb1 \
    libxcb-xkb-dev \
    libxkbcommon-x11-0 \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-render-util0 \
    libdbus-1-3 \
    python3-pip \
    python3-venv \
    git \
    libsm6 

RUN python3 -m venv /opt/sam2_env && \
    /opt/sam2_env/bin/pip3 install torch==2.5.0 torchvision torchaudio && \
    /opt/sam2_env/bin/pip3 install virtualenv-clone    

RUN git clone https://github.com/KopiousKarp/digitalsreeni-image-annotator.git /opt/digitalsreeni-image-annotator

RUN cd /opt/digitalsreeni-image-annotator/ && /opt/sam2_env/bin/pip3 install -e .

RUN /opt/sam2_env/bin/pip3 uninstall -y opencv-python
RUN /opt/sam2_env/bin/pip3 install opencv-python-headless hydra-core>=1.3.2 iopath>=0.1.10 pillow>=9.4.0
RUN apt-get install -y \
    fontconfig-config \
    fonts-dejavu-core \
    libfontconfig1 \
    libfreetype6 \
    libpng16-16 \
    ucf

RUN git clone https://github.com/facebookresearch/segment-anything-2.git /opt/sam2 && \
  cd /opt/sam2 && /opt/sam2_env/bin/pip install --no-deps -e ".[demo]" && \
  cd /opt/sam2/checkpoints && ./download_ckpts.sh


RUN /opt/sam2_env/bin/pip3 install \
    matplotlib \
    pycocotools \
    scikit-learn \
    jupyter \
    segmentation-models-pytorch \ 
    pandas \
    ftfy \
    regex \
    git+https://github.com/openai/CLIP.git