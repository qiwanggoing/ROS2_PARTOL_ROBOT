# ROS 2 Patrol Robot Simulation

A ROS 2 mobile robot simulation with autonomous navigation, waypoint patrols, speech announcements, and image capture at patrol stops.

<p align="center">
  <img src="docs/images/gazebo_simulation.jpg" width="48%" alt="Robot simulation in Gazebo">
  <img src="docs/images/navigation_rviz.jpg" width="48%" alt="Navigation in RViz">
</p>

## Features

### Mapping and Autonomous Navigation

| Feature | What it does |
| --- | --- |
| Map building | Drive through the room and build an environment map using laser scans. |
| Map saving and loading | Save maps for later use and switch between maps for navigation. |
| Initial localization | Set the robot's starting position and heading on the map. |
| Pose lookup | Read the robot's current position and orientation in the map. |
| Goal navigation | Select a destination in RViz or send a goal from a program, including the desired arrival heading. |
| Path planning and obstacle avoidance | Plan routes through the map and adjust motion using laser observations. |
| Navigation recovery | Configure recovery actions such as spinning, backing up, and waiting when navigation is blocked. |

### Patrols and Image Capture

| Feature | What it does |
| --- | --- |
| Waypoint navigation | Visit an ordered sequence of waypoints in a single run. |
| Repeated patrols | Repeat a configured patrol route until the task is stopped. |
| Custom patrol routes | Set the initial pose and each waypoint's position and arrival heading. |
| Task progress | Display remaining distance, the current waypoint index, and task results. |
| Speech announcements | Announce initialization, departure, arrival, and image capture; the speech service can also be called independently. |
| Image capture at stops | Save camera images at patrol stops, name them using position coordinates, and choose an output directory. |

### Observation and Manual Control

| Feature | What it does |
| --- | --- |
| Keyboard control | Drive forward, reverse, turn, and stop for exploration and mapping. |
| Camera viewing | View color images, depth images, and point clouds. |
| Sensor and state inspection | Read laser scans, IMU data, odometry, and wheel joint states. |
| Simulation visualization | Observe motion in Gazebo and inspect maps, scans, paths, and obstacle regions in RViz. |

### Running and Validation

| Feature | What it does |
| --- | --- |
| Combined or separate launch | Start simulation, navigation, and RViz together, or launch simulation and navigation separately. |
| Headless operation | Run the navigation simulation without graphical windows. |
| Automated navigation check | Check sensor and navigation readiness, send a goal, and save arrival results, position error, and motion evidence. |

See the [usage guide](docs/USAGE.md) for instructions and optional dependencies. The combined patrol, speech, and image capture workflow still requires integration testing.

## Demo Video

[![Robot navigation demo](docs/images/navigation_preview.gif)](Navigation.mp4)

[Watch the full video](Navigation.mp4)

## Getting Started

Prepare Conda and the build tools as described in the [installation guide](docs/USAGE.md). Then download the project and create its environment:

```bash
git clone https://github.com/qiwanggoing/ROS2_PARTOL_ROBOT.git
cd ROS2_PARTOL_ROBOT
conda env create --file environment.navigation.yml
conda activate ros2_patrol
```

Set `conda_root` and `patrol_env` at the top of `scripts/navigation.sh` to your installation paths, following the [installation guide](docs/USAGE.md). Then build and launch:

```bash
bash scripts/navigation.sh build
bash scripts/navigation.sh demo
```

In RViz, use **2D Pose Estimate** to set the initial pose, then **Nav2 Goal** to select a destination.

See the [usage guide](docs/USAGE.md) for the full setup and operating instructions.

This project builds on the educational materials from [fishros / FishBot](https://github.com/fishros).
