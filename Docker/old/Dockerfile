FROM ubuntu:22.04

# プロキシ設定があればプロキシ設定
ARG HTTP_PROXY
ARG HTTPS_PROXY

ENV DEBIAN_FRONTEND=noninteractive

ENV HTTP_PROXY=${HTTP_PROXY}
ENV HTTPS_PROXY=${HTTPS_PROXY}

RUN if [ -n "$HTTP_PROXY" ]; then \
      echo "Acquire::http { Proxy \"$HTTP_PROXY\"; };" > /etc/apt/apt.conf.d/01proxy; \
    fi

# 非対話的環境でのインストールを可能にする
ENV DEBIAN_FRONTEND=noninteractive

# 必要最低限のパッケージだけインストール
RUN apt-get update && apt-get install -y \
    x11-apps \
    && apt-get clean && rm -rf /var/lib/apt/lists/*