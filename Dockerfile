# exercise extreme caution when bumping this docker image to the newest ubuntu LTS version
FROM ubuntu:24.04

# for rationale behind each of these dependencies, consult the native section of DEVELOPING.md
RUN DEBIAN_FRONTEND=noninteractive \
  apt update \
  && DEBIAN_FRONTEND=noninteractive apt install -y curl git libffi-dev python-is-python3 python3-dev python3-wheel python3-setuptools python3-virtualenv libssl-dev autoconf openjdk-17-jdk cmake libtool libssl-dev libncurses5-dev libsqlite3-dev libreadline-dev libtk8.6 libgdm-dev libpcap-dev unzip zip wget apksigner build-essential libopus-dev libogg-dev portaudio19-dev patchelf pipx \
  && apt install --reinstall python3  \
  && rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/*

# need to run as root for a rootless docker runtime
# the repository folders owned by 1000 on the host are mounted to 0 on the container; this is intentional and unchangable

# add pipx 
ENV PATH=$PATH:/root/.local/bin

# install & inject wheel
RUN pipx install git+https://github.com/kivy/buildozer.git@abc2d7e66c8abe096a95ed58befe6617f7efdad0
RUN pipx inject buildozer wheel

# needed for some transitive deps, like rnsh
RUN pipx install poetry==2.1.1
