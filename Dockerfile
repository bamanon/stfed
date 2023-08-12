FROM ubuntu:20.04

ENV TZ=Etc/UTC

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone \
    && DEBIAN_FRONTEND=noninteractive apt-get update \
    && apt-get install -y \
        make \
        gcc \
        python3 \
        python3-venv \
        python3-dev \
        libasound2-dev \
        portaudio19-dev \
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
        libfontconfig \
        libgssapi-krb5-2

COPY . /app

WORKDIR /app

RUN make

CMD ["make", "run"]
