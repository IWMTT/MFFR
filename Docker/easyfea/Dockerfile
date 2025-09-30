FROM quay.io/jupyter/minimal-notebook:latest


# プロキシ設定があればプロキシ設定
ARG HTTP_PROXY
ARG HTTPS_PROXY

ENV DEBIAN_FRONTEND=noninteractive

ENV HTTP_PROXY=${HTTP_PROXY}
ENV HTTPS_PROXY=${HTTPS_PROXY}

RUN if [ -n "$HTTP_PROXY" ]; then \
        echo "Acquire::http { Proxy \"$HTTP_PROXY\"; };" > /etc/apt/apt.conf.d/01proxy; \
    fi

USER root
RUN apt update && apt install -y libglu1 libxcursor-dev libxft2 libxinerama1 libfltk1.3-dev libfreetype6-dev libgl1-mesa-dev libocct-foundation-dev libocct-data-exchange-dev \
    && rm -rf /var/lib/apt/lists/*

RUN apt update && apt install -y xvfb libgl1-mesa-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install EasyFEA trame trame-vtk trame-vuetify trame-components ipywidgets

ENV USER_DIR=/home/jovyan
ENV WS=/home/jovyan/work

WORKDIR ${WS}


RUN curl -OL https://easyfea.readthedocs.io/en/latest/_downloads/aadfa90b122ddd054aa9b882abdea498/Elas7.zip
RUN unzip Elas7.zip && rm Elas7.zip

# PyVistaのJupyterバックエンドを設定
RUN mkdir -p ${USER_DIR}/.ipython/profile_default/startup
RUN mkdir -p ${USER_DIR}/.ipython/profile_default/startup && \
    printf '%s\n%s\n%s\n' \
      '# ~/.ipython/profile_default/startup/00-pyvista.py' \
      'import pyvista as pv' \
      "pv.set_jupyter_backend('html')" \
    > ${USER_DIR}/.ipython/profile_default/startup/00-pyvista.py


RUN chown -R jovyan:users ${WS}
RUN chown -R jovyan:users ${USER_DIR}

# # 起動スクリプトをコピーして実行権限を付与
# COPY ./entrypoint.sh /
# RUN chmod +x /entrypoint.sh
# ENTRYPOINT ["/entrypoint.sh"]
# CMD ["bash"]

# ENV USER=ubuntu
# ENV PASSWORD=ubuntu
# USER ubuntu
