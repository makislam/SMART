"""
Test preset configurations for the robot arm
Simple script to visualize specific joint angle configurations
"""

import numpy as np
from visualization import PlotlyURDFVisualizer
import sys

# Define preset configurations
configs = {
    'home': {
        'name': 'Home Position',
        'angles': [0, 0, 0, 0, 0, 0],
        'description': 'All joints at zero (home position)'
    },
    'config1': {
        'name': 'Configuration 1',
        'angles': [0, -np.pi/2, -np.pi/3, -np.pi/4, -np.pi/2, 0],
        'description': 'C1=0, C2=-π/2, C3=-π/3, C4=-π/4, C5=-π/2, C6=0'
    },
    'vertical': {
        'name': 'Vertical Reach',
        'angles': [0, -np.pi/2, 0, 0, 0, 0],
        'description': 'Arm pointing straight up'
    },
    'forward': {
        'name': 'Forward Reach',
        'angles': [0, -np.pi/4, -np.pi/4, -np.pi/4, 0, 0],
        'description': 'Arm reaching forward'
    },
    'side': {
        'name': 'Side Reach',
        'angles': [np.pi/2, -np.pi/4, -np.pi/4, -np.pi/4, 0, 0],
        'description': 'Arm reaching to the side'
    }
}

def visualize_config(config_name, show_inertia=False):
    """Visualize a specific configuration"""
    if config_name not in configs:
        print(f"Error: Configuration '{config_name}' not found!")
        print(f"Available configurations: {', '.join(configs.keys())}")
        return
    
    config = configs[config_name]
    angles = config['angles']
    
    print("\n" + "="*60)
    print(f"Visualizing: {config['name']}")
    print("="*60)
    print(f"\nDescription: {config['description']}")
    print("\nJoint Angles:")
    for i, angle in enumerate(angles):
        print(f"  C{i+1} (Joint {i+1}): {angle:.4f} rad = {np.degrees(angle):.2f}°")
    
    # Create visualizer
    visualizer = PlotlyURDFVisualizer('URDF/mycobotpro320.urdf', show_inertia=show_inertia)
    
    # Create figure with the specified angles
    import plotly.graph_objects as go
    
    traces = visualizer.create_robot_traces(angles)
    fig = go.Figure(data=traces)
    
    fig.update_layout(
        title=f"{config['name']} - Joint Configuration",
        scene=dict(
            xaxis=dict(range=[-0.5, 0.5], title='X (m)'),
            yaxis=dict(range=[-0.5, 0.5], title='Y (m)'),
            zaxis=dict(range=[0, 0.7], title='Z (m)'),
            aspectmode='manual',
            aspectratio=dict(x=1, y=1, z=1.2),
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.2),
                center=dict(x=0, y=0, z=0.3)
            )
        ),
        showlegend=False,
        margin=dict(l=0, r=0, b=0, t=50),
        height=800
    )
    
    fig.show()
    print("\nVisualization opened in browser!")
    print("="*60 + "\n")

def list_configs():
    """List all available configurations"""
    print("\n" + "="*60)
    print("Available Preset Configurations")
    print("="*60)
    for key, config in configs.items():
        print(f"\n{key}:")
        print(f"  Name: {config['name']}")
        print(f"  Description: {config['description']}")
        angles_str = [f"{a:.3f}" for a in config['angles']]
        print(f"  Angles: [{', '.join(angles_str)}]")
    print("\n" + "="*60 + "\n")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Visualize preset robot arm configurations',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test_configs.py --list                 # List all configurations
  python test_configs.py home                   # Visualize home position
  python test_configs.py config1                # Visualize config 1
  python test_configs.py forward --inertia      # Show with inertia visualization
        """
    )
    
    parser.add_argument('config', nargs='?', default=None,
                       help='Configuration name to visualize')
    parser.add_argument('--list', '-l', action='store_true',
                       help='List all available configurations')
    parser.add_argument('--inertia', '-i', action='store_true',
                       help='Show full visualization with inertia/mass')
    
    args = parser.parse_args()
    
    if args.list or args.config is None:
        list_configs()
        if not args.list:
            print("Usage: python test_configs.py <config_name>")
            print("Use --list to see all available configurations\n")
    else:
        visualize_config(args.config, show_inertia=args.inertia)
