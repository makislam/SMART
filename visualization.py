"""
URDF Robot Visualization using Plotly
Interactive 3D visualization of a 6-axis robotic arm with sliders
Opens in your web browser with smooth animations
"""

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import xml.etree.ElementTree as ET
import argparse

class PlotlyURDFVisualizer:
    def __init__(self, urdf_file, show_inertia=False):
        self.urdf_file = urdf_file
        self.show_inertia = show_inertia
        self.joints = []
        self.links = []
        self.colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
        self.parse_urdf()
        
    def parse_urdf(self):
        """Parse the URDF file to extract joint and link information"""
        tree = ET.parse(self.urdf_file)
        root = tree.getroot()
        
        # Extract joints
        for joint in root.findall('joint'):
            joint_info = {
                'name': joint.get('name'),
                'type': joint.get('type'),
                'parent': joint.find('parent').get('link'),
                'child': joint.find('child').get('link'),
                'origin': self._parse_origin(joint.find('origin')),
                'axis': self._parse_axis(joint.find('axis')),
                'limits': self._parse_limits(joint.find('limit'))
            }
            self.joints.append(joint_info)
        
        # Extract links
        for link in root.findall('link'):
            link_info = {
                'name': link.get('name'),
                'visual': self._parse_visual(link.find('visual'))
            }
            self.links.append(link_info)
    
    def _parse_origin(self, origin):
        if origin is None:
            return {'xyz': [0, 0, 0], 'rpy': [0, 0, 0]}
        xyz = [float(x) for x in origin.get('xyz', '0 0 0').split()]
        rpy = [float(x) for x in origin.get('rpy', '0 0 0').split()]
        return {'xyz': xyz, 'rpy': rpy}
    
    def _parse_axis(self, axis):
        if axis is None:
            return [0, 0, 1]
        return [float(x) for x in axis.get('xyz', '0 0 1').split()]
    
    def _parse_limits(self, limit):
        if limit is None:
            return {'lower': -np.pi, 'upper': np.pi}
        return {
            'lower': float(limit.get('lower', -np.pi)),
            'upper': float(limit.get('upper', np.pi))
        }
    
    def _parse_visual(self, visual):
        if visual is None:
            return None
        
        geom = visual.find('geometry')
        if geom is None:
            return None
            
        origin = self._parse_origin(visual.find('origin'))
        
        visual_info = {'origin': origin}
        
        if geom.find('cylinder') is not None:
            cyl = geom.find('cylinder')
            visual_info['type'] = 'cylinder'
            visual_info['radius'] = float(cyl.get('radius'))
            visual_info['length'] = float(cyl.get('length'))
        elif geom.find('box') is not None:
            box = geom.find('box')
            visual_info['type'] = 'box'
            visual_info['size'] = [float(x) for x in box.get('size').split()]
        elif geom.find('mesh') is not None:
            mesh = geom.find('mesh')
            visual_info['type'] = 'mesh'
            visual_info['filename'] = mesh.get('filename')
            # For mesh files, we'll create a simple box representation
            # You can enhance this later to load actual mesh files
            visual_info['size'] = [0.05, 0.05, 0.05]  # Default size for placeholder
        else:
            return None
        
        return visual_info
    
    def rotation_matrix(self, roll, pitch, yaw):
        """Create a rotation matrix from roll, pitch, yaw angles"""
        R_x = np.array([[1, 0, 0],
                        [0, np.cos(roll), -np.sin(roll)],
                        [0, np.sin(roll), np.cos(roll)]])
        
        R_y = np.array([[np.cos(pitch), 0, np.sin(pitch)],
                        [0, 1, 0],
                        [-np.sin(pitch), 0, np.cos(pitch)]])
        
        R_z = np.array([[np.cos(yaw), -np.sin(yaw), 0],
                        [np.sin(yaw), np.cos(yaw), 0],
                        [0, 0, 1]])
        
        return R_z @ R_y @ R_x
    
    def forward_kinematics(self, joint_angles):
        """Calculate the forward kinematics for given joint angles"""
        transforms = []
        current_transform = np.eye(4)
        
        for i, joint in enumerate(self.joints):
            # Joint origin transform
            origin = joint['origin']
            rpy = origin['rpy']
            xyz = origin['xyz']
            
            T_joint = np.eye(4)
            T_joint[:3, :3] = self.rotation_matrix(rpy[0], rpy[1], rpy[2])
            T_joint[:3, 3] = xyz
            
            # Apply joint rotation
            angle = joint_angles[i]
            axis = joint['axis']
            
            if abs(axis[2]) > 0.5:  # Z-axis rotation
                T_rotation = np.eye(4)
                T_rotation[:3, :3] = self.rotation_matrix(0, 0, angle)
            elif abs(axis[1]) > 0.5:  # Y-axis rotation
                T_rotation = np.eye(4)
                T_rotation[:3, :3] = self.rotation_matrix(0, angle, 0)
            elif abs(axis[0]) > 0.5:  # X-axis rotation
                T_rotation = np.eye(4)
                T_rotation[:3, :3] = self.rotation_matrix(angle, 0, 0)
            else:
                T_rotation = np.eye(4)
            
            current_transform = current_transform @ T_joint @ T_rotation
            transforms.append(current_transform.copy())
        
        return transforms
    
    def create_cylinder_mesh(self, radius, length, transform, color):
        """Create a cylinder mesh"""
        n_segments = 20
        theta = np.linspace(0, 2 * np.pi, n_segments)
        z = np.array([0, length])
        
        # Create cylinder points
        x = []
        y = []
        z_coords = []
        
        for zi in z:
            for t in theta:
                point = np.array([radius * np.cos(t), radius * np.sin(t), zi, 1])
                transformed = transform @ point
                x.append(transformed[0])
                y.append(transformed[1])
                z_coords.append(transformed[2])
        
        # Create faces
        i = []
        j = []
        k = []
        
        for seg in range(n_segments - 1):
            # Side faces
            i.extend([seg, seg, seg + n_segments])
            j.extend([seg + 1, seg + n_segments, seg + n_segments + 1])
            k.extend([seg + n_segments, seg + n_segments + 1, seg + 1])
        
        # Close the cylinder
        i.extend([n_segments - 1, n_segments - 1, 2 * n_segments - 1])
        j.extend([0, n_segments, n_segments])
        k.extend([n_segments, 2 * n_segments - 1, 0])
        
        # Top and bottom caps
        center_bottom = transform @ np.array([0, 0, 0, 1])
        center_top = transform @ np.array([0, 0, length, 1])
        
        x.extend([center_bottom[0], center_top[0]])
        y.extend([center_bottom[1], center_top[1]])
        z_coords.extend([center_bottom[2], center_top[2]])
        
        center_bottom_idx = len(x) - 2
        center_top_idx = len(x) - 1
        
        for seg in range(n_segments - 1):
            i.extend([center_bottom_idx, center_top_idx])
            j.extend([seg, seg + n_segments])
            k.extend([seg + 1, seg + n_segments + 1])
        
        i.extend([center_bottom_idx, center_top_idx])
        j.extend([n_segments - 1, 2 * n_segments - 1])
        k.extend([0, n_segments])
        
        return go.Mesh3d(
            x=x, y=y, z=z_coords,
            i=i, j=j, k=k,
            color=color,
            opacity=0.7,
            lighting=dict(ambient=0.5, diffuse=0.8, specular=0.5),
            lightposition=dict(x=100, y=100, z=100)
        )
    
    def create_box_mesh(self, size, transform, color):
        """Create a box mesh"""
        sx, sy, sz = size
        
        # Define box vertices
        vertices = np.array([
            [-sx/2, -sy/2, 0], [sx/2, -sy/2, 0], [sx/2, sy/2, 0], [-sx/2, sy/2, 0],
            [-sx/2, -sy/2, sz], [sx/2, -sy/2, sz], [sx/2, sy/2, sz], [-sx/2, sy/2, sz]
        ])
        
        # Transform vertices
        x, y, z = [], [], []
        for v in vertices:
            point = np.append(v, 1)
            transformed = transform @ point
            x.append(transformed[0])
            y.append(transformed[1])
            z.append(transformed[2])
        
        # Define faces
        i = [0, 0, 0, 1, 1, 4, 4, 5, 2, 2, 7, 7]
        j = [1, 2, 4, 2, 5, 5, 7, 6, 3, 6, 3, 6]
        k = [2, 3, 5, 6, 6, 1, 0, 1, 7, 7, 4, 2]
        
        return go.Mesh3d(
            x=x, y=y, z=z,
            i=i, j=j, k=k,
            color=color,
            opacity=0.7,
            lighting=dict(ambient=0.5, diffuse=0.8, specular=0.5),
            lightposition=dict(x=100, y=100, z=100)
        )
    
    def create_link_cylinder(self, start_pos, end_pos, radius, color):
        """Create a cylinder connecting two points (representing a link)"""
        # Calculate direction and length
        direction = end_pos - start_pos
        length = np.linalg.norm(direction)
        
        if length < 1e-6:  # Avoid zero-length cylinders
            return None
        
        direction = direction / length
        
        # Create cylinder along z-axis first
        n_segments = 20
        theta = np.linspace(0, 2 * np.pi, n_segments)
        z = np.array([0, length])
        
        x = []
        y = []
        z_coords = []
        
        for zi in z:
            for t in theta:
                point = np.array([radius * np.cos(t), radius * np.sin(t), zi])
                x.append(point[0])
                y.append(point[1])
                z_coords.append(point[2])
        
        # Create transformation matrix to align cylinder with link direction
        # Find rotation that maps [0, 0, 1] to direction
        z_axis = np.array([0, 0, 1])
        if np.allclose(direction, z_axis):
            rotation = np.eye(3)
        elif np.allclose(direction, -z_axis):
            rotation = np.array([[-1, 0, 0], [0, 1, 0], [0, 0, -1]])
        else:
            v = np.cross(z_axis, direction)
            s = np.linalg.norm(v)
            c = np.dot(z_axis, direction)
            vx = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
            rotation = np.eye(3) + vx + vx @ vx * ((1 - c) / (s * s))
        
        # Transform all points
        x_transformed = []
        y_transformed = []
        z_transformed = []
        
        for i in range(len(x)):
            point = np.array([x[i], y[i], z_coords[i]])
            transformed = rotation @ point + start_pos
            x_transformed.append(transformed[0])
            y_transformed.append(transformed[1])
            z_transformed.append(transformed[2])
        
        # Create faces
        i_faces = []
        j_faces = []
        k_faces = []
        
        for seg in range(n_segments - 1):
            i_faces.extend([seg, seg, seg + n_segments])
            j_faces.extend([seg + 1, seg + n_segments, seg + n_segments + 1])
            k_faces.extend([seg + n_segments, seg + n_segments + 1, seg + 1])
        
        # Close the cylinder
        i_faces.extend([n_segments - 1, n_segments - 1, 2 * n_segments - 1])
        j_faces.extend([0, n_segments, n_segments])
        k_faces.extend([n_segments, 2 * n_segments - 1, 0])
        
        # Add caps
        x_transformed.extend([start_pos[0], end_pos[0]])
        y_transformed.append(start_pos[1])
        y_transformed.append(end_pos[1])
        z_transformed.append(start_pos[2])
        z_transformed.append(end_pos[2])
        
        center_bottom_idx = len(x_transformed) - 2
        center_top_idx = len(x_transformed) - 1
        
        for seg in range(n_segments - 1):
            i_faces.extend([center_bottom_idx, center_top_idx])
            j_faces.extend([seg, seg + n_segments])
            k_faces.extend([seg + 1, seg + n_segments + 1])
        
        i_faces.extend([center_bottom_idx, center_top_idx])
        j_faces.extend([n_segments - 1, 2 * n_segments - 1])
        k_faces.extend([0, n_segments])
        
        return go.Mesh3d(
            x=x_transformed, y=y_transformed, z=z_transformed,
            i=i_faces, j=j_faces, k=k_faces,
            color=color,
            opacity=0.8,
            lighting=dict(ambient=0.5, diffuse=0.8, specular=0.5),
            lightposition=dict(x=100, y=100, z=100)
        )
    
    def create_joint_connector(self, position, size, color):
        """Create a small box at joint position to represent the joint connector"""
        s = size
        vertices = np.array([
            [-s, -s, -s], [s, -s, -s], [s, s, -s], [-s, s, -s],
            [-s, -s, s], [s, -s, s], [s, s, s], [-s, s, s]
        ])
        
        x = (vertices[:, 0] + position[0]).tolist()
        y = (vertices[:, 1] + position[1]).tolist()
        z = (vertices[:, 2] + position[2]).tolist()
        
        i = [0, 0, 0, 1, 1, 4, 4, 5, 2, 2, 7, 7]
        j = [1, 2, 4, 2, 5, 5, 7, 6, 3, 6, 3, 6]
        k = [2, 3, 5, 6, 6, 1, 0, 1, 7, 7, 4, 2]
        
        return go.Mesh3d(
            x=x, y=y, z=z,
            i=i, j=j, k=k,
            color=color,
            opacity=0.9,
            lighting=dict(ambient=0.5, diffuse=0.8, specular=0.5),
            lightposition=dict(x=100, y=100, z=100)
        )
    
    def create_robot_traces(self, joint_angles):
        """Create all traces for the robot - skeleton or full visualization"""
        traces = []
        transforms = self.forward_kinematics(joint_angles)
        
        if self.show_inertia:
            # Full visualization with cylinders and boxes (inertia visualization)
            
            # Draw base link (if it has visual)
            if self.links[0]['visual']:
                visual = self.links[0]['visual']
                T_visual = np.eye(4)
                T_visual[:3, 3] = visual['origin']['xyz']
                T_visual[:3, :3] = self.rotation_matrix(*visual['origin']['rpy'])
                
                if visual['type'] == 'cylinder':
                    traces.append(self.create_cylinder_mesh(
                        visual['radius'], visual['length'], T_visual, '#808080'
                    ))
                elif visual['type'] == 'box' or visual['type'] == 'mesh':
                    traces.append(self.create_box_mesh(
                        visual['size'], T_visual, '#808080'
                    ))
            
            # Draw other links
            for i, (link, transform) in enumerate(zip(self.links[1:], transforms)):
                if link['visual']:
                    visual = link['visual']
                    T_visual = np.eye(4)
                    T_visual[:3, 3] = visual['origin']['xyz']
                    T_visual[:3, :3] = self.rotation_matrix(*visual['origin']['rpy'])
                    
                    final_transform = transform @ T_visual
                    color = self.colors[i % len(self.colors)]
                    
                    if visual['type'] == 'cylinder':
                        traces.append(self.create_cylinder_mesh(
                            visual['radius'], visual['length'], final_transform, color
                        ))
                    elif visual['type'] == 'box' or visual['type'] == 'mesh':
                        traces.append(self.create_box_mesh(
                            visual['size'], final_transform, color
                        ))
            
            # Draw joint connections
            positions = [[0, 0, 0]]
            for transform in transforms:
                positions.append(transform[:3, 3].tolist())
            positions = np.array(positions)
            
            traces.append(go.Scatter3d(
                x=positions[:, 0],
                y=positions[:, 1],
                z=positions[:, 2],
                mode='lines+markers',
                line=dict(color='black', width=4),
                marker=dict(size=6, color='red'),
                name='Joints',
                showlegend=False
            ))
        else:
            # Skeleton visualization with cylindrical links and joint connectors
            
            # Calculate all joint positions
            positions = [[0, 0, 0]]  # Base position
            for transform in transforms:
                positions.append(transform[:3, 3].tolist())
            positions = np.array(positions)
            
            # Create cylindrical links between joints
            link_radius = 0.015  # 15mm radius for links
            link_colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F']
            
            for i in range(len(positions) - 1):
                cylinder = self.create_link_cylinder(
                    positions[i], 
                    positions[i+1], 
                    link_radius,
                    link_colors[i % len(link_colors)]
                )
                if cylinder:
                    traces.append(cylinder)
            
            # Create joint connectors (small boxes at each joint)
            joint_colors = ['#808080', '#FF8C00', '#87CEEB', '#9370DB', '#87CEEB', '#9370DB', '#4169E1']
            joint_size = 0.02  # 20mm cube for joints
            
            for i, (pos, color) in enumerate(zip(positions, joint_colors)):
                traces.append(self.create_joint_connector(pos, joint_size, color))
        
        return traces
    
    def visualize(self):
        """Create interactive Plotly visualization with individual joint control"""
        # Initial joint angles (all zeros)
        initial_angles = [0.0] * len(self.joints)
        
        # Create figure
        fig = go.Figure()
        
        # Add initial robot traces
        for trace in self.create_robot_traces(initial_angles):
            fig.add_trace(trace)
        
        # Create sliders for each joint
        sliders = []
        
        for joint_idx in range(len(self.joints)):
            joint = self.joints[joint_idx]
            lower = joint['limits']['lower']
            upper = joint['limits']['upper']
            
            # Create steps for this slider
            n_steps = 100
            steps = []
            
            for step_idx in range(n_steps):
                # Calculate angle for this step
                angle = lower + (upper - lower) * step_idx / (n_steps - 1)
                
                # Create joint angles array with this joint at the current angle
                # We'll use a naming convention to identify which joint to update
                step_label = f"{angle:.3f} rad ({np.degrees(angle):.1f}°)"
                
                steps.append({
                    'method': 'skip',  # We'll handle updates via callback
                    'label': step_label,
                    'value': angle
                })
            
            slider = {
                'active': int(n_steps / 2),  # Start at middle (near 0)
                'yanchor': 'top',
                'y': 1.0 - joint_idx * 0.08,  # Stack sliders vertically
                'xanchor': 'left',
                'x': 0.0,
                'currentvalue': {
                    'prefix': f'C{joint_idx + 1} (J{joint_idx + 1}): ',
                    'visible': True,
                    'xanchor': 'right',
                    'font': {'size': 14}
                },
                'pad': {'b': 10, 't': 10},
                'len': 0.85,
                'steps': steps
            }
            sliders.append(slider)
        
        # Update layout
        fig.update_layout(
            title={
                'text': '6-Axis Robotic Arm - Interactive Joint Control',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20}
            },
            scene=dict(
                xaxis=dict(range=[-0.25, 0.25], title='X (m)'),
                yaxis=dict(range=[-0.25, 0.25], title='Y (m)'),
                zaxis=dict(range=[0, 0.5], title='Z (m)'),
                aspectmode='manual',
                aspectratio=dict(x=1, y=1, z=1),
                camera=dict(
                    eye=dict(x=1.3, y=1.3, z=1.0),
                    center=dict(x=0, y=0, z=0.25)
                )
            ),
            showlegend=False,
            sliders=sliders,
            margin=dict(l=0, r=0, b=150, t=50),
            height=900
        )
        
        # Show in browser
        fig.show()
        
        print("\n" + "="*60)
        print("Interactive 3D Robot Arm Visualization")
        print("="*60)
        print(f"\nVisualization Mode: {'Full (with inertia/mass)' if self.show_inertia else 'Skeleton'}")
        print("\nNote: Plotly sliders in Python have limitations.")
        print("For full interactive control, please use the web app version.")
        print("\nControls:")
        print("  • Use mouse to rotate, zoom, and pan the view")
        print("  • Left click + drag: Rotate")
        print("  • Right click + drag: Pan")
        print("  • Scroll wheel: Zoom in/out")
        print("\nPreset Configurations (copy to a separate Python script):")
        print("  Config 1: C1=0, C2=-π/2, C3=-π/3, C4=-π/4, C5=-π/2, C6=0")
        print("  Config 2: C1=0, C2=0, C3=0, C4=0, C5=0, C6=0 (Home)")
        print("\nThe visualization is now open in your browser!")
        print("="*60 + "\n")

def main():
    parser = argparse.ArgumentParser(
        description='Visualize URDF robot model in 3D',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python visualization.py                    # Skeleton view (default)
  python visualization.py --inertia          # Full view with inertia/mass
  python visualization.py -i                 # Short form
        """
    )
    parser.add_argument(
        '--inertia', '-i',
        action='store_true',
        help='Show full visualization with inertia and mass (cylinders/boxes)'
    )
    
    args = parser.parse_args()
    
    visualizer = PlotlyURDFVisualizer('URDF/mycobotpro320.urdf', show_inertia=args.inertia)
    visualizer.visualize()

if __name__ == "__main__":
    main()
