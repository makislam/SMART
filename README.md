# 6-Axis Robotic Arm URDF Visualization

This project contains a URDF model of a 6-axis robotic arm and a Python script to visualize it using PyBullet.

## Structure

- `robot.urdf` - URDF definition of the 6-axis robotic arm
- `visualization.py` - Python script to visualize the robot
- `requirements.txt` - Python dependencies

## Robot Description

The 6-axis arm consists of:
- **Base Link**: Fixed gray cylinder base
- **Joint 1**: Revolute joint (Z-axis rotation) - Base rotation
- **Joint 2**: Revolute joint (Y-axis rotation) - Shoulder pitch
- **Joint 3**: Revolute joint (Y-axis rotation) - Elbow pitch
- **Joint 4**: Revolute joint (Z-axis rotation) - Wrist roll
- **Joint 5**: Revolute joint (Y-axis rotation) - Wrist pitch
- **Joint 6**: Revolute joint (Z-axis rotation) - Wrist yaw

Total arm reach: approximately 1.5 meters

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Interactive Mode (Default)
Run the visualization with interactive sliders to control each joint:
```bash
python visualization.py
```

This will open a PyBullet GUI window with sliders on the right side. Use the sliders to control each joint individually.

### Animated Demo Mode
Run an automated animation:
```bash
python visualization.py --demo
```

This will show the robot performing a continuous sinusoidal motion across all joints.

## Controls

- **Mouse**: 
  - Left click + drag: Rotate camera
  - Right click + drag: Pan camera
  - Scroll wheel: Zoom in/out
- **Sliders**: Control individual joint angles (interactive mode only)
- **Ctrl+C**: Exit the simulation

## URDF Details

The URDF includes:
- Visual geometry (colored links)
- Collision geometry
- Inertial properties (mass and inertia tensors)
- Joint limits and dynamics
- Material colors for easy identification

## Customization

You can modify:
- `robot.urdf`: Change link dimensions, colors, joint limits, or add new components
- `visualization.py`: Adjust camera settings, animation patterns, or add new features

## Requirements

- Python 3.7+
- PyBullet 3.2.5+
- NumPy 1.21.0+

## Troubleshooting

If you encounter issues:
1. Ensure PyBullet is properly installed: `pip install --upgrade pybullet`
2. Check that `robot.urdf` is in the same directory as `visualization.py`
3. For Windows users, make sure you have Visual C++ redistributables installed
