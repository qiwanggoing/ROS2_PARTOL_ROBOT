# ROS 2 Patrol Robot Simulation

A simulated mobile-robot project for visiting a sequence of patrol points, announcing each arrival, and saving a camera image at each stop.

<p align="center">
  <img src="docs/images/gazebo_simulation.jpg" width="48%" alt="Patrol robot in Gazebo">
  <img src="docs/images/navigation_rviz.jpg" width="48%" alt="Navigation and waypoint progress in RViz">
</p>

## What the system does

- Builds a map with SLAM Toolbox and navigates with Nav2.
- Follows a list of waypoints in simulation.
- Announces each reached waypoint through text-to-speech.
- Captures and saves an image from the robot camera at each stop.
- Splits the application into ROS 2 packages for robot description, navigation, interfaces, and patrol behavior.

## Main tools

ROS 2 Humble, Ubuntu 22.04, Gazebo, Nav2, SLAM Toolbox, Python, and `ros2-control`.

## Run the simulation

Install the ROS 2 dependencies for Gazebo, Nav2, SLAM Toolbox, and the robot description packages. Then build the workspace:

```bash
colcon build
source install/setup.bash
```

Launch the simulator and navigation:

```bash
ros2 launch fishbot_description gazebo_sim.launch.py
ros2 launch fishbot_navigation2 navigation2.launch.py
```

Start the patrol behavior:

```bash
ros2 launch autopartol_robot autopartol.launch.py
```

Package names and launch files follow the source tree in this repository. The demonstrations are from simulation; this project was not evaluated on a physical patrol robot.

## Acknowledgement

This educational project builds on the FishBot materials by [fishros](https://github.com/fishros).

