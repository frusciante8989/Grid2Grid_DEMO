from evasdk import Eva
from evaUtilities import EvaGrids
from config.config_manager import load_use_case_config


if __name__ == "__main__":
    # Load use-case parameters
    config = load_use_case_config()

    # Connection to robot
    host = config['EVA']['comm']['host']
    token = config['EVA']['comm']['token']
    eva = Eva(host, token)

    # Compute grid points and robot joints
    eva_box = EvaGrids(eva, config, show_plot=True)
    joints = eva_box.get_grid_points(config['grids']['names'])

    # Go home before starting
    with eva.lock():
        eva.control_go_to(config['EVA']['home'])

    while True:
        for counter in range(len(joints[(config['grids']['names'][0])]['pick'])):
            joints_home = config['EVA']['home']
            joints_pick = joints[config['grids']['names'][0]]['pick'][counter]
            joints_drop = joints[config['grids']['names'][1]]['pick'][counter]
            joints_pick_hover = joints[config['grids']['names'][0]]['hover'][counter]
            joints_drop_hover = joints[config['grids']['names'][1]]['hover'][counter]

            # USER DEFINED WAY-POINTS
            joints_operation_A = [1.0819689, -0.38178113, -1.4469715, 0.0018216578, -0.9544528, -0.45301753]   # near drop-off
            joints_operation_B = [1.1585743, -0.87851846, -0.90641856, 0.0013422741, -1.3712289, 1.1612589]  # above drop-off
            joints_operation_C = [1.1583827, -0.894434, -0.94083834, 0.001054644, -1.3176339, 1.1613548]  # drop-off

            tool_path_grid_to_grid = {
                "metadata": {
                    "version": 2,
                    "default_max_speed": 0.9,
                    "next_label_id": 9,
                    "payload": config['EVA']['end_effector']['payload'],
                    "analog_modes": {"i0": "voltage", "i1": "voltage", "o0": "voltage", "o1": "voltage"}
                    },
                "waypoints": [
                    {"label_id": 1, "joints": joints_home},
                    {"label_id": 2, "joints": joints_pick_hover},
                    {"label_id": 3, "joints": joints_pick},
                    {"label_id": 4, "joints": joints_operation_A},
                    {"label_id": 5, "joints": joints_drop_hover},
                    {"label_id": 6, "joints": joints_drop},
                    {"label_id": 7, "joints": joints_operation_B},
                    {"label_id": 8, "joints": joints_operation_C},
                ],
                "timeline": [
                    {"type": "home", "waypoint_id": 0},

                    # Pick up part
                    {"type": "trajectory", "trajectory": "joint_space", "waypoint_id": 1},
                    {"type": "output-set", "io": {"location": "base", "type": "digital", "index": 0}, "value": True},
                    {"type": "output-set", "io": {"location": "base", "type": "digital", "index": 1}, "value": True},
                    {"type": "trajectory", "trajectory": "joint_space", "time": 2, "waypoint_id": 2},
                    {"type": "wait", "condition": {"type": "time", "duration": 0.5}},
                    {"type": "trajectory", "trajectory": "joint_space", "waypoint_id": 1},

                    # Move to chuck
                    {"type": "trajectory", "trajectory": "joint_space", "waypoint_id": 0},
                    {"type": "output-set", "io": {"location": "base", "type": "digital", "index": 0}, "value": False},
                    {"type": "output-set", "io": {"location": "base", "type": "digital", "index": 1}, "value": False},

                    # Move to drop-off tray
                    {"type": "trajectory", "trajectory": "joint_space", "waypoint_id": 3},
                    {"type": "trajectory", "trajectory": "joint_space", "waypoint_id": 0},
                    {"type": "trajectory", "trajectory": "joint_space", "waypoint_id": 4},
                    {"type": "trajectory", "trajectory": "joint_space", "waypoint_id": 5},

                    # Release part to drop-off tray
                    {"type": "output-set", "io": {"location": "base", "type": "digital", "index": 2}, "value": True},
                    {"type": "trajectory", "trajectory": "joint_space", "waypoint_id": 4},
                    {"type": "trajectory", "trajectory": "joint_space", "waypoint_id": 0},
                    {"type": "output-set", "io": {"location": "base", "type": "digital", "index": 2}, "value": False},
                ]
            }

            with eva.lock():
                print(f'Counter is {counter}')
                eva.control_wait_for_ready()
                eva.toolpaths_use(tool_path_grid_to_grid)
                eva.control_run(loop=1, mode="automatic")
