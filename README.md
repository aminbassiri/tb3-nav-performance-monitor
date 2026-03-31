# 🚀 TurtleBot3 Navigation Performance Monitor

A ROS2 Humble project for monitoring and evaluating TurtleBot3 navigation performance in Gazebo using Nav2.

---

# 📌 Project Overview

This project builds a **complete evaluation pipeline** for robot navigation:

* Run navigation in simulation (Gazebo + Nav2)
* Send goals to robot
* Monitor performance in real-time
* Save results into CSV
* Compare performance across environments

---

# 🧠 What This System Measures

For each goal, the system computes:

* Execution time (how long robot takes)
* Final error (distance to goal)
* Path efficiency (actual vs planned path)
* Recovery behavior (if robot gets stuck)
* Battery proxy (based on distance)

---

# 🏗️ Project Structure

```
tb3-nav-performance-monitor/
├── workspace/src/tbot3_nav_monitor/
│   ├── goal_bridge.py
│   ├── metrics_collector.py
│   └── csv_logger.py
├── tools/
│   ├── compare_results.py
│   └── dashboard.py
├── results/
├── media/
├── worlds/My_maze.world
├── docker-compose.yml
└── README.md
```

---

# 💻 Development Environment

* Windows 11
* WSL2 (Ubuntu)
* Docker Desktop
* ROS2 Humble
* Gazebo
* Nav2
* TurtleBot3 Burger

---
---
## 🐳 Docker Image

A ready-to-run Docker image is available on Docker Hub:

https://hub.docker.com/r/aminbassiri/tb3-nav-monitor

## Pull the image with:

```bash
https://hub.docker.com/r/aminbassiri/tb3-nav-monitor

# ⚙️ Setup (Step-by-Step)

## 1. Start Docker

Make sure Docker Desktop is running.

---

## 2. Open Ubuntu (WSL)

---

## 3. Go to project folder

```bash
cd ~/ai4i_assignment
```

---

## 4. Start container

```bash
docker compose up -d
```

---

## 5. Enter container

```bash
docker exec -it tbot3_monitor bash
```

---

## 6. Source ROS

```bash
source /opt/ros/humble/setup.bash
source /root/ws/install/setup.bash
```

---

## 7. Build (if needed)

```bash
cd /root/ws
rm -rf build install log
colcon build
source install/setup.bash
```

---

# ▶️ Running the System (Step-by-Step)

⚠️ **Important: Follow steps exactly in order**

---

# 🧹 STEP 0 — Clean Start

```bash
docker compose down
cd ~/ai4i_assignment
docker compose up -d
```

---

# 🌍 STEP 1 — Start Gazebo

```bash
docker exec -it tbot3_monitor bash
source /opt/ros/humble/setup.bash
source /root/ws/install/setup.bash

ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
or
ros2 launch turtlebot3_gazebo turtlebot3_house.launch.py
or
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py \
world:=/root/ws/worlds/My_maze.world
```

👉 Wait until Gazebo fully loads

---

# 🧭 STEP 2 — Start Navigation (Nav2)

Open a **new terminal**:

```bash
docker exec -it tbot3_monitor bash
source /opt/ros/humble/setup.bash
source /root/ws/install/setup.bash

ros2 launch turtlebot3_navigation2 navigation2.launch.py use_sim_time:=True use_rviz:=True
```

👉 Wait ~5–10 seconds

---

# 📍 STEP 3 — Set Initial Pose

```bash
docker exec -it tbot3_monitor bash
source /opt/ros/humble/setup.bash
source /root/ws/install/setup.bash

ros2 topic pub --once /initialpose geometry_msgs/msg/PoseWithCovarianceStamped "{header: {frame_id: 'map'}, pose: {pose: {position: {x: -2.0, y: -0.5, z: 0.0}, orientation: {w: 1.0}}, covariance: [0.25,0,0,0,0,0,0,0.25,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.068]}}"
```

👉 Wait 5 seconds

---

# 🤖 STEP 4 — Start Your Nodes

### goal_bridge

```bash
docker exec -it tbot3_monitor bash
source /opt/ros/humble/setup.bash
source /root/ws/install/setup.bash
ros2 run tbot3_nav_monitor goal_bridge
```

---

### metrics_collector

```bash
docker exec -it tbot3_monitor bash
source /opt/ros/humble/setup.bash
source /root/ws/install/setup.bash
ros2 run tbot3_nav_monitor metrics_collector
```

👉 Wait 10 seconds (for odom stabilization)

---

# 🧹 STEP 5 — Clear Old Results

```bash
docker exec -it tbot3_monitor bash
source /opt/ros/humble/setup.bash
source /root/ws/install/setup.bash
rm -f /root/ws/results/goal_metrics.csv
```

---

# 🎯 STEP 6 — Send Goal

```bash
docker exec -it tbot3_monitor bash
source /opt/ros/humble/setup.bash
source /root/ws/install/setup.bash
ros2 topic pub --once /goal_pose geometry_msgs/msg/PoseStamped "{header: {frame_id: 'map'}, pose: {position: {x: -1.5, y: 0.7, z: 0.0}, orientation: {w: 1.0}}}"
```

---

# 👀 What You Should See

### In Gazebo:

✔ Robot moves toward goal

### In goal_bridge:

```
Received goal
Goal accepted
Navigation finished
```

### In metrics_collector:

```
New goal received
Goal finished success=True
```

---

# ⏱️ STEP 7 — Wait

Wait until:

```
Goal finished success=True
```

---

# 🎯 STEP 8 — Send Another Goal

```bash
ros2 topic pub --once /goal_pose geometry_msgs/msg/PoseStamped "{header: {frame_id: 'map'}, pose: {position: {x: 1.5, y: 0.7, z: 0.0}, orientation: {w: 1.0}}}"
```

---

# 💾 STEP 9 — Check Results

```bash
cat /root/ws/results/goal_metrics.csv
```

---

# 🌍 Multi-Environment Testing

Before each run:

```bash
rm -f /root/ws/results/goal_metrics.csv
```

---

## Save Results

```bash
docker cp tbot3_monitor:/root/ws/results/goal_metrics.csv ~/ai4i_assignment/results/goal_metrics_basic.csv
```

---

# 📊 Dashboard

```bash
cd ~/ai4i_assignment/tools
python3 dashboard.py
```

Open:

```
http://localhost:5000
```
Here is a clean README section you can use:

---

## Dashboard Setup

If the dashboard does not open, follow these steps:

### 1. Install Required Dependencies

```bash
pip install flask pandas matplotlib
```

### 2. Run the Dashboard

```bash
python3 dashboard.py
```

### 3. Open in Browser

Go to:

```
http://127.0.0.1:5000
```

---

If the page still does not load, make sure the script is running without errors and the port is not blocked.


---

# 📈 Compare Results

```bash
python3 compare_results.py
```

---

# ⚠️ Important Notes

* Do NOT send same goal twice
* Do NOT stop nodes during execution
* Always wait for goal to finish
* Always clear CSV before new test

---
# 🎥 Demo

[https://youtu.be/s3MAgZvcXAQ](https://youtu.be/s3MAgZvcXAQ)

---
Author: Amin Basiri


