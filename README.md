# 🚀 TurtleBot3 Navigation Performance Monitor

This project implements a performance monitoring system for TurtleBot3 navigation using ROS2. It evaluates navigation behavior by collecting and analyzing key metrics such as path efficiency, goal completion time, and obstacle avoidance performance.

---

## 📌 Overview

The system is designed to:
- Monitor robot navigation in real-time
- Collect metrics from ROS2 topics
- Log results into CSV files
- Analyze navigation performance

---

## 🧠 Key Features

- Goal tracking
- Navigation time measurement
- Path efficiency calculation
- Obstacle avoidance evaluation
- CSV logging
- Performance comparison tools

---

## 🏗️ Project Structure

tb3-nav-performance-monitor/
├── docker/
├── workspace/
├── tools/
├── results/
├── docker-compose.yml
├── README.md

---

## ⚙️ Setup Instructions

### Start Docker container

docker compose up -d

### Enter container

docker exec -it tbot3_monitor bash

### Source ROS2

source /opt/ros/humble/setup.bash  
source /root/ws/install/setup.bash

---

## ▶️ Running the System

### Set initial pose

ros2 topic pub --once /initialpose geometry_msgs/msg/PoseWithCovarianceStamped "{header: {frame_id: 'map'}, pose: {pose: {position: {x: -2.0, y: -0.5, z: 0.0}, orientation: {w: 1.0}}}}"

### Send navigation goal

ros2 topic pub --once /goal_pose geometry_msgs/msg/PoseStamped "{header: {frame_id: 'map'}, pose: {position: {x: 0.8, y: 0.0, z: 0.0}, orientation: {w: 1.0}}}"

### Run metrics collector

ros2 run tbot3_nav_monitor metrics_collector

---

## 📊 Metrics

- Goal completion time  
- Path efficiency  
- Obstacle avoidance efficiency  
- Success rate  

---

## 📁 Output

Results are saved in:

results/

---

## 🧪 Implementation

- ROS2 (rclpy)
- Topics: /odom, /goal_pose, /plan
- Custom node: metrics_collector.py
- Data saved as CSV

---

## 👨‍💻 Author

Amin Basiri  
Robotics Engineer
