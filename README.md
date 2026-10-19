# ROS 2 Patrol Robot Simulation

基于 FishBot 的移动机器人仿真项目：在 Gazebo 中运行差速底盘、激光雷达和相机，通过 Nav2 完成定位、路径规划与导航，并提供多点导航、循环巡逻、语音播报和到点拍照代码。

<p align="center">
  <img src="docs/images/gazebo_simulation.jpg" width="48%" alt="Gazebo 中的巡逻机器人">
  <img src="docs/images/navigation_rviz.jpg" width="48%" alt="RViz 导航地图与路径">
</p>

## 1. 快速启动：直接看导航效果

**本机环境已安装，导航包已编译。** 打开终端，进入项目目录：

```bash
cd /home/qiwang/job_search/4_Projects_Portfolio/ROS2_PARTOL_ROBOT
bash scripts/navigation.sh demo
```

这个命令同时启动 Gazebo、机器人、底盘控制器、Nav2 和 RViz。每次只运行一套仿真；如果窗口已经打开，直接操作现有窗口。

1. 等待 Gazebo 中出现机器人、RViz 中出现房间地图。
2. 首次启动时，在 RViz 点击 **2D Pose Estimate**，在机器人真实位置按住鼠标拖出朝向。刚重启仿真时，初始位置为地图坐标 `(0, 0)`，朝向 `+x`。
3. 点击 **Nav2 Goal**，在地图的可通行区域按住鼠标拖出目标朝向，再松开。
4. 在 Gazebo 观察运动，在 RViz 观察激光、规划路径和代价地图。日志出现 `Goal succeeded` 表示导航任务成功。
5. 在启动终端按 `Ctrl+C` 关闭整套程序。再次启动时重新初始化定位。

机器人已经移动后，**2D Pose Estimate 应设为当前真实位置**。它用于告诉定位系统机器人在哪里，不会让 Gazebo 中的机器人瞬移回原点。

## 2. 功能与验证状态

验证日期：**2026-10-19**。本项目的运行和验证范围为 Gazebo 仿真。

| 功能 | 用途 | 当前状态 |
| --- | --- | --- |
| Gazebo + RViz | 查看机器人、地图、激光和规划路径 | 已实际启动并完成导航演示 |
| AMCL + Nav2 | 已知地图上的定位、规划、避障与目标点导航 | 已验证到达 `(2, 1)` 米目标 |
| 自动导航检查 | 初始化定位、下发目标、保存检测报告 | 有界面和无界面均通过 |
| 单次多点导航 | 依次经过预设路点，执行一轮 | 已有代码，本次未单独验证 |
| 键盘遥控 | 手动驾驶底盘，辅助建图 | 需安装遥控包 |
| SLAM 建图与存图 | 用激光生成新地图，供后续导航使用 | SLAM Toolbox 已安装，完整建图流程待验证 |
| 相机显示 | 查看 RGB、深度图和点云 | 仿真已加载相机；独立查看器需另装 |
| 循环巡逻 + 播报 + 拍照 | 反复访问配置路点，并在每站保存相机图像 | 已有代码；需补语音依赖、编译巡逻包并验证 |

本次到达结果：

| 模式 | 目标 `(x, y)` / m | 定位终点 `(x, y)` / m | 位置误差 | 结果 |
| --- | --- | --- | --- | --- |
| 无界面 | `(2.0, 1.0)` | `(1.919, 0.894)` | 0.133 m | 成功 |
| Gazebo + RViz | `(2.0, 1.0)` | `(1.890, 0.906)` | 0.144 m | 成功 |

误差来自最终 `map → base_footprint` 定位结果。检测报告分别保存于 `log/navigation_check.json` 和 `log/navigation_gui_check.json`；这些日志是本地生成文件。

## 3. 环境配置与安装

### 3.1 本机已验证的环境

