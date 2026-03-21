# 🚀 TurtleBot3 Navigation Performance Monitor

A ROS 2 Humble project for monitoring and evaluating TurtleBot3 navigation performance in Gazebo using Nav2.

This system collects real-time navigation metrics, logs them into CSV files, compares results across multiple environments, and visualizes performance through a web dashboard.

---

# 📌 Project Overview

This project provides a complete evaluation pipeline for robot navigation:

- Real-time performance monitoring
- Metric computation and logging
- Adaptive behavior analysis
- Multi-environment benchmarking
- Web-based visualization

---

# 🧠 Features

## Navigation Performance Metrics
The system measures:

- Path execution time (goal start → completion)
- Navigation accuracy (final distance to goal)
- Obstacle avoidance efficiency (actual path vs planned path)
- Recovery behavior frequency (stuck detection)
- Battery consumption proxy (based on path length)

---

## Adaptive Behavior System
Dynamic adjustments based on performance:

- Reduce velocity when robot gets stuck frequently
- Increase goal tolerance when accuracy is poor
- Switch to conservative mode when efficiency is low
- Adjust navigation behavior based on environment complexity

---

## Data Logging & Visualization

- CSV logging with timestamps
- Console monitoring and warnings
- Performance comparison across environments
- Flask-based dashboard (runs outside Docker)

---

## Multi-Environment Testing

Tested in:

- Basic world
- TurtleBot3 house world
- Narrow / cluttered environment

---

# 🏗️ Project Structure

tb3-nav-performance-monitor/
├── docker/
├── workspace/
│ └── src/
│ └── tbot3_nav_monitor/
│ ├── goal_bridge.py
│ ├── metrics_collector.py
│ └── csv_logger.py
├── tools/
│ ├── compare_results.py
│ └── dashboard.py
├── results/
│ ├── goal_metrics_basic.csv
│ ├── goal_metrics_house.csv
│ └── goal_metrics_maze.csv
├── media/
│ ├── dashboard.png
│ ├── gazebo_basic.png
│ ├── gazebo_house.png
│ └── gazebo_maze.png
├── docker-compose.yml
├── README.md
└── requirements.txt

---

# 💻 Development Environment

- Windows 11
- Docker Desktop
- WSL2 (Ubuntu)
- VS Code
- ROS 2 Humble
- Gazebo
- Nav2
- TurtleBot3 Burger

---

# ⚙️ Prerequisites

Install Flask:

pip3 install flask

---

# 🐳 Step-by-Step Setup

## Step 1 — Open Docker Desktop
Make sure Docker Desktop is running.

## Step 2 — Open Ubuntu (WSL2)

## Step 3 — Go to project folder

cd ~/ai4i_assignment

## Step 4 — Start container

docker compose up -d

## Step 5 — Enter container

docker exec -it tbot3_monitor bash

## Step 6 — Source ROS

source /opt/ros/humble/setup.bash  
source /root/ws/install/setup.bash

## Step 7 — Build (if needed)

cd /root/ws  
rm -rf build install log  
colcon build  
source install/setup.bash

---

# ▶️ Running the Full System

## Terminal 1 — Gazebo

Basic:
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py

House:
ros2 launch turtlebot3_gazebo turtlebot3_house.launch.py

---

## Terminal 2 — Navigation

ros2 launch turtlebot3_navigation2 navigation2.launch.py use_sim_time:=True use_rviz:=False

---

## Terminal 3 — Initial Pose

ros2 topic pub --once /initialpose geometry_msgs/msg/PoseWithCovarianceStamped "{header: {frame_id: 'map'}, pose: {pose: {position: {x: -2.0, y: -0.5, z: 0.0}, orientation: {w: 1.0}}}}"

Wait 5 seconds.

---

## Terminal 4 — goal_bridge

ros2 run tbot3_nav_monitor goal_bridge

---

## Terminal 5 — metrics_collector

ros2 run tbot3_nav_monitor metrics_collector

---

## Terminal 6 — Send Goal

ros2 topic pub --once /goal_pose geometry_msgs/msg/PoseStamped "{header: {frame_id: 'map'}, pose: {position: {x: 0.8, y: 0.0, z: 0.0}, orientation: {w: 1.0}}}"

---

# 🌍 Multi-Environment Testing

Before each environment:

rm -f /root/ws/results/goal_metrics.csv

---

## Save results

Basic:
docker cp tbot3_monitor:/root/ws/results/goal_metrics.csv ~/ai4i_assignment/results/goal_metrics_basic.csv

House:
docker cp tbot3_monitor:/root/ws/results/goal_metrics.csv ~/ai4i_assignment/results/goal_metrics_house.csv

Maze:
docker cp tbot3_monitor:/root/ws/results/goal_metrics.csv ~/ai4i_assignment/results/goal_metrics_maze.csv

---

# 📊 Dashboard

cd ~/ai4i_assignment/tools  
python3 dashboard.py

Open in browser:
http://localhost:5000

---

# 📈 Compare Results

cd ~/ai4i_assignment/tools  
python3 compare_results.py

---

# 📂 Output

results/

---

# 🎥 Demo Video

Video link here:

https://youtu.be/s3MAgZvcXAQ

---

# 🖼️ Screenshots

![Dashboard](media/dashboard.png)

---

# ⚠️ Troubleshooting

## GitHub push error
Use Personal Access Token instead of password.

## Dashboard not opening
Run:
python3 dashboard.py

## Package not found
cd /root/ws  
colcon build  
source install/setup.bash

---

# 👨‍💻 Author

Amin Basiri  
Robotics Engineer 
