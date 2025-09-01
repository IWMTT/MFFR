# ベースイメージ：ROS 2 Jazzy（Ubuntu 24.04）
FROM ros:jazzy


# プロキシ設定があればプロキシ設定
ARG HTTP_PROXY
ARG HTTPS_PROXY

ENV DEBIAN_FRONTEND=noninteractive

ENV HTTP_PROXY=${HTTP_PROXY}
ENV HTTPS_PROXY=${HTTPS_PROXY}

RUN if [ -n "$HTTP_PROXY" ]; then \
        echo "Acquire::http { Proxy \"$HTTP_PROXY\"; };" > /etc/apt/apt.conf.d/01proxy; \
    fi

# 開発に必要なツールをインストール
RUN apt-get update && apt-get install -y \
    git \
    python3-colcon-common-extensions\
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y \
    ros-jazzy-desktop-full \
    && rm -rf /var/lib/apt/lists/*
    

RUN apt update && apt install -y ros-jazzy-moveit \
    && rm -rf /var/lib/apt/lists/*

# ワークスペースを作成
ENV ROS_WS=/root/moveit2_ws
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
    colcon build --mixin release --symlink-install

# ROS環境を有効化
RUN echo "source /root/moveit2_ws/install/setup.bash" >> ~/.bashrc

# 起動スクリプトをコピーして実行権限を付与
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# ENTRYPOINTでsourceを通したbash環境へ
ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]