#!/usr/bin/env bash
# Run in a clean Humble environment even when the calling shell uses Foxy.
set -eo pipefail
project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
patrol_env="${PATROL_CONDA_PREFIX:-/var/tmp/qiwang/conda/envs/ros2_patrol}"
conda_root="${PATROL_CONDA_ROOT:-/home/qiwang/miniconda3}"
if [[ ! -f "$patrol_env/conda-meta/history" ]]; then
    echo "Missing environment: $patrol_env (see environment.navigation.yml)" >&2
    exit 1
fi
unset AMENT_PREFIX_PATH CMAKE_PREFIX_PATH COLCON_PREFIX_PATH PYTHONPATH
unset ROS_DISTRO ROS_VERSION ROS_PYTHON_VERSION LD_LIBRARY_PATH
unset GAZEBO_PLUGIN_PATH GAZEBO_MODEL_PATH GAZEBO_RESOURCE_PATH
source "$conda_root/etc/profile.d/conda.sh"
conda activate "$patrol_env"
export ROS_LOG_DIR="$project_dir/log/ros"
export GAZEBO_MODEL_DATABASE_URI=""
cd "$project_dir"
task="${1:-demo}"
if [[ $# -gt 0 ]]; then shift; fi
if [[ "$task" == build ]]; then
    exec colcon build --base-paths fishbot_description fishbot_navigation2 fishbot_application \
        --symlink-install --cmake-args -DBUILD_TESTING=OFF \
        -DCMAKE_POLICY_VERSION_MINIMUM=3.5 "$@"
fi
if [[ ! -f install/setup.bash ]]; then
    echo "Build first: bash scripts/navigation.sh build" >&2
    exit 1
fi
source install/setup.bash
case "$task" in
    demo) exec ros2 launch fishbot_navigation2 simulation.launch.py "$@" ;;
    sim) exec ros2 launch fishbot_description gazebo_sim.launch.py "$@" ;;
    nav) exec ros2 launch fishbot_navigation2 navigation2.launch.py "$@" ;;
    check) exec python scripts/check_navigation.py "$@" ;;
    *) exec "$task" "$@" ;;
esac
