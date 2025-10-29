"""
URDF Robot Visualization using Matplotlib
Visualizes a 6-axis robotic arm with interactive sliders
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import xml.etree.ElementTree as ET

class URDFVisualizer:
    def __init__(self, urdf_file):
        self.urdf_file = urdf_file
        self.joints = []
        self.links = []
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
    
    def draw_cylinder(self, ax, radius, length, transform, color='b'):
        """Draw a cylinder"""
        z = np.linspace(0, length, 20)
        theta = np.linspace(0, 2 * np.pi, 20)
        theta_grid, z_grid = np.meshgrid(theta, z)
        x_grid = radius * np.cos(theta_grid)
        y_grid = radius * np.sin(theta_grid)
        
        # Transform points
        points = np.stack([x_grid.flatten(), y_grid.flatten(), z_grid.flatten(), np.ones(x_grid.size)])
        transformed = transform @ points
        
        x_t = transformed[0, :].reshape(x_grid.shape)
        y_t = transformed[1, :].reshape(y_grid.shape)
        z_t = transformed[2, :].reshape(z_grid.shape)
        
        ax.plot_surface(x_t, y_t, z_t, color=color, alpha=0.6)
    
    def draw_box(self, ax, size, transform, color='r'):
        """Draw a box"""
        sx, sy, sz = size
        
        # Define box vertices
        vertices = np.array([
            [-sx/2, -sy/2, 0], [sx/2, -sy/2, 0], [sx/2, sy/2, 0], [-sx/2, sy/2, 0],
            [-sx/2, -sy/2, sz], [sx/2, -sy/2, sz], [sx/2, sy/2, sz], [-sx/2, sy/2, sz]
        ])
        
        # Transform vertices
        vertices_h = np.hstack([vertices, np.ones((8, 1))]).T
        transformed = transform @ vertices_h
        vertices_t = transformed[:3, :].T
        
        # Define box faces
        faces = [
            [vertices_t[0], vertices_t[1], vertices_t[5], vertices_t[4]],
            [vertices_t[7], vertices_t[6], vertices_t[2], vertices_t[3]],
            [vertices_t[0], vertices_t[3], vertices_t[7], vertices_t[4]],
            [vertices_t[1], vertices_t[2], vertices_t[6], vertices_t[5]],
            [vertices_t[0], vertices_t[1], vertices_t[2], vertices_t[3]],
            [vertices_t[4], vertices_t[5], vertices_t[6], vertices_t[7]]
        ]
        
        ax.add_collection3d(Poly3DCollection(faces, facecolors=color, linewidths=1, edgecolors='k', alpha=0.6))
    
    def visualize(self):
        """Create interactive visualization"""
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        # Initial joint angles
        joint_angles = [0.0] * len(self.joints)
        
        # Create sliders
        slider_axes = []
        sliders = []
        slider_height = 0.03
        slider_bottom = 0.05
        
        for i, joint in enumerate(self.joints):
            ax_slider = plt.axes([0.15, slider_bottom + i * (slider_height + 0.01), 0.3, slider_height])
            slider = Slider(
                ax_slider, 
                joint['name'],
                joint['limits']['lower'],
                joint['limits']['upper'],
                valinit=0,
                valstep=0.01
            )
            sliders.append(slider)
            slider_axes.append(ax_slider)
        
        def update(val):
            # Get current joint angles from sliders
            for i, slider in enumerate(sliders):
                joint_angles[i] = slider.val
            
            # Clear and redraw
            ax.clear()
            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            ax.set_zlabel('Z')
            ax.set_xlim([-1, 1])
            ax.set_ylim([-1, 1])
            ax.set_zlim([0, 2])
            
            # Calculate forward kinematics
            transforms = self.forward_kinematics(joint_angles)
            
            # Draw base
            ax.scatter([0], [0], [0], c='black', s=100, marker='o')
            
            # Draw links
            colors = ['blue', 'red', 'green', 'yellow', 'cyan', 'magenta']
            for i, (link, transform) in enumerate(zip(self.links[1:], transforms)):
                if link['visual'] and link['visual']['type'] == 'cylinder':
                    visual = link['visual']
                    T_visual = np.eye(4)
                    T_visual[:3, 3] = visual['origin']['xyz']
                    T_visual[:3, :3] = self.rotation_matrix(*visual['origin']['rpy'])
                    
                    final_transform = transform @ T_visual
                    self.draw_cylinder(ax, visual['radius'], visual['length'], 
                                     final_transform, colors[i % len(colors)])
                elif link['visual'] and link['visual']['type'] == 'box':
                    visual = link['visual']
                    T_visual = np.eye(4)
                    T_visual[:3, 3] = visual['origin']['xyz']
                    T_visual[:3, :3] = self.rotation_matrix(*visual['origin']['rpy'])
                    
                    final_transform = transform @ T_visual
                    self.draw_box(ax, visual['size'], final_transform, colors[i % len(colors)])
            
            # Draw joint positions
            positions = [[0, 0, 0]]
            for transform in transforms:
                positions.append(transform[:3, 3])
            positions = np.array(positions)
            ax.plot(positions[:, 0], positions[:, 1], positions[:, 2], 'ko-', linewidth=2, markersize=6)
            
            plt.draw()
        
        # Connect sliders to update function
        for slider in sliders:
            slider.on_changed(update)
        
        # Initial draw
        update(None)
        
        plt.show()

def main():
    visualizer = URDFVisualizer('robot.urdf')
    visualizer.visualize()

if __name__ == "__main__":
    main()
