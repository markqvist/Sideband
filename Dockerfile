FROM ubuntu:24.04

# for rationale behind each of these dependencies, consult the native section of DEVELOPING.md
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    make \
    adb \
    python3 \
    python3-dev \
    python-is-python3  \
    pipx \
    patchelf \
    patch \
    perl \
    portaudio19-dev \
    libopus-dev \
    libogg-dev  \
    git  \
    zip  \
    unzip  \
    openjdk-17-jdk  \
    python3-pip  \
    autoconf \
    libtool \
    libtool-bin \
    automake \
    gettext \
    pkg-config  \
    zlib1g-dev  \
    libncurses-dev  \
    libtinfo6  \
    cmake  \
    libffi-dev  \
    libffi-c-perl \
    libssl-dev \
    && \
    rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/*

# need to run as root for a rootless docker runtime
# the repository folders owned by 1000 on the host are mounted to 0 on the container; this is intentional and unchangable

# add pipx 
ENV PATH=$PATH:/root/.local/bin

# install & inject wheel
RUN pipx install git+https://github.com/kivy/buildozer.git@abc2d7e66c8abe096a95ed58befe6617f7efdad0
RUN pipx inject buildozer wheel
