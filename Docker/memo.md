### When launching from windows powershell
When launching from windows powershell
```sh
docker build . -t test --build-arg http_proxy=http://proxy:port  --build-arg https_proxy=http://proxy:port
```


port

```sh
wsl bash -c 'docker run -it --rm \
  -e DISPLAY=$DISPLAY \
  -e XDG_RUNTIME_DIR=$XDG_RUNTIME_DIR \
  -e PULSE_SERVER=$PULSE_SERVER \
  -e QT_QPA_PLATFORM=xcb \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  --gpus all \
  --shm-size=4080m \
  -p 6081:10000 \
  test'

```



### Test images

```sh
 docker build . -f ./DockerfileTest -t test_vnc --build-arg http_proxy=http://proxy:port  --build-arg https_proxy=http://proxy:port
```



```sh
wsl bash -c 'docker run --gpus all --name ROS2vncGPU -p 6080:80 --shm-size=1024m test_vnc'
```


### Todo
- https://github.com/Tiryoh/docker-ros2-desktop-vnc/tree/master/jazzy のエントリーポイントで入れ替える