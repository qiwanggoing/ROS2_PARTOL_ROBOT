# ROS 2 Patrol Robot Simulation

基于 ROS 2 的移动机器人巡逻仿真项目，支持自主导航、多点巡逻、语音播报和到点拍照。

<p align="center">
  <img src="docs/images/gazebo_simulation.jpg" width="48%" alt="Gazebo 机器人仿真">
  <img src="docs/images/navigation_rviz.jpg" width="48%" alt="RViz 导航效果">
</p>

## 功能

- **自主导航**：定位、路径规划与避障，前往指定目标。
- **地图构建**：使用激光雷达与 SLAM Toolbox 建立地图。
- **多点巡逻**：按预设路点依次导航，支持循环巡逻。
- **语音播报**：播报任务进度和到达信息。
- **到点拍照**：在巡逻点采集并保存相机图像。
- **仿真可视化**：通过 Gazebo 和 RViz 查看运动、地图、激光与路径。

循环巡逻、语音与拍照需安装扩展依赖，完整流程待联调。

## 演示视频

[![机器人导航演示](docs/images/navigation_preview.gif)](Navigation.mp4)

[观看完整视频](Navigation.mp4)

## 首次使用

先准备 Conda 和构建工具，详见 [安装说明](docs/USAGE.md)。然后下载项目并创建环境：

```bash
git clone https://github.com/qiwanggoing/ROS2_PARTOL_ROBOT.git
cd ROS2_PARTOL_ROBOT
conda env create --file environment.navigation.yml
conda activate ros2_patrol
```

按 [安装说明](docs/USAGE.md) 将 `scripts/navigation.sh` 顶部的 `conda_root` 和 `patrol_env` 改为自己的安装路径，然后启动：

```bash
bash scripts/navigation.sh build
bash scripts/navigation.sh demo
```

在 RViz 中用 **2D Pose Estimate** 设置初始位置，再用 **Nav2 Goal** 选择目标。

详细操作与环境配置见 [使用文档](docs/USAGE.md)。

项目基于 [fishros / FishBot](https://github.com/fishros) 教育材料扩展。
