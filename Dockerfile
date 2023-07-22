FROM ubuntu:22.04

RUN DEBIAN_FRONTEND=noninteractive \
    apt-get update \
    && apt-get install -y \
        make \
        python3 \
        python3-venv \
        python3-pip \
        python3-pillow \
        python3-pyaudio \
        libasound2-dev \
        libgl1-mesa-glx \
        libxkbcommon-x11-0 \
        libegl1 \
        libdbus-1-dev \
        libxcb1-dev \
        libxcb-cursor0 \
        libxcb-icccm4 \
        libxcb-keysyms1 \
        libxcb-randr0 \
        libxcb-shape0 \
    && pip3 install \
        pyside6 \
        simpleaudio


COPY . /app

WORKDIR /app

RUN make

CMD ["python3", "-m", "stfed"]
