
FROM ubuntu:noble-20250404

# Automatic platform ARGs in the global scope
# https://docs.docker.com/reference/dockerfile/#automatic-platform-args-in-the-global-scope
ARG TARGETPLATFORM
ARG TARGETARCH

# The QEMU_CPU option is used to speed up arm64 image builds,
# amd64 is unaffected as it does not use QEMU.
# This environment variable is only declared at build time.
ARG QEMU_CPU

SHELL ["/bin/bash", "-c"]

# Upgrade OS
RUN apt-get update -q && \
    DEBIAN_FRONTEND=noninteractive apt-get upgrade -y && \
    apt-get autoclean && \
    apt-get autoremove && \
    rm -rf /var/lib/apt/lists/*

# Install minimal Ubuntu Desktop (GNOME) + gnome-terminal
RUN apt-get update -q && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
        ubuntu-desktop-minimal \
        gnome-terminal && \
    apt-get autoclean && \
    apt-get autoremove && \
    rm -rf /var/lib/apt/lists/*



# Add Package
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
        tigervnc-standalone-server tigervnc-common \
        supervisor wget curl gosu git sudo python3-full python3-pip tini \
        build-essential vim sudo lsb-release locales \
        bash-completion tzdata terminator && \
    apt-get autoclean && \
    apt-get autoremove && \
    rm -rf /var/lib/apt/lists/*

# noVNC and Websockify
RUN git clone https://github.com/AtsushiSaito/noVNC.git -b add_clipboard_support /usr/lib/novnc
RUN pip install --no-cache-dir --break-system-packages git+https://github.com/novnc/websockify.git@v0.10.0
RUN ln -s /usr/lib/novnc/vnc.html /usr/lib/novnc/index.html

# Set remote resize function enabled by default
RUN sed -i "s/UI.initSetting('resize', 'off');/UI.initSetting('resize', 'remote');/g" /usr/lib/novnc/app/ui.js

# Disable auto update and crash report
RUN sed -i 's/Prompt=.*/Prompt=never/' /etc/update-manager/release-upgrades
RUN sed -i 's/enabled=1/enabled=0/g' /etc/default/apport


# Install ROS
ENV ROS_DISTRO jazzy
# desktop or ros-base
ARG INSTALL_PACKAGE=desktop

RUN apt-get update -q && \
    apt-get install -y curl gnupg2 lsb-release && \
    curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/ros2.list > /dev/null && \
    apt-get update -q && \
    apt-get install -y ros-${ROS_DISTRO}-${INSTALL_PACKAGE} \
    python3-argcomplete \
    python3-colcon-common-extensions \
    python3-rosdep python3-vcstool && \
    rosdep init && \
    rm -rf /var/lib/apt/lists/*


RUN rosdep update

RUN apt update && apt install -y ros-jazzy-moveit \
    && rm -rf /var/lib/apt/lists/*


# Install simulation packages
RUN apt-get update -q && \
    apt-get install -y \
    ros-${ROS_DISTRO}-ros-gz && \
    rm -rf /var/lib/apt/lists/*

# Enable apt-get completion after running `apt-get update` in the container
RUN rm /etc/apt/apt.conf.d/docker-clean

# プロキシ設定があればプロキシ設定
ARG HTTP_PROXY
ARG HTTPS_PROXY


ENV HTTP_PROXY=${HTTP_PROXY}
ENV HTTPS_PROXY=${HTTPS_PROXY}

RUN if [ -n "$HTTP_PROXY" ]; then \
        echo "Acquire::http { Proxy \"$HTTP_PROXY\"; };" > /etc/apt/apt.conf.d/01proxy; \
    fi

# Create ubuntu user at build time
RUN id -u ubuntu &>/dev/null || useradd -m -s /bin/bash ubuntu && \
    echo "ubuntu:ubuntu" | chpasswd && \
    adduser ubuntu sudo && \
    echo "ubuntu ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers


ENV ROS_WS=/home/ubuntu/moveit2_ws
WORKDIR ${ROS_WS}

# チュートリアル + moveit2 関連のソースを取得（mainブランチ）
RUN mkdir -p src && cd src && \
    git clone -b main https://github.com/ros-planning/moveit2_tutorials.git && \
    git clone -b ROS2v0.7.0 https://github.com/Unity-Technologies/ROS-TCP-Endpoint && \
    vcs import < moveit2_tutorials/moveit2_tutorials.repos

# 依存解決
RUN apt-get update && rosdep update && \
    rosdep install -r --from-paths src --ignore-src --rosdistro jazzy -y \
    && rm -rf /var/lib/apt/lists/*

# ビルド
RUN . /opt/ros/jazzy/setup.sh && \
    colcon build --cmake-args -DCMAKE_BUILD_TYPE=Release --symlink-install --packages-skip moveit_ros_tests



COPY ./entrypoint.sh /
RUN chmod +x /entrypoint.sh
ENTRYPOINT [ "/bin/bash", "-c", "/entrypoint.sh" ]

ENV USER ubuntu
ENV PASSWD ubuntu
