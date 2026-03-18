FROM osrf/ros:humble-desktop

ENV DEBIAN_FRONTEND=noninteractive
ENV TURTLEBOT3_MODEL=burger

RUN apt-get update && apt-get install -y \
    python3-colcon-common-extensions \
    python3-pip \
    git \
    nano \
    vim \
    curl \
    wget \
    ros-humble-navigation2 \
    ros-humble-nav2-bringup \
    ros-humble-turtlebot3 \
    ros-humble-turtlebot3-gazebo \
    ros-humble-turtlebot3-msgs \
    ros-humble-gazebo-ros-pkgs \
    ros-humble-rviz2 \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pandas numpy matplotlib

WORKDIR /root/ws

COPY ./workspace/src /root/ws/src

RUN /bin/bash -c "source /opt/ros/humble/setup.bash && colcon build || true"

RUN echo 'source /opt/ros/humble/setup.bash' >> /root/.bashrc && \
    echo 'if [ -f /root/ws/install/setup.bash ]; then source /root/ws/install/setup.bash; fi' >> /root/.bashrc && \
    echo 'export TURTLEBOT3_MODEL=burger' >> /root/.bashrc

CMD ["/bin/bash"]