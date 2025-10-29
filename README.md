# myCobot 320 Pi - 6-Axis Robotic Arm Visualization

This project contains a URDF model of the myCobot 320 Pi (Baby Elephant Cooperative Robotic Arm) and an interactive Python script to visualize it using Plotly.

## Robot Specifications

- **Model**: myCobot 320 Pi
- **Degrees of Freedom**: 6
- **Working Radius**: 350mm
- **Payload**: 1kg
- **Positioning Precision**: ±0.5mm
- **Weight**: 3.3kg
- **Power Input**: 24V, 9.2A
- **Operating Temperature**: 0°~45°C
- **Service Life**: 2000h

### Joint Range of Motion
| Joint | Angle Range |
|-------|-------------|
| J1    | -165° to +165° |
| J2    | -165° to +165° |
| J3    | -165° to +165° |
| J4    | -165° to +165° |
| J5    | -165° to +165° |
| J6    | -175° to +175° |

## Structure

- `robot.urdf` - URDF definition with accurate myCobot 320 Pi dimensions
- `visualization.py` - Interactive Plotly-based 3D visualization script
- `requirements.txt` - Python dependencies

## Robot Description

The myCobot 320 Pi consists of:
- **Base Link**: 179.90mm height (gray)
- **Joint 1**: Revolute joint (Z-axis rotation) - Base rotation
- **Link 1**: 135.00mm segment (white)
- **Joint 2**: Revolute joint (Y-axis rotation) - Shoulder pitch
- **Link 2**: 100.00mm segment (light blue)
- **Joint 3**: Revolute joint (Y-axis rotation) - Elbow pitch
- **Link 3**: 95.00mm segment (white)
- **Joint 4**: Revolute joint (Z-axis rotation) - Wrist roll
- **Link 4**: 88.78mm segment (light blue)
- **Joint 5**: Revolute joint (Y-axis rotation) - Wrist pitch
- **Link 5**: 65.50mm segment (white)
- **Joint 6**: Revolute joint (Z-axis rotation) - Wrist yaw
- **Link 6**: End effector flange (light blue)

**Total reach**: 350mm working radius

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Visualization

Run the basic skeleton visualization:
```bash
python visualization.py
```

Show full visualization with inertia/mass:
```bash
python visualization.py --inertia
```

### Interactive Joint Control (Recommended!)

For real-time control of all 6 joints with sliders:
```bash
python interactive_control.py
```

This will start a local web server at `http://127.0.0.1:8050/` with:
- **6 Individual Joint Sliders**: Control each joint angle in real-time (C1-C6)
- **Preset Configurations**: Quick access to common poses
- **Live Angle Display**: See current angles in both radians and degrees
- **Interactive 3D View**: Rotate, pan, and zoom while controlling joints

### Test Preset Configurations

Quickly visualize specific configurations:
```bash
python test_configs.py --list              # List all available presets
python test_configs.py home                # Home position (all zeros)
python test_configs.py config1             # Configuration 1
python test_configs.py forward --inertia   # Forward reach with inertia view
```

Available presets:
- `home`: All joints at zero (home position)
- `config1`: C1=0, C2=-π/2, C3=-π/3, C4=-π/4, C5=-π/2, C6=0
- `vertical`: Arm pointing straight up
- `forward`: Arm reaching forward
- `side`: Arm reaching to the side

## Controls

### Interactive Control App
- **Joint Sliders**: Drag each slider to control joint angles (C1-C6)
- **Preset Buttons**: Click to jump to predefined configurations
- **3D View**: 
  - Left click + drag: Rotate camera
  - Right click + drag: Pan camera
  - Scroll wheel: Zoom in/out

### Basic Visualization
- **Mouse Controls**: 
  - Left click + drag: Rotate camera
  - Right click + drag: Pan camera
  - Scroll wheel: Zoom in/out

## Requirements

- Python 3.7+
- Plotly 6.0+
- NumPy 1.21.0+
- Dash 2.14.0+ (for interactive control)

## Features

- 🎮 **Real-time Joint Control**: Individual sliders for all 6 joints with live updates
- 🎨 Modern browser-based 3D visualization using Plotly
- � Preset configurations for common robot poses
- 🔧 Skeleton mode with cylindrical links and joint connectors
- 💡 Full inertia visualization mode (optional)
- 🖱️ Interactive camera controls (rotate, pan, zoom)
- 📊 Live angle display in radians and degrees
- 🚀 No compilation required - pure Python!
- 🌐 Web-based interface for easy control

## Joint Angle Control

The robot uses 6 control parameters (C1-C6) corresponding to joints (J1-J6):

```
J = [J₁, J₂, J₃, J₄, J₅, J₆]
```

Where:
- **J₁ = C₁**: Base rotation (around Z-axis)
- **J₂ = C₂ - C₃**: Shoulder pitch (around Y-axis)
- **J₃ = 2·C₃**: Elbow pitch (around Y-axis)
- **J₄ = C₄ - (C₂ + C₃)**: Wrist roll (around Z-axis)
- **J₅ = -C₅**: Wrist pitch (around Y-axis)
- **J₆ = C₆**: Wrist yaw (around Z-axis)

Example configurations:
```python
# Home position
C = [0, 0, 0, 0, 0, 0]

# Configuration 1
C = [0, -π/2, -π/3, -π/4, -π/2, 0]
```

## Customization

You can modify:
- `URDF/mycobotpro320.urdf`: Change link dimensions, colors, joint limits, or add new components
- `visualization.py`: Adjust rendering, colors, or add new features
- `interactive_control.py`: Add custom presets or modify the control interface
- `test_configs.py`: Add your own preset configurations