| 项目 | 配置 |
| --- | --- |
| 宿主系统 | Ubuntu 20.04.6 LTS，Linux x86_64 |
| 系统原有 ROS | ROS 2 Foxy，位于 `/opt/ros/foxy` |
| 项目使用的 ROS | RoboStack 提供的 ROS 2 Humble |
| Conda 根目录 | `/home/qiwang/miniconda3` |
| 项目环境目录 | `/var/tmp/qiwang/conda/envs/ros2_patrol` |
| Python | 3.12.15 |
| Gazebo Classic | 11.15.1 |
| Nav2 | 1.1.20 |
| RViz | 11.2.26 |
| SLAM Toolbox | 2.6.10 |
| gazebo_ros2_control | 0.4.10 |
| setuptools | 79.0.1，配置中限制为 `<80` |
| CMake | 4.2.3；构建时传入 `CMAKE_POLICY_VERSION_MINIMUM=3.5` |

环境本身约占 **4.9 GB**，下载和解压缓存还需要额外空间。安装时 `/home` 只剩约 4.5 GB，因此选择空间充足的根分区。可用以下命令查看当前磁盘情况：

```bash
df -h /home /var/tmp /tmp
du -sh /var/tmp/qiwang/conda/envs/ros2_patrol
```

`/var/tmp` 受系统临时文件清理策略影响。长期保存时可在有权限、空间足够的持久目录按配置重建环境，并修改下面的环境变量。**不要直接移动已安装的 Conda 环境目录**，其中包含安装路径。

### 3.2 在新机器或其他目录重建

