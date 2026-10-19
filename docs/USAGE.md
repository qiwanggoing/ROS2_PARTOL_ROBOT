# 安装与使用

本文从首次下载项目开始。所有操作均在 Linux x86_64 的终端中进行；图形演示需要桌面会话。

## 1. 下载项目与准备环境

准备 Git、Conda（Miniconda 或 Miniforge）和 C/C++ 构建工具。Ubuntu 可安装构建工具：

```bash
sudo apt update
sudo apt install git build-essential
```

安装并初始化 Conda 后，重新打开终端，下载项目：

```bash
git clone https://github.com/qiwanggoing/ROS2_PARTOL_ROBOT.git
cd ROS2_PARTOL_ROBOT
```

通过 [environment.navigation.yml](../environment.navigation.yml) 创建独立环境：

```bash
conda env create --file environment.navigation.yml
conda activate ros2_patrol
```

环境提供 ROS 2 Humble、Gazebo Classic 11、Nav2 和 RViz；宿主系统无需另外安装 ROS。ROS 的 Conda 分发方式见 [RoboStack 文档](https://robostack.github.io/GettingStarted.html)。环境文件中的 `setuptools<80` 用于兼容 Humble 的 Python 包构建工具。

如果默认磁盘空间不足，可选择有权限、空间充足的持久目录，例如：

```bash
conda env create --prefix "$HOME/conda-envs/ros2_patrol" --file environment.navigation.yml
conda activate "$HOME/conda-envs/ros2_patrol"
```

使用自定义目录时，下文的 `conda install --name ros2_patrol` 相应替换为 `conda install --prefix "环境的完整路径"`。

## 2. 构建并启动导航

先查看 Conda 和环境的安装路径：

```bash
conda info --base
conda env list
```

打开 [scripts/navigation.sh](../scripts/navigation.sh)，修改顶部的 `conda_root` 和 `patrol_env`。可以直接将这两行替换为：

```bash
conda_root="/你的/Conda安装目录"
patrol_env="/你的/ros2_patrol环境目录"
```

`conda_root` 填 `conda info --base` 的输出；`patrol_env` 填 `conda env list` 中 `ros2_patrol` 对应的完整路径。保存后，在项目根目录执行：

```bash
bash scripts/navigation.sh build
bash scripts/navigation.sh demo
```

脚本使用你填写的路径激活环境并加载项目。每个新终端先进入项目目录，再运行对应命令即可；更换环境位置时重新修改这两项。

首次启动后：

1. 等待 Gazebo 出现机器人、RViz 出现地图。
2. 在 RViz 点击 **2D Pose Estimate**，将初始位置设为 `(0, 0)`，朝向 `+x`。
3. 点击 **Nav2 Goal**，在可通行区域拖出目标位置和朝向。
4. 查看机器人运动和规划路径；`Goal succeeded` 表示导航成功。
5. 在启动终端按 `Ctrl+C` 退出，等待进程结束后再重启。

机器人已经移动时，定位应使用当前真实位置。`2D Pose Estimate` 调整定位估计，不会改变 Gazebo 中的实际位置。

项目默认运行导航模块。遥控、建图、循环巡逻和相机查看的使用方法见下文；各扩展的依赖在对应章节安装。

所有后续命令均在项目根目录执行。`build/`、`install/`、`log/` 由构建或运行生成，首次下载时无需预先存在。不要混合加载其他版本的 ROS 环境；包装脚本会清理冲突路径。

## 3. 启动方式与导航操作

### 3.1 常用启动命令

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

### 3.2 RViz 中看什么

- **Map**：静态房间地图；全局坐标系设为 `map`。
- **RobotModel**：机器人模型，描述来自 `/robot_description`。
- **LaserScan**：选择 `/scan`，显示机器人探测到的障碍物。
- **Global/Local Costmap**：显示导航使用的障碍物和膨胀区域。
- **Path**：全局路径通常为 `/plan`，局部路径为 `/local_plan`。
- **2D Pose Estimate**：校正机器人的地图位置与朝向。
- **Nav2 Goal**：选择导航终点和最终朝向。

Nav2 默认 RViz 配置会预设主要显示项。如果机器人或激光没有显示，先完成定位，再检查对应话题和 Fixed Frame。

### 3.3 用命令初始化定位、发送目标

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

### 3.4 自动检查导航

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

### 3.5 查询机器人位置

```bash
bash scripts/navigation.sh ros2 run fishbot_application get_robot_pose \
  --ros-args -p use_sim_time:=true
```

程序打印 `map → base_footprint` 平移、四元数与欧拉角。也可直接查看 TF：

```bash
bash scripts/navigation.sh ros2 run tf2_ros tf2_echo map base_footprint
```

## 4. 键盘遥控

使用键盘遥控前，先安装遥控包：

```bash
conda install \
  --name ros2_patrol \
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

## 5. SLAM 建图、保存地图与切换导航

先安装建图依赖：

```bash
conda install --name ros2_patrol --override-channels \
  -c robostack-humble -c conda-forge ros-humble-slam-toolbox
```

启动前停止已有的 `demo` 或 `nav`，随后分别在几个终端执行。

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

**终端 4：按第 4 节启动键盘遥控。** 缓慢绕房间行驶，让激光覆盖通道和障碍物。

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

## 6. 单次多点导航

先启动 `demo` 并完成初始定位，然后执行：

```bash
bash scripts/navigation.sh ros2 run fishbot_application waypoint_follower \
  --ros-args -p use_sim_time:=true
```

[waypoint_follower.py](../fishbot_application/fishbot_application/waypoint_follower.py) 中的默认路线为：

```text
(2.0, 1.0, 0.0) → (0.0, 1.0, 0.0) → (0.0, 0.0, 0.0)
```

每组为 `(x, y, yaw)`，单位为米和弧度。程序调用 Nav2 `FollowWaypoints`，依次执行一轮并打印路点进度与任务结果。更改路线时修改程序中的各个 `PoseStamped`，随后执行 `bash scripts/navigation.sh build`。

## 7. 循环巡逻、语音播报和到点拍照

### 7.1 运行逻辑与额外依赖

`autopartol_robot` 的巡逻逻辑为：播报准备初始化 → 设置初始位姿 → 逐个访问路点 → 每站播报并保存图像 → 重复整条路线，直到停止程序。

循环巡逻需要额外的图像与语音依赖，以及 `autopartol_interfaces`、`autopartol_robot` 两个包。先安装依赖，再按下一节编译：

```bash
conda install --name ros2_patrol --override-channels \
  -c robostack-humble -c conda-forge \
  ros-humble-cv-bridge ros-humble-tf-transformations opencv
```

在普通终端安装语音依赖：

```bash
sudo apt install espeak-ng
bash scripts/navigation.sh python -m pip install espeakng
```

本项目使用 `espeakng.Speaker()`，对应 [espeakng Python 绑定](https://pypi.org/project/espeakng/)。安装后检查 API 和语音引擎：

```bash
bash scripts/navigation.sh python -c "import espeakng; print(espeakng.Speaker)"
espeak-ng --voices
espeak-ng -v zh '巡逻机器人语音测试'
```

声音输出需要可用的音频设备。巡逻、语音与拍照的完整流程仍需联调。

### 7.2 编译巡逻接口和节点

先按第 2 节构建导航，再执行：

```bash
bash scripts/navigation.sh colcon build \
  --base-paths autopartol_interfaces autopartol_robot \
  --symlink-install --cmake-args -DBUILD_TESTING=OFF \
  -DCMAKE_POLICY_VERSION_MINIMUM=3.5
```

后续每次通过包装脚本启动程序时，都会重新加载构建后的工作空间。

### 7.3 配置巡逻路线与照片目录

参考配置为 [partol_config.yaml](../autopartol_robot/config/partol_config.yaml)。原配置的 `use_sim_time` 为 `false`，仿真中应使用 `true`。建议建立独立配置文件：

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

### 7.4 启动语音与巡逻

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

接口见 [SpeechText.srv](../autopartol_interfaces/srv/SpeechText.srv)：请求为 `string text`，响应为 `bool result`。

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

### 7.5 使用时检查任务结果

当前巡逻代码在导航结束后直接播报到达和拍照，没有按 `TaskResult` 区分成功、失败和取消；评估到达结果时应同时检查 Nav2 的任务状态。代码也会在尚未收到相机帧时跳过保存。语音提示“图像记录完成”之后，请检查照片目录是否实际生成文件。

停止时先在巡逻终端按 `Ctrl+C`，并在 RViz 确认取消仍在执行的导航目标，再停止语音和仿真。结束导航客户端进程不保证服务器上的目标自动取消。

## 8. 相机与传感器查看

### 8.1 在 RViz 看图像

仿真启动后，在 RViz 添加 **Image**，选择 `/camera_sensor/image_raw`。也可添加深度图或点云显示；以当前发布的话题为准：

```bash
bash scripts/navigation.sh ros2 topic list -t
bash scripts/navigation.sh ros2 topic info /camera_sensor/image_raw -v
```

### 8.2 独立图像查看器

查看相机图像时，按需安装查看器：

```bash
conda install \
  --name ros2_patrol \
  --override-channels -c robostack-humble -c conda-forge \
  ros-humble-rqt-image-view
```

启动后在下拉框中选择图像话题：

```bash
bash scripts/navigation.sh ros2 run rqt_image_view rqt_image_view
```

### 8.3 关键话题和坐标系

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

## 9. 参数修改与排查

### 9.1 常改配置

| 文件 | 常改内容 |
| --- | --- |
| `fishbot_navigation2/config/nav2_params.yaml` | AMCL、规划器、DWB 控制器、代价地图、目标容差 |
| `fishbot_navigation2/maps/room.yaml` | 地图图像路径、分辨率、原点 |
| `fishbot_description/config/fishbot_ros2_controller.yaml` | 轮距、轮半径、里程计、速度命令超时 |
| `fishbot_description/urdf/fishbot/` | 底盘、轮子、传感器和 Gazebo 插件 |
| `fishbot_description/world/custom_room.world` | 房间和障碍物 |
| `autopartol_robot/config/partol_config.yaml` | 原有巡逻入口读取的路线和初始位置 |

当前底盘轮距为 0.20 m、轮半径为 0.032 m；Nav2 配置的最大前进速度为 0.26 m/s，目标位置和朝向容差均为 0.15（m / rad）。模型、控制器与导航参数应保持一致。底盘当前使用 `open_loop: true` 计算里程计。

### 9.2 常用检查命令

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

### 9.3 常见现象

| 现象 | 检查或处理 |
| --- | --- |
| `ros2` 找不到，或加载到 Foxy | 使用包装脚本；自定义环境位置时设置 `PATROL_CONDA_PREFIX` |
| `option --editable not recognized` | 检查当前环境的 setuptools，使用配置中的 `<80` 版本 |
| CMake 提示旧策略不兼容 | 使用 README 中带 `-DCMAKE_POLICY_VERSION_MINIMUM=3.5` 的构建命令 |
| 初始出现 `odom` / `map` TF 等待信息 | 等待机器人和底盘控制器激活，再设置初始定位 |
| Nav2 一直未就绪 | 检查 `/clock`、`/scan`、`/odom` 和 `map → base_footprint`；全局代价地图需要定位后才能完成启动 |
| 机器人或激光在 RViz 中位置不正确 | 检查 Fixed Frame、初始定位、地图是否对应当前世界，以及各节点的 `use_sim_time` |
| 模型重复、实体已存在、Gazebo 端口被占用 | 返回原启动终端停止旧实例，再启动一套 `demo` |
| `model://cafe_table/...` 或 `No mesh specified` | 房间文件引用的桌子外观网格未随仓库提供；桌子视觉可能不完整 |
| 找不到 `ros2 control` | 该命令行扩展是可选依赖；本项目使用 `controller_manager/spawner` 加载底盘 |
| 巡逻一直等待语音服务 | 检查两个巡逻包是否编译、`espeakng` 是否安装、`speaker` 是否运行 |
| 提示拍照完成但没有图片 | 检查相机话题、目录是否存在、路径末尾 `/` 和写入权限 |
| 示例程序访问反馈字段时报 `NoneType` | 示例直接读取反馈字段；可先使用第 3 节的 Action 命令或自动检查脚本验证导航 |
| 关闭时 Nav2 容器未及时退出 | 组合节点关闭超时时，launch 会继续发送终止信号；等待启动终端结束后再重开 |

## 10. 项目结构与入口

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
