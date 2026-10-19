# Installation and Usage

This guide starts with a fresh download. Run the commands in a Linux x86_64 terminal. Graphical demonstrations require a desktop session.

## 1. Download and Environment Setup

Install Git, Conda (Miniconda or Miniforge), and C/C++ build tools. On Ubuntu, install the build tools with:

```bash
sudo apt update
sudo apt install git build-essential
```

After installing and initializing Conda, open a new terminal and download the project:

```bash
git clone https://github.com/qiwanggoing/ROS2_PARTOL_ROBOT.git
cd ROS2_PARTOL_ROBOT
```

Create an isolated environment using [environment.navigation.yml](../environment.navigation.yml):

```bash
conda env create --file environment.navigation.yml
conda activate ros2_patrol
```

The environment provides ROS 2 Humble, Gazebo Classic 11, Nav2, and RViz. A separate system ROS installation is unnecessary. See the [RoboStack documentation](https://robostack.github.io/GettingStarted.html) for ROS packages distributed through Conda. The `setuptools<80` constraint maintains compatibility with Humble's Python build tools.

If the default disk has insufficient space, choose a persistent directory with enough free space and write permission, for example:

```bash
conda env create --prefix "$HOME/conda-envs/ros2_patrol" --file environment.navigation.yml
conda activate "$HOME/conda-envs/ros2_patrol"
```

For a custom directory, replace subsequent `conda install --name ros2_patrol` commands with `conda install --prefix "/full/path/to/environment"`.

## 2. Configure Paths, Build, and Launch

Check the installation paths:

```bash
conda info --base
conda env list
```

Open [scripts/navigation.sh](../scripts/navigation.sh) and edit `conda_root` and `patrol_env` near the top. You can replace those two lines with:

```bash
conda_root="/path/to/your/conda/installation"
patrol_env="/path/to/your/ros2_patrol/environment"
```

Set `conda_root` to the output of `conda info --base`. Set `patrol_env` to the full path listed for `ros2_patrol` by `conda env list`. Save the file, then run these commands from the project root:

```bash
bash scripts/navigation.sh build
bash scripts/navigation.sh demo
```

The script activates the environment at the paths you supplied and loads the project. In each new terminal, enter the project directory before running commands. Update the two paths if you relocate or recreate the environment elsewhere.

After startup:

1. Wait for the robot to appear in Gazebo and the map to appear in RViz.
2. Click **2D Pose Estimate** in RViz and set the initial position to `(0, 0)`, facing `+x`.
3. Click **Nav2 Goal** and drag in free space to select a destination and heading.
4. Observe the robot and planned path. `Goal succeeded` indicates successful navigation.
5. Press `Ctrl+C` in the launch terminal to stop. Wait for its processes to exit before restarting.

If the robot has moved, initialize localization at its actual current pose. **2D Pose Estimate** changes the localization estimate; it does not move the robot in Gazebo.

The default launch runs navigation. Install optional dependencies for keyboard control, mapping, repeated patrols, and camera viewing as described in their sections below.

Run all subsequent commands from the project root. The build and runtime commands generate `build/`, `install/`, and `log/`; these directories need not exist in a fresh download. Avoid mixing different ROS environments. The wrapper clears conflicting paths.

## 3. Launch Options and Navigation

### 3.1 Common Commands

| Task | Command |
| --- | --- |
| Build the three navigation packages | `bash scripts/navigation.sh build` |
| Start Gazebo, Nav2, and RViz together | `bash scripts/navigation.sh demo` |
| Run without graphical windows | `bash scripts/navigation.sh demo gui:=false use_rviz:=false` |
| Start simulation only | `bash scripts/navigation.sh sim` |
| Start navigation and RViz only | `bash scripts/navigation.sh nav` |
| List launch arguments | `bash scripts/navigation.sh ros2 launch fishbot_navigation2 simulation.launch.py --show-args` |

To launch separately, run `sim` and `nav` in two terminals. The combined `demo` command includes both.

The default world is `fishbot_description/world/custom_room.world`, the map is `fishbot_navigation2/maps/room.yaml`, and the navigation parameters are in `fishbot_navigation2/config/nav2_params.yaml`.

To use another map or parameter file:

```bash
bash scripts/navigation.sh demo \
  map:="$PWD/log/maps/room_new.yaml" \
  params_file:="$PWD/fishbot_navigation2/config/nav2_params.yaml"
```

### 3.2 RViz Displays

- **Map:** the room map; set the global Fixed Frame to `map`.
- **RobotModel:** the robot model from `/robot_description`.
- **LaserScan:** select `/scan` to display detected obstacles.
- **Global/Local Costmap:** obstacles and the inflated regions used by navigation.
- **Path:** the global path is usually `/plan`, and the local path is `/local_plan`.
- **2D Pose Estimate:** set or correct the robot's map position and heading.
- **Nav2 Goal:** select a destination and final heading.

The default Nav2 RViz configuration includes the main displays. If the robot or scans are missing, initialize localization and check the selected topics and Fixed Frame.

### 3.3 Initialize Localization and Send a Goal

After a fresh startup, while the robot remains at the origin:

```bash
bash scripts/navigation.sh ros2 run fishbot_application init_robot_pose \
  --ros-args -p use_sim_time:=true
```

This node initializes `(0, 0, 0)` and keeps running. Leave it in a separate terminal or stop it with `Ctrl+C`; stopping this node does not clear AMCL's established localization.

Once localization is ready, send a goal at `(2, 1)` meters from another terminal:

```bash
bash scripts/navigation.sh ros2 action send_goal \
  /navigate_to_pose nav2_msgs/action/NavigateToPose \
  '{pose: {header: {frame_id: map}, pose: {position: {x: 2.0, y: 1.0, z: 0.0}, orientation: {w: 1.0}}}}' \
  --feedback
```

The single-goal example uses the same destination:

```bash
bash scripts/navigation.sh ros2 run fishbot_application nav_to_pose \
  --ros-args -p use_sim_time:=true
```

Goals use the `map` frame and meter units. `orientation.w: 1.0` faces `+x`. Rebuild after changing a goal in the example source.

### 3.4 Automated Navigation Check

Start a fresh simulation, then run this in another terminal:

```bash
bash scripts/navigation.sh check --x 2.0 --y 1.0
```

The script checks valid laser scans, simulation time, odometry, AMCL, and Nav2 readiness. It initializes localization and sends a goal. Success requires a successful Nav2 result, a final localized position error within 0.25 m, valid laser scans, and nonzero velocity commands.

You can set the goal heading, timeout, report location, and actual initial pose:

```bash
bash scripts/navigation.sh check \
  --x 2.0 --y 1.0 --yaw 0.0 \
  --initial-x 0.0 --initial-y 0.0 --initial-yaw 0.0 \
  --timeout 180 \
  --output log/navigation_check.json
```

Angles are in radians. If the robot has moved, supply its actual current pose through `--initial-*`, or restart the simulation first.

### 3.5 Read the Robot Pose

```bash
bash scripts/navigation.sh ros2 run fishbot_application get_robot_pose \
  --ros-args -p use_sim_time:=true
```

This example prints the translation, quaternion, and Euler angles for `map → base_footprint`. You can also inspect the transform directly:

```bash
bash scripts/navigation.sh ros2 run tf2_ros tf2_echo map base_footprint
```

## 4. Keyboard Control

Install the keyboard control package:

```bash
conda install \
  --name ros2_patrol \
  --override-channels -c robostack-humble -c conda-forge \
  ros-humble-teleop-twist-keyboard
```

With the simulation running, start keyboard control in a separate terminal:

```bash
bash scripts/navigation.sh ros2 run teleop_twist_keyboard teleop_twist_keyboard \
  --ros-args -p speed:=0.15 -p turn:=0.5
```

Keep keyboard focus in that terminal. Use `i` to move forward, `,` to reverse, `j/l` to turn, and `k` to stop. Follow the terminal instructions for other combinations. Commands are published on `/cmd_vel`.

Cancel any active navigation task before manual driving so that one source controls the base at a time. For mapping, start only `sim` and then use keyboard control.

## 5. Build, Save, and Use a Map

Install the mapping dependency:

```bash
conda install --name ros2_patrol --override-channels \
  -c robostack-humble -c conda-forge ros-humble-slam-toolbox
```

Stop any existing `demo` or `nav` launch before following these steps in separate terminals.

**Terminal 1: start simulation.**

```bash
bash scripts/navigation.sh sim
```

**Terminal 2: start SLAM.**

```bash
bash scripts/navigation.sh ros2 launch slam_toolbox online_async_launch.py \
  use_sim_time:=true
```

The installed SLAM defaults use `base_footprint`, `odom`, `map`, and `/scan`, matching this robot. To use a custom configuration, pass `slam_params_file:=/absolute/path/to/slam.yaml`. See the [Nav2 mapping and localization guide](https://docs.nav2.org/rolling/configuration_and_development/first_time_robot_setup_guide/sensors/mapping_localization/).

**Terminal 3: open RViz.**

```bash
bash scripts/navigation.sh ros2 run rviz2 rviz2 \
  --ros-args -p use_sim_time:=true
```

Set Fixed Frame to `map`. Add `Map` (`/map`), `LaserScan` (`/scan`), `RobotModel`, and `TF` displays.

**Terminal 4: start keyboard control as described in Section 4.** Drive slowly around the room so that laser scans cover passages and obstacles.

**Terminal 5: save the map.** Once the map is visible in RViz:

```bash
mkdir -p log/maps
bash scripts/navigation.sh ros2 run nav2_map_server map_saver_cli \
  -f "$PWD/log/maps/room_new" --ros-args -p use_sim_time:=true
```

This produces `room_new.yaml` and a map image. The image extension depends on the saver settings. Supply the YAML path when launching navigation.

When mapping is complete, stop SLAM and keyboard control, leave simulation running, and start navigation on the saved map:

```bash
bash scripts/navigation.sh nav map:="$PWD/log/maps/room_new.yaml"
```

Use **2D Pose Estimate** in RViz to set the robot's actual current pose, then send a navigation goal. SLAM and AMCL both publish `map → odom`; run only the localization source for the selected mode.

## 6. Waypoint Navigation

Start `demo`, initialize localization, and run:

```bash
bash scripts/navigation.sh ros2 run fishbot_application waypoint_follower \
  --ros-args -p use_sim_time:=true
```

The default route in [waypoint_follower.py](../fishbot_application/fishbot_application/waypoint_follower.py) is:

```text
(2.0, 1.0, 0.0) → (0.0, 1.0, 0.0) → (0.0, 0.0, 0.0)
```

Each tuple is `(x, y, yaw)` in meters and radians. The example calls Nav2 `FollowWaypoints`, runs the route once, and prints waypoint progress and the result. To change the route, edit its `PoseStamped` objects and run `bash scripts/navigation.sh build`.

## 7. Repeated Patrols, Speech, and Image Capture

### 7.1 Workflow and Dependencies

The `autopartol_robot` workflow announces initialization, sets the initial pose, visits each waypoint, announces arrival, captures an image, and repeats the route until stopped.

This workflow requires image and speech dependencies, plus the `autopartol_interfaces` and `autopartol_robot` packages. Install dependencies first, then build the packages in the next section:

```bash
conda install --name ros2_patrol --override-channels \
  -c robostack-humble -c conda-forge \
  ros-humble-cv-bridge ros-humble-tf-transformations opencv
```

Install the speech dependencies:

```bash
sudo apt install espeak-ng
bash scripts/navigation.sh python -m pip install espeakng
```

The project uses `espeakng.Speaker()` from the [espeakng Python bindings](https://pypi.org/project/espeakng/). Check the API and speech engine:

```bash
bash scripts/navigation.sh python -c "import espeakng; print(espeakng.Speaker)"
espeak-ng --voices
espeak-ng -v en 'Patrol robot speech test'
```

Speech requires an available audio output device. The combined patrol, speech, and image capture workflow still requires integration testing.

### 7.2 Build the Patrol Interface and Nodes

Build navigation as described in Section 2, then run:

```bash
bash scripts/navigation.sh colcon build \
  --base-paths autopartol_interfaces autopartol_robot \
  --symlink-install --cmake-args -DBUILD_TESTING=OFF \
  -DCMAKE_POLICY_VERSION_MINIMUM=3.5
```

Each subsequent wrapper invocation loads the updated workspace.

### 7.3 Configure the Route and Image Directory

See [partol_config.yaml](../autopartol_robot/config/partol_config.yaml) for the original configuration. Its `use_sim_time` value is `false`; use `true` for simulation. Create a separate configuration file:

```bash
mkdir -p log/patrol_images
cat > log/partol_config.yaml <<EOF
/partol_node:
  ros__parameters:
    use_sim_time: true
    initial_point: [0.0, 0.0, 0.0]
    target_points: [2.0, 1.0, 0.0, 0.0, 1.0, 1.57, 0.0, 0.0, 0.0]
    img_save_path: "$PWD/log/patrol_images/"
EOF
```

| Parameter | Meaning |
| --- | --- |
| `initial_point` | The robot's actual starting `[x, y, yaw]`. |
| `target_points` | A flat list of waypoints in `x, y, yaw` groups; its length must be a multiple of three. |
| `img_save_path` | An existing image directory. Include a trailing `/` because the code appends filenames directly. |
| `use_sim_time` | Set to `true` for Gazebo simulation. |

Images are named `img_<x>_<y>.png`, with coordinates rounded to two decimal places. Repeated captures at the same coordinates overwrite the corresponding file.

### 7.4 Start Speech and Patrol

Start a fresh `demo` and keep the robot at the pose specified by `initial_point`.

**Terminal 2: start the speech service.**

```bash
bash scripts/navigation.sh ros2 run autopartol_robot speaker
```

Test the service independently from another terminal:

```bash
bash scripts/navigation.sh ros2 service call \
  /speech_text autopartol_interfaces/srv/SpeechText \
  "{text: 'Robot ready to begin patrol'}"
```

[SpeechText.srv](../autopartol_interfaces/srv/SpeechText.srv) defines a `string text` request and a `bool result` response.

**Terminal 3: start the patrol node.**

```bash
bash scripts/navigation.sh ros2 run autopartol_robot partol_node \
  --ros-args --params-file "$PWD/log/partol_config.yaml"
```

The patrol node initializes localization. Keep the speech service running: the code waits for `/speech_text` and for each announcement to complete.

The original combined launch is also available:

```bash
bash scripts/navigation.sh ros2 launch autopartol_robot autopartol.launch.py
```

It reads the package's `config/partol_config.yaml`. Before using it, update simulation time, the route, the initial pose, and the image directory in that source configuration, then rebuild `autopartol_robot`. This launch does not read the separate `log/partol_config.yaml` created above.

### 7.5 Check Task and Image Results

The patrol code announces arrival and captures an image after navigation ends without distinguishing successful, failed, or canceled `TaskResult` values. Check the Nav2 result when assessing arrival. Image saving is skipped if no camera frame has arrived, so verify that files were created after an image capture announcement.

To stop, press `Ctrl+C` in the patrol terminal and cancel any active navigation goal in RViz before stopping speech and simulation. Exiting a navigation client does not guarantee that its server-side goal is canceled.

## 8. Camera and Sensor Viewing

### 8.1 View Images in RViz

With simulation running, add an **Image** display and select `/camera_sensor/image_raw`. You can also display depth images and point clouds. Check the published topics:

```bash
bash scripts/navigation.sh ros2 topic list -t
bash scripts/navigation.sh ros2 topic info /camera_sensor/image_raw -v
```

### 8.2 Standalone Image Viewer

Install the optional viewer:

```bash
conda install \
  --name ros2_patrol \
  --override-channels -c robostack-humble -c conda-forge \
  ros-humble-rqt-image-view
```

Launch it and choose an image topic from the dropdown:

```bash
bash scripts/navigation.sh ros2 run rqt_image_view rqt_image_view
```

### 8.3 Main Topics and Frames

| Name | Type or purpose |
| --- | --- |
| `/clock` | Gazebo simulation time. |
| `/robot_description` | The robot URDF description. |
| `/joint_states` | Wheel joint states. |
| `/cmd_vel` | `geometry_msgs/msg/Twist` base velocity commands. |
| `/odom` | `nav_msgs/msg/Odometry` base odometry. |
| `/scan` | `sensor_msgs/msg/LaserScan` planar laser scans. |
| `/imu` | IMU data. |
| `/map` | A `nav_msgs/msg/OccupancyGrid` map. |
| `/amcl_pose` | AMCL localization estimates. |
| `/camera_sensor/image_raw` | RGB images used for patrol image capture. |
| `/camera_sensor/depth/image_raw` | Depth images; confirm the actual topic with `topic list -t`. |
| `/camera_sensor/points` | Depth camera point clouds. |
| `/navigate_to_pose` | Single-goal navigation action. |
| `/follow_waypoints` | Waypoint navigation action. |
| `/speech_text` | Speech service provided by `speaker`. |

The main TF chain is `map → odom → base_footprint → base_link → sensor frames`. AMCL or SLAM provides `map → odom`, the base controller provides `odom → base_footprint`, and the robot state publisher provides the model's internal transforms.

## 9. Configuration and Troubleshooting

### 9.1 Common Configuration Files

| File | Settings |
| --- | --- |
| `fishbot_navigation2/config/nav2_params.yaml` | AMCL, planning, the DWB controller, costmaps, and goal tolerances. |
| `fishbot_navigation2/maps/room.yaml` | Map image path, resolution, and origin. |
| `fishbot_description/config/fishbot_ros2_controller.yaml` | Wheel separation, wheel radius, odometry, and command timeout. |
| `fishbot_description/urdf/fishbot/` | Base, wheels, sensors, and Gazebo plugins. |
| `fishbot_description/world/custom_room.world` | The room and obstacles. |
| `autopartol_robot/config/partol_config.yaml` | Route and initial pose used by the original patrol launch. |

The base uses a 0.20 m wheel separation and a 0.032 m wheel radius. Nav2's configured maximum forward speed is 0.26 m/s; position and heading tolerances are 0.15 m and 0.15 rad. Keep the model, controller, and navigation parameters consistent. The base currently computes odometry with `open_loop: true`.

### 9.2 Inspection Commands

```bash
bash scripts/navigation.sh ros2 node list
bash scripts/navigation.sh ros2 topic list -t
bash scripts/navigation.sh ros2 topic hz /scan
bash scripts/navigation.sh ros2 topic hz /odom
bash scripts/navigation.sh ros2 topic echo /clock --once
bash scripts/navigation.sh ros2 lifecycle get /amcl
bash scripts/navigation.sh ros2 lifecycle get /bt_navigator
bash scripts/navigation.sh ros2 action list -t
```

`topic hz` runs until you press `Ctrl+C`. Use the same `ROS_DOMAIN_ID` in all terminals.

### 9.3 Common Issues

| Symptom | What to check |
| --- | --- |
| `ros2` is missing or Foxy is loaded | Use the wrapper and check the `conda_root` and `patrol_env` paths at the top of the script. |
| `option --editable not recognized` | Check setuptools in the project environment and use the configured `<80` version. |
| CMake rejects an old policy version | Use the build command with `-DCMAKE_POLICY_VERSION_MINIMUM=3.5` from this guide. |
| Startup waits for `odom` or `map` transforms | Wait for the robot and controllers to activate, then initialize localization. |
| Nav2 does not become ready | Check `/clock`, `/scan`, `/odom`, and `map → base_footprint`; the global costmap needs localization before activation can finish. |
| The robot or scans appear in the wrong place | Check Fixed Frame, the initial pose, whether the map matches the world, and `use_sim_time`. |
| Duplicate models, an existing entity, or a busy Gazebo port | Stop the previous launch in its terminal, then start one `demo` instance. |
| `model://cafe_table/...` or `No mesh specified` | The table's visual mesh is not included in the repository, so its appearance may be incomplete. |
| `ros2 control` is unavailable | That CLI extension is optional. This project loads the base controllers with `controller_manager/spawner`. |
| Patrol waits for the speech service | Check that both patrol packages were built, `espeakng` is installed, and `speaker` is running. |
| An image capture announcement produces no file | Check the camera topic, directory existence, trailing `/`, and write permission. |
| An example raises `NoneType` while reading feedback | The examples access feedback fields directly. Use the action command or automated check in Section 3 to verify navigation first. |
| The Nav2 container does not stop immediately | Launch escalates termination signals if composed nodes time out. Wait for the launch terminal to finish before restarting. |

## 10. Project Layout and Entry Points

```text
ROS2_PARTOL_ROBOT/
├── environment.navigation.yml       # Humble Conda navigation dependencies
├── scripts/
│   ├── navigation.sh                # Environment, build, and launch wrapper
│   └── check_navigation.py          # Navigation check and JSON report
├── fishbot_description/             # URDF, sensors, controllers, and Gazebo world
├── fishbot_navigation2/             # Nav2 parameters, maps, and launch files
├── fishbot_application/             # Localization, pose lookup, and navigation examples
├── autopartol_interfaces/           # Custom SpeechText service
├── autopartol_robot/                # Repeated patrols, speech, and image capture
├── docs/
│   ├── USAGE.md                     # Installation and operating instructions
│   └── images/                      # Screenshots and animated preview
└── log/                             # Generated logs, reports, and example output
```

The package names `autopartol_*` and filenames `partol_*` preserve the original spelling. View the robot model in Gazebo and the navigation RViz window. The older `display_robot.launch.py` is a standalone model example: it references `display_model.rviz`, while the actual file is named `dispaly_model.rviz`. Install `joint_state_publisher` and correct that path before using this example.

## Acknowledgements

This project builds on educational materials from [fishros / FishBot](https://github.com/fishros). Environment setup follows the [RoboStack documentation](https://robostack.github.io/GettingStarted.html), and navigation and mapping configuration follow the [Nav2 documentation](https://docs.nav2.org/).
