"""
URDF Robot Visualization using Plotly
Interactive 3D visualization of a 6-axis robotic arm with sliders
Opens in your web browser with smooth animations
"""

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import xml.etree.ElementTree as ET

class PlotlyURDFVisualizer:
    def __init__(self, urdf_file):
        self.urdf_file = urdf_file
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
    
    def create_robot_traces(self, joint_angles):
        """Create all traces for the robot"""
        traces = []
        transforms = self.forward_kinematics(joint_angles)
        
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
                elif visual['type'] == 'box':
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
            name='Joints'
        ))
        
        return traces
    
    def visualize(self):
        """Create interactive Plotly visualization"""
        # Initial joint angles
        joint_angles = [0.0] * len(self.joints)
        
        # Create figure
        fig = go.Figure()
        
        # Add initial robot traces
        for trace in self.create_robot_traces(joint_angles):
            fig.add_trace(trace)
        
        # Create sliders
        steps = []
        n_steps = 50  # Number of steps for each joint
        
        # For demonstration, we'll create an animation that moves all joints
        for step in range(n_steps):
            t = step / (n_steps - 1)
            
            # Create sinusoidal motion for each joint
            animated_angles = []
            for i, joint in enumerate(self.joints):
                lower = joint['limits']['lower']
                upper = joint['limits']['upper']
                range_val = upper - lower
                center = (upper + lower) / 2
                
                # Different phase for each joint
                phase = (i / len(self.joints)) * 2 * np.pi
                angle = center + (range_val / 3) * np.sin(2 * np.pi * t + phase)
                animated_angles.append(angle)
            
            # Create traces for this step
            traces = self.create_robot_traces(animated_angles)
            
            step_data = {
                'label': f'Step {step}',
                'method': 'animate',
                'args': [
                    [f'frame{step}'],
                    {
                        'frame': {'duration': 50, 'redraw': True},
                        'mode': 'immediate',
                        'transition': {'duration': 50}
                    }
                ]
            }
            steps.append(step_data)
        
        # Create frames for animation
        frames = []
        for step in range(n_steps):
            t = step / (n_steps - 1)
            
            animated_angles = []
            for i, joint in enumerate(self.joints):
                lower = joint['limits']['lower']
                upper = joint['limits']['upper']
                range_val = upper - lower
                center = (upper + lower) / 2
                phase = (i / len(self.joints)) * 2 * np.pi
                angle = center + (range_val / 3) * np.sin(2 * np.pi * t + phase)
                animated_angles.append(angle)
            
            frame = go.Frame(
                data=self.create_robot_traces(animated_angles),
                name=f'frame{step}'
            )
            frames.append(frame)
        
        fig.frames = frames
        
        # Update layout
        fig.update_layout(
            title={
                'text': '6-Axis Robotic Arm - Interactive 3D Visualization',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20}
            },
            scene=dict(
                xaxis=dict(range=[-1, 1], title='X'),
                yaxis=dict(range=[-1, 1], title='Y'),
                zaxis=dict(range=[0, 2], title='Z'),
                aspectmode='manual',
                aspectratio=dict(x=1, y=1, z=1),
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.2),
                    center=dict(x=0, y=0, z=0.5)
                )
            ),
            showlegend=False,
            updatemenus=[
                {
                    'type': 'buttons',
                    'showactive': False,
                    'buttons': [
                        {
                            'label': '▶ Play Animation',
                            'method': 'animate',
                            'args': [
                                None,
                                {
                                    'frame': {'duration': 50, 'redraw': True},
                                    'fromcurrent': True,
                                    'transition': {'duration': 50}
                                }
                            ]
                        },
                        {
                            'label': '⏸ Pause',
                            'method': 'animate',
                            'args': [
                                [None],
                                {
                                    'frame': {'duration': 0, 'redraw': False},
                                    'mode': 'immediate',
                                    'transition': {'duration': 0}
                                }
                            ]
                        }
                    ],
                    'x': 0.1,
                    'y': 0.0,
                    'xanchor': 'left',
                    'yanchor': 'bottom'
                }
            ],
            margin=dict(l=0, r=0, b=0, t=50)
        )
        
        # Show in browser
        fig.show()
        
        print("\n" + "="*60)
        print("Interactive 3D Robot Arm Visualization")
        print("="*60)
        print("\nControls:")
        print("  • Click '▶ Play Animation' to see the robot move")
        print("  • Use mouse to rotate, zoom, and pan the view")
        print("  • Left click + drag: Rotate")
        print("  • Right click + drag: Pan")
        print("  • Scroll wheel: Zoom in/out")
        print("\nThe visualization is now open in your browser!")
        print("="*60 + "\n")

def main():
    visualizer = PlotlyURDFVisualizer('robot.urdf')
    visualizer.visualize()

if __name__ == "__main__":
    main()