需要先安装 Conda。环境依赖见 [environment.navigation.yml](environment.navigation.yml)，ROS 包来自 [RoboStack](https://robostack.github.io/GettingStarted.html)。

```bash
cd /path/to/ROS2_PARTOL_ROBOT

# 按实际位置修改；已有本机环境时无需重复创建。
export PATROL_CONDA_ROOT="$HOME/miniconda3"
export PATROL_CONDA_PREFIX="/var/tmp/$USER/conda/envs/ros2_patrol"

source "$PATROL_CONDA_ROOT/etc/profile.d/conda.sh"
CONDA_PKGS_DIRS=/tmp/patrol_conda_pkgs conda env create \
  --prefix "$PATROL_CONDA_PREFIX" \
  --file environment.navigation.yml

bash scripts/navigation.sh build
bash scripts/navigation.sh demo
```

环境文件描述导航所需依赖和兼容限制；安装时由 Conda 解析具体构建版本。它不是所有软件包精确版本的锁文件。

`setuptools<80` 用于兼容 Humble 的经典 Python 包构建方式；过新版本会出现 `option --editable not recognized`。

### 3.3 每个终端如何使用环境

本文命令均在项目根目录执行。推荐通过包装脚本运行：

```bash
bash scripts/navigation.sh ros2 pkg list
bash scripts/navigation.sh python -c "import rclpy; print('ROS Python OK')"
```

脚本自动激活 Humble、清除冲突的 Foxy/外部库路径，并加载本项目的 `install/setup.bash`。使用脚本时无需提前激活环境。自定义安装位置后，每个终端均需设置 `PATROL_CONDA_PREFIX` 和 `PATROL_CONDA_ROOT`；本机默认位置可直接使用。

也可手动激活环境：

```bash
source /home/qiwang/miniconda3/etc/profile.d/conda.sh
conda activate /var/tmp/qiwang/conda/envs/ros2_patrol
source install/setup.bash
```

手动方式请从没有加载系统 Foxy 的干净终端开始。不要在 Humble Conda 终端中执行 `source /opt/ros/foxy/setup.bash`。

日志默认保存在 `log/ros/`。`build/`、`install/`、`log/` 都是生成目录。

### 3.4 使用系统安装的 Humble

在已安装 ROS 2 Humble 的 Ubuntu 22.04 上，可通过系统包提供相同依赖。这条安装路径本次未重新验证。

```bash
sudo apt update
sudo apt install ros-humble-ros-base ros-humble-rviz2 \
  ros-humble-navigation2 ros-humble-nav2-bringup \
  ros-humble-nav2-simple-commander ros-humble-slam-toolbox \
  ros-humble-gazebo-ros-pkgs ros-humble-gazebo-ros2-control \
  ros-humble-diff-drive-controller ros-humble-joint-state-broadcaster \
  ros-humble-xacro ros-humble-robot-state-publisher \
  ros-humble-tf-transformations python3-colcon-common-extensions

source /opt/ros/humble/setup.bash
colcon build --base-paths fishbot_description fishbot_navigation2 fishbot_application \
  --symlink-install --cmake-args -DBUILD_TESTING=OFF
source install/setup.bash
ros2 launch fishbot_navigation2 simulation.launch.py
```

系统安装方式使用原生 `ros2` 命令；下文 `bash scripts/navigation.sh ros2 ...` 对应去掉包装脚本后的命令。

## 4. 启动方式与导航操作

### 4.1 常用启动命令

| 操作 | 命令 |
| --- | --- |
| 编译导航相关的三个包 | `bash scripts/navigation.sh build` |
| 同时打开 Gazebo、Nav2、RViz | `bash scripts/navigation.sh demo` |
| 完全无界面运行 | `bash scripts/navigation.sh demo gui:=false use_rviz:=false` |
| 只运行仿真 | `bash scripts/navigation.sh sim` |
| 只运行导航和 RViz | `bash scripts/navigation.sh nav` |
| 列出启动参数 | `bash scripts/navigation.sh ros2 launch fishbot_navigation2 simulation.launch.py --show-args` |

分开启动时，在两个终端分别运行 `sim` 和 `nav`。一键 `demo` 已包含这两部分。

默认房间为 `fishbot_description/world/custom_room.world`，地图为 `fishbot_navigation2/maps/room.yaml`，导航参数为 `fishbot_navigation2/config/nav2_params.yaml`。

加载其他地图或参数：

```bash
bash scripts/navigation.sh demo \
  map:="$PWD/log/maps/room_new.yaml" \
  params_file:="$PWD/fishbot_navigation2/config/nav2_params.yaml"
```

### 4.2 RViz 中看什么

- **Map**：静态房间地图；全局坐标系设为 `map`。
- **RobotModel**：机器人模型，描述来自 `/robot_description`。
- **LaserScan**：选择 `/scan`，显示机器人探测到的障碍物。
- **Global/Local Costmap**：显示导航使用的障碍物和膨胀区域。
- **Path**：全局路径通常为 `/plan`，局部路径为 `/local_plan`。
- **2D Pose Estimate**：校正机器人的地图位置与朝向。
- **Nav2 Goal**：选择导航终点和最终朝向。

Nav2 默认 RViz 配置会预设主要显示项。如果机器人或激光没有显示，先完成定位，再检查对应话题和 Fixed Frame。

### 4.3 用命令初始化定位、发送目标

刚启动、机器人仍在原点时，可用程序初始化定位：

```bash
bash scripts/navigation.sh ros2 run fishbot_application init_robot_pose \
  --ros-args -p use_sim_time:=true
```

该节点初始化 `(0, 0, 0)` 后持续运行，可保留在单独终端；按 `Ctrl+C` 结束此节点不会清除 AMCL 已建立的定位。

定位就绪后，在另一终端发送 `(2, 1)` 米目标：

```bash
bash scripts/navigation.sh ros2 action send_goal \
  /navigate_to_pose nav2_msgs/action/NavigateToPose \
  '{pose: {header: {frame_id: map}, pose: {position: {x: 2.0, y: 1.0, z: 0.0}, orientation: {w: 1.0}}}}' \
  --feedback
```

代码中的单点导航示例也使用同一目标：

```bash
bash scripts/navigation.sh ros2 run fishbot_application nav_to_pose \
  --ros-args -p use_sim_time:=true
```

目标坐标位于 `map` 坐标系，长度单位为米；`orientation.w: 1.0` 表示朝向 `+x`。修改示例程序中的目标后重新运行构建命令。

### 4.4 自动检查导航

先启动一套新仿真，再在另一终端执行：

```bash
bash scripts/navigation.sh check --x 2.0 --y 1.0
```

脚本检查有效激光、仿真时钟、里程计、AMCL 和 Nav2 状态，初始化定位并发送目标；成功条件包含 Nav2 成功状态、定位终点误差不超过 0.25 m，以及有效激光和非零速度指令。

可配置目标朝向、超时、报告位置和初始真实位姿：

```bash
bash scripts/navigation.sh check \
  --x 2.0 --y 1.0 --yaw 0.0 \
  --initial-x 0.0 --initial-y 0.0 --initial-yaw 0.0 \
  --timeout 180 \
  --output log/navigation_check.json
```

角度单位为弧度。机器人已经移动时，应把 `--initial-*` 改为真实当前位置，或先重启仿真。

### 4.5 查询机器人位置

```bash
bash scripts/navigation.sh ros2 run fishbot_application get_robot_pose \
  --ros-args -p use_sim_time:=true
```

程序打印 `map → base_footprint` 平移、四元数与欧拉角。也可直接查看 TF：

```bash
bash scripts/navigation.sh ros2 run tf2_ros tf2_echo map base_footprint
```

## 5. 键盘遥控

当前基础环境需要补装遥控包。以下安装操作在普通终端执行；若环境位置不同，替换 `--prefix`：

```bash
CONDA_PKGS_DIRS=/tmp/patrol_conda_pkgs conda install \
  --prefix /var/tmp/qiwang/conda/envs/ros2_patrol \
  --override-channels -c robostack-humble -c conda-forge \
  ros-humble-teleop-twist-keyboard
```

启动仿真后，在单独终端运行：

```bash
bash scripts/navigation.sh ros2 run teleop_twist_keyboard teleop_twist_keyboard \
  --ros-args -p speed:=0.15 -p turn:=0.5
```

键盘焦点要放在遥控终端：`i` 前进，`,` 后退，`j/l` 转向，`k` 停止；其他组合键以终端提示为准。遥控发布到 `/cmd_vel`。

手动驾驶前先取消正在执行的导航任务，确保底盘同一时刻只有一个运动指令来源。建图时可以只启动 `sim`，然后使用遥控。

## 6. SLAM 建图、保存地图与切换导航

此流程使用当前已安装的 SLAM Toolbox，完整建图结果仍需实际验证。启动前停止现有 `demo` 或 `nav`，随后分别在几个终端执行。

**终端 1：启动仿真。**

```bash
bash scripts/navigation.sh sim
```

**终端 2：启动 SLAM。**

```bash
bash scripts/navigation.sh ros2 launch slam_toolbox online_async_launch.py \
  use_sim_time:=true
```

安装版本的默认 SLAM 配置使用 `base_footprint`、`odom`、`map` 和 `/scan`，与当前机器人一致。自定义配置时，可通过 `slam_params_file:=/absolute/path/to/slam.yaml` 传入。[SLAM 与 Nav2 的配置说明](https://docs.nav2.org/rolling/configuration_and_development/first_time_robot_setup_guide/sensors/mapping_localization/)

**终端 3：打开 RViz。**

```bash
bash scripts/navigation.sh ros2 run rviz2 rviz2 \
  --ros-args -p use_sim_time:=true
```

将 Fixed Frame 设为 `map`，添加 `Map`（`/map`）、`LaserScan`（`/scan`）、`RobotModel` 和 `TF`。

**终端 4：按第 5 节启动键盘遥控。** 缓慢绕房间行驶，让激光覆盖通道和障碍物。

**终端 5：保存地图。** 等待 RViz 中地图形成后执行：

```bash
mkdir -p log/maps
bash scripts/navigation.sh ros2 run nav2_map_server map_saver_cli \
  -f "$PWD/log/maps/room_new" --ros-args -p use_sim_time:=true
```

生成 `room_new.yaml` 及地图图像，图像扩展名由保存器配置决定。导航时传入 YAML 文件路径。

建图完成后，停止 SLAM 和遥控，保留仿真，然后启动已知地图导航：

```bash
bash scripts/navigation.sh nav map:="$PWD/log/maps/room_new.yaml"
```

在 RViz 用 **2D Pose Estimate** 设置机器人当前真实位置，再发送导航目标。SLAM 和 AMCL 都会发布 `map → odom`，切换时应只保留当前模式对应的定位来源。

## 7. 单次多点导航

先启动 `demo` 并完成初始定位，然后执行：

```bash
bash scripts/navigation.sh ros2 run fishbot_application waypoint_follower \
  --ros-args -p use_sim_time:=true
```

[waypoint_follower.py](fishbot_application/fishbot_application/waypoint_follower.py) 中的默认路线为：

```text
(2.0, 1.0, 0.0) → (0.0, 1.0, 0.0) → (0.0, 0.0, 0.0)
```

每组为 `(x, y, yaw)`，单位为米和弧度。程序调用 Nav2 `FollowWaypoints`，依次执行一轮并打印路点进度与任务结果。更改路线需修改程序中的各个 `PoseStamped`，随后执行 `bash scripts/navigation.sh build`。

## 8. 循环巡逻、语音播报和到点拍照

### 8.1 运行逻辑与额外依赖

`autopartol_robot` 的巡逻逻辑为：播报准备初始化 → 设置初始位姿 → 逐个访问路点 → 每站播报并保存图像 → 重复整条路线，直到停止程序。

当前已安装 `cv_bridge`、OpenCV 和 `tf_transformations`；`autopartol_interfaces`、`autopartol_robot` 尚需编译，语音 Python 包 `espeakng` 和 `espeak-ng` 可执行文件需要安装。

在普通终端安装语音依赖：

```bash
sudo apt install espeak-ng
/var/tmp/qiwang/conda/envs/ros2_patrol/bin/python -m pip install espeakng
```

本项目使用 `espeakng.Speaker()`，对应 [espeakng Python 绑定](https://pypi.org/project/espeakng/)。安装后检查 API 和语音引擎：

```bash
bash scripts/navigation.sh python -c "import espeakng; print(espeakng.Speaker)"
espeak-ng --voices
espeak-ng -v zh '巡逻机器人语音测试'
```

声音输出依赖本机的音频设备和音量设置。此扩展流程本次尚未完成端到端验证。

### 8.2 编译巡逻接口和节点

先按第 3 节构建导航，再执行：

```bash
bash scripts/navigation.sh colcon build \
  --base-paths autopartol_interfaces autopartol_robot \
  --symlink-install --cmake-args -DBUILD_TESTING=OFF \
  -DCMAKE_POLICY_VERSION_MINIMUM=3.5
```

后续每次通过包装脚本启动程序时，都会重新加载构建后的工作空间。

### 8.3 配置巡逻路线与照片目录

参考配置为 [partol_config.yaml](autopartol_robot/config/partol_config.yaml)。原配置的 `use_sim_time` 为 `false`，仿真中应使用 `true`。建议建立独立配置文件：

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

| 参数 | 含义 |
| --- | --- |
| `initial_point` | 启动时机器人真实的 `[x, y, yaw]` |
| `target_points` | 按 `x, y, yaw` 三个数一组排列的路点列表，长度应为 3 的倍数 |
| `img_save_path` | 已存在的照片目录；当前代码直接拼接文件名，因此路径末尾必须有 `/` |
| `use_sim_time` | Gazebo 仿真中设为 `true` |

照片命名为 `img_<x>_<y>.png`，坐标保留两位小数。同一坐标重复拍照会覆盖同名文件。

### 8.4 启动语音与巡逻

先启动一套新的 `demo`，让机器人保持在与 `initial_point` 一致的位置。

**终端 2：启动语音服务。**

```bash
bash scripts/navigation.sh ros2 run autopartol_robot speaker
```

可在另一终端单独测试服务：

```bash
bash scripts/navigation.sh ros2 service call \
  /speech_text autopartol_interfaces/srv/SpeechText \
  "{text: '机器人准备开始巡逻'}"
```

接口见 [SpeechText.srv](autopartol_interfaces/srv/SpeechText.srv)：请求为 `string text`，响应为 `bool result`。

**终端 3：启动巡逻节点。**

```bash
bash scripts/navigation.sh ros2 run autopartol_robot partol_node \
  --ros-args --params-file "$PWD/log/partol_config.yaml"
```

巡逻节点会自行初始化定位。保持语音服务在线；代码会等待 `/speech_text` 服务，并依次等待播报完成。

原有合并启动入口也保留在仓库中：

```bash
bash scripts/navigation.sh ros2 launch autopartol_robot autopartol.launch.py
```

该入口固定读取包内 `config/partol_config.yaml`。使用它之前，应修改源码配置中的仿真时间、路线、初始位置和照片目录，并重新编译 `autopartol_robot`。它不会读取上面另建的 `log/partol_config.yaml`。

### 8.5 使用时检查任务结果

当前巡逻代码在导航结束后直接播报到达和拍照，没有按 `TaskResult` 区分成功、失败和取消；评估到达结果时应同时检查 Nav2 的任务状态。代码也会在尚未收到相机帧时跳过保存。语音提示“图像记录完成”之后，请检查照片目录是否实际生成文件。

停止时先在巡逻终端按 `Ctrl+C`，并在 RViz 确认取消仍在执行的导航目标，再停止语音和仿真。结束导航客户端进程不保证服务器上的目标自动取消。

## 9. 相机与传感器查看

### 9.1 在 RViz 看图像

仿真启动后，在 RViz 添加 **Image**，选择 `/camera_sensor/image_raw`。也可添加深度图或点云显示；以当前发布的话题为准：

```bash
bash scripts/navigation.sh ros2 topic list -t
bash scripts/navigation.sh ros2 topic info /camera_sensor/image_raw -v
```

### 9.2 独立图像查看器

安装可选查看器：

```bash
CONDA_PKGS_DIRS=/tmp/patrol_conda_pkgs conda install \
  --prefix /var/tmp/qiwang/conda/envs/ros2_patrol \
  --override-channels -c robostack-humble -c conda-forge \
  ros-humble-rqt-image-view
```

启动后在下拉框中选择图像话题：

```bash
bash scripts/navigation.sh ros2 run rqt_image_view rqt_image_view
```

### 9.3 关键话题和坐标系

| 名称 | 类型 / 用途 |
| --- | --- |
| `/clock` | Gazebo 仿真时间 |
| `/robot_description` | 机器人 URDF 描述 |
| `/joint_states` | 轮关节状态 |
| `/cmd_vel` | `geometry_msgs/msg/Twist`，底盘速度指令 |
| `/odom` | `nav_msgs/msg/Odometry`，底盘里程计 |
| `/scan` | `sensor_msgs/msg/LaserScan`，二维激光 |
| `/imu` | IMU 数据 |
| `/map` | `nav_msgs/msg/OccupancyGrid`，地图 |
| `/amcl_pose` | AMCL 定位结果 |
| `/camera_sensor/image_raw` | RGB 相机图像，巡逻拍照订阅源 |
| `/camera_sensor/depth/image_raw` | 深度图；用 `topic list -t` 确认实际话题 |
| `/camera_sensor/points` | 深度相机点云 |
| `/navigate_to_pose` | 单目标导航 Action |
| `/follow_waypoints` | 多路点导航 Action |
| `/speech_text` | 巡逻语音服务，需启动 `speaker` |

主要 TF 链为 `map → odom → base_footprint → base_link → 传感器坐标系`。AMCL 或 SLAM 提供 `map → odom`，底盘提供 `odom → base_footprint`，机器人状态发布器提供模型内部变换。

## 10. 参数修改与排查

### 10.1 常改配置

| 文件 | 常改内容 |
| --- | --- |
| `fishbot_navigation2/config/nav2_params.yaml` | AMCL、规划器、DWB 控制器、代价地图、目标容差 |
| `fishbot_navigation2/maps/room.yaml` | 地图图像路径、分辨率、原点 |
| `fishbot_description/config/fishbot_ros2_controller.yaml` | 轮距、轮半径、里程计、速度命令超时 |
| `fishbot_description/urdf/fishbot/` | 底盘、轮子、传感器和 Gazebo 插件 |
| `fishbot_description/world/custom_room.world` | 房间和障碍物 |
| `autopartol_robot/config/partol_config.yaml` | 原有巡逻入口读取的路线和初始位置 |

当前底盘轮距为 0.20 m、轮半径为 0.032 m；Nav2 配置的最大前进速度为 0.26 m/s，目标位置和朝向容差均为 0.15（m / rad）。模型、控制器与导航参数应保持一致。底盘当前使用 `open_loop: true` 计算里程计。

### 10.2 常用检查命令

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

`topic hz` 会持续运行，按 `Ctrl+C` 结束该检查。确认所有终端使用同一个 `ROS_DOMAIN_ID`。

### 10.3 常见现象

| 现象 | 检查或处理 |
| --- | --- |
| `ros2` 找不到，或加载到 Foxy | 使用包装脚本；自定义环境位置时设置 `PATROL_CONDA_PREFIX` |
| `option --editable not recognized` | 检查当前环境的 setuptools，使用配置中的 `<80` 版本 |
| CMake 提示旧策略不兼容 | 使用 README 中带 `-DCMAKE_POLICY_VERSION_MINIMUM=3.5` 的构建命令 |
| 初始出现 `odom` / `map` TF 等待信息 | 等待机器人和底盘控制器激活，再设置初始定位 |
| Nav2 一直未就绪 | 检查 `/clock`、`/scan`、`/odom` 和 `map → base_footprint`；全局代价地图需要定位后才能完成启动 |
| 机器人或激光在 RViz 中位置不正确 | 检查 Fixed Frame、初始定位、地图是否对应当前世界，以及各节点的 `use_sim_time` |
| 模型重复、实体已存在、Gazebo 端口被占用 | 返回原启动终端停止旧实例，再启动一套 `demo` |
| `model://cafe_table/...` 或 `No mesh specified` | 房间文件引用的桌子外观网格未随仓库提供；当前已验证导航能运行，桌子视觉可能不完整 |
| 找不到 `ros2 control` | 当前环境未额外安装该命令行扩展；本项目已改用 `controller_manager/spawner` 加载底盘 |
| 巡逻一直等待语音服务 | 检查两个巡逻包是否编译、`espeakng` 是否安装、`speaker` 是否运行 |
| 提示拍照完成但没有图片 | 检查相机话题、目录是否存在、路径末尾 `/` 和写入权限 |
| 示例程序访问反馈字段时报 `NoneType` | 示例直接读取反馈字段；可先使用第 4 节的 Action 命令或自动检查脚本验证导航 |
| 关闭时 Nav2 容器未及时退出 | 本环境曾出现组合节点关闭超时，launch 会继续发送终止信号；等待启动终端结束后再重开 |

## 11. 项目结构与入口

```text
ROS2_PARTOL_ROBOT/
├── environment.navigation.yml       # Humble Conda 导航依赖
├── scripts/
│   ├── navigation.sh                # 环境、构建和运行包装脚本
│   └── check_navigation.py          # 自动导航检查与 JSON 报告
├── fishbot_description/             # URDF、传感器、控制器和 Gazebo 世界
├── fishbot_navigation2/             # Nav2 配置、地图和启动文件
├── fishbot_application/             # 初始定位、位姿查询、单点/多点示例
├── autopartol_interfaces/           # SpeechText 自定义服务
├── autopartol_robot/                # 循环巡逻、语音和到点拍照
├── docs/images/                     # 项目展示图片
└── log/                             # 本地日志、报告与示例输出（生成目录）
```

包名 `autopartol_*` 和文件名 `partol_*` 沿用原项目拼写。机器人模型可直接在 Gazebo 与导航 RViz 中查看；旧的 `display_robot.launch.py` 是早期独立模型示例，其 RViz 配置引用 `display_model.rviz`，实际文件名为 `dispaly_model.rviz`，且需要额外安装 `joint_state_publisher` 后修正路径再使用。

## 致谢

本项目基于 [fishros / FishBot](https://github.com/fishros) 的教育材料扩展。环境安装参考 [RoboStack 文档](https://robostack.github.io/GettingStarted.html)，导航与建图配置参考 [Nav2 文档](https://docs.nav2.org/)。
