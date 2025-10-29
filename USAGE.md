# Quick Start Guide - myCobot 320 Pi Visualization

## 🚀 Three Ways to Visualize Your Robot

### 1. Interactive Control Panel (RECOMMENDED) 🎮

**Best for**: Real-time joint control with sliders

```bash
python interactive_control.py
```

Opens at: `http://127.0.0.1:8050/`

**Features:**
- 6 individual sliders (C1-C6) for each joint
- Real-time 3D updates as you move sliders
- Preset configuration buttons (Home, Config1, Vertical, Forward, Side)
- Live angle display in radians and degrees
- Interactive 3D camera controls

**Controls:**
- Drag sliders to adjust joint angles
- Click preset buttons for quick configurations
- Use mouse to rotate/pan/zoom the 3D view

---

### 2. Preset Configuration Viewer 🎯

**Best for**: Quickly viewing specific robot poses

```bash
# List all available presets
python test_configs.py --list

# Visualize a specific configuration
python test_configs.py home
python test_configs.py config1
python test_configs.py forward
```

**Available Presets:**
- `home` - All joints at zero
- `config1` - C₁=0, C₂=-π/2, C₃=-π/3, C₄=-π/4, C₅=-π/2, C₆=0
- `vertical` - Arm pointing up
- `forward` - Arm reaching forward
- `side` - Arm reaching to the side

---

### 3. Basic Visualization 🔍

**Best for**: Simple viewing or screenshots

```bash
# Skeleton view (default)
python visualization.py

# Full view with link geometry
python visualization.py --inertia
```

**Visualization Modes:**
- **Skeleton**: Clean cylindrical links with joint connectors (default)
- **Inertia**: Full 3D mesh visualization showing link geometry

---

## 📐 Understanding Joint Angles

The robot uses 6 control parameters (C1-C6):

| Parameter | Joint | Description | Axis | Range |
|-----------|-------|-------------|------|-------|
| C₁ | J₁ | Base rotation | Z | -165° to +165° |
| C₂ | J₂ | Shoulder pitch | Y | -165° to +165° |
| C₃ | J₃ | Elbow pitch | Y | -165° to +165° |
| C₄ | J₄ | Wrist roll | Z | -165° to +165° |
| C₅ | J₅ | Wrist pitch | Y | -165° to +165° |
| C₆ | J₆ | Wrist yaw | Z | -175° to +175° |

### Example Configurations

**Home Position (Zero Position):**
```
C = [0, 0, 0, 0, 0, 0]
```

**Configuration 1 (Example from specs):**
```
C = [0, -π/2, -π/3, -π/4, -π/2, 0]
  = [0, -90°, -60°, -45°, -90°, 0]
```

---

## 🖱️ Mouse Controls

All visualization modes support:
- **Left click + drag**: Rotate camera around robot
- **Right click + drag**: Pan camera (move view left/right/up/down)
- **Scroll wheel**: Zoom in/out

---

## 💡 Tips

1. **For learning**: Use `interactive_control.py` to understand how each joint affects the arm position

2. **For presentations**: Use `test_configs.py` to show specific poses quickly

3. **For development**: Use `visualization.py --inertia` to see the full link geometry

4. **Custom configurations**: Edit `test_configs.py` to add your own preset poses

---

## 🐛 Troubleshooting

**Port already in use (interactive_control.py)**
```bash
# The server is already running. Check http://127.0.0.1:8050/
# Or kill the process and restart
```

**Import errors**
```bash
pip install -r requirements.txt
```

**Browser doesn't open automatically**
- Manually navigate to: `http://127.0.0.1:8050/` (for interactive control)
- Or check the terminal output for the URL

---

## 📚 Next Steps

- Read `README.md` for full documentation
- Modify `URDF/mycobotpro320.urdf` to customize the robot
- Edit `interactive_control.py` to add custom presets
- Check `test_configs.py` for configuration examples
