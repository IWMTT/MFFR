FROM osrf/ros:humble-desktop-full-jammy


# プロキシ設定があればプロキシ設定
ARG HTTP_PROXY
ARG HTTPS_PROXY

ENV DEBIAN_FRONTEND=noninteractive

ENV HTTP_PROXY=${HTTP_PROXY}
ENV HTTPS_PROXY=${HTTPS_PROXY}

RUN if [ -n "$HTTP_PROXY" ]; then \
        echo "Acquire::http { Proxy \"$HTTP_PROXY\"; };" > /etc/apt/apt.conf.d/01proxy; \
    fi

RUN apt update && apt install -y ros-humble-moveit \
    && rm -rf /var/lib/apt/lists/*

ENV USER_DIR=/home/ubuntu
ENV ROS_WS=/home/ubuntu/moveit2_ws
WORKDIR ${ROS_WS}


# チュートリアル + moveit2 関連のソースを取得（mainブランチ）
RUN mkdir -p src && cd src && \
    # git clone -b main https://github.com/ros-planning/moveit2_tutorials.git && \
    git clone -b ROS2v0.7.0 https://github.com/Unity-Technologies/ROS-TCP-Endpoint && \
    git clone https://github.com/Kinovarobotics/ros2_kortex.git && \
    # vcs import < moveit2_tutorials/moveit2_tutorials.repos && \
    rm -rf /var/lib/apt/lists/*


    
# 依存解決
RUN apt-get update && rosdep update && \
    rosdep install -r --from-paths src --ignore-src --rosdistro humble -y \
    && rm -rf /var/lib/apt/lists/*

# ビルド
RUN . /opt/ros/humble/setup.sh && \
    colcon build --mixin release --symlink-install

# # ROS環境を有効化
RUN echo "source /opt/ros/humble/setup.bash" >> ${USER_DIR}/.bashrc
RUN echo "source ${ROS_WS}/install/setup.bash" >> ${USER_DIR}/.bashrc

# GUI 用
RUN apt-get update && apt-get install -y \
    x11-apps \
    mesa-utils \
    libgl1 \
    libglx-mesa0 \
    libxext6 \
    libx11-6 \
    libxrender1 \
    libxft2 \
    && rm -rf /var/lib/apt/lists/*


# 作業ディレクトリをユーザーディレクトリに変更
WORKDIR ${USER_DIR}

# ubuntuユーザーをビルド時に作ってsudoersに追加
RUN id -u ubuntu 2>/dev/null || \
    (useradd -m -s /bin/bash -G sudo ubuntu && \
     echo 'ubuntu ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/ubuntu && \
     chmod 0440 /etc/sudoers.d/ubuntu)

# ${ROS_WS}以下すべてのディレクトリとファイル権限をubuntuユーザーに変更
RUN chown -R ubuntu:ubuntu ${ROS_WS}
RUN chown -R ubuntu:ubuntu ${USER_DIR}


# 起動スクリプトをコピーして実行権限を付与
COPY ./entrypoint.sh /
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]

# ENV USER=ubuntu
# ENV PASSWORD=ubuntu
# USER ubuntu
