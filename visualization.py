"""
URDF Robot Visualization Script
Visualizes a 6-axis robotic arm using PyBullet
"""

import pybullet as p
import pybullet_data
import time
import math

def main():
    """Main visualization function"""
    
    # Connect to PyBullet in GUI mode
    physics_client = p.connect(p.GUI)
    
    # Set up the simulation environment
    p.setAdditionalSearchPath(pybullet_data.getDataPath())
    p.setGravity(0, 0, -9.81)
    
    # Load a ground plane
    plane_id = p.loadURDF("plane.urdf")
    
    # Load the robot URDF
    robot_start_pos = [0, 0, 0]
    robot_start_orientation = p.getQuaternionFromEuler([0, 0, 0])
    
    robot_id = p.loadURDF("robot.urdf", 
                          robot_start_pos, 
                          robot_start_orientation,
                          useFixedBase=True)
    
    # Get number of joints
    num_joints = p.getNumJoints(robot_id)
    print(f"Robot loaded with {num_joints} joints")
    
    # Print joint information
    print("\n=== Joint Information ===")
    joint_indices = []
    for i in range(num_joints):
        joint_info = p.getJointInfo(robot_id, i)
        joint_name = joint_info[1].decode('utf-8')
        joint_type = joint_info[2]
        print(f"Joint {i}: {joint_name} (Type: {joint_type})")
        if joint_type == p.JOINT_REVOLUTE:
            joint_indices.append(i)
    
    # Configure camera
    p.resetDebugVisualizerCamera(
        cameraDistance=2.5,
        cameraYaw=45,
        cameraPitch=-30,
        cameraTargetPosition=[0, 0, 0.5]
    )
    
    # Add sliders for each joint
    joint_sliders = []
    for i in joint_indices:
        joint_info = p.getJointInfo(robot_id, i)
        joint_name = joint_info[1].decode('utf-8')
        lower_limit = joint_info[8]
        upper_limit = joint_info[9]
        
        slider = p.addUserDebugParameter(
            joint_name,
            lower_limit,
            upper_limit,
            0  # Initial position
        )
        joint_sliders.append((i, slider))
    
    print("\n=== Controls ===")
    print("Use the sliders on the right to control each joint")
    print("Close the window to exit")
    
    # Animation variables
    time_step = 0
    animation_speed = 0.5
    
    # Main simulation loop
    try:
        while True:
            # Read slider values and set joint positions
            for joint_idx, slider_id in joint_sliders:
                target_pos = p.readUserDebugParameter(slider_id)
                p.setJointMotorControl2(
                    robot_id,
                    joint_idx,
                    p.POSITION_CONTROL,
                    targetPosition=target_pos
                )
            
            # Step the simulation
            p.stepSimulation()
            time.sleep(1./240.)  # 240 Hz simulation
            
            time_step += 0.01
            
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        p.disconnect()

def demo_animation():
    """Alternative function with automated animation"""
    
    # Connect to PyBullet in GUI mode
    physics_client = p.connect(p.GUI)
    
    # Set up the simulation environment
    p.setAdditionalSearchPath(pybullet_data.getDataPath())
    p.setGravity(0, 0, -9.81)
    
    # Load a ground plane
    plane_id = p.loadURDF("plane.urdf")
    
    # Load the robot URDF
    robot_start_pos = [0, 0, 0]
    robot_start_orientation = p.getQuaternionFromEuler([0, 0, 0])
    
    robot_id = p.loadURDF("robot.urdf", 
                          robot_start_pos, 
                          robot_start_orientation,
                          useFixedBase=True)
    
    # Get revolute joint indices
    num_joints = p.getNumJoints(robot_id)
    joint_indices = []
    for i in range(num_joints):
        joint_info = p.getJointInfo(robot_id, i)
        if joint_info[2] == p.JOINT_REVOLUTE:
            joint_indices.append(i)
    
    # Configure camera
    p.resetDebugVisualizerCamera(
        cameraDistance=2.5,
        cameraYaw=45,
        cameraPitch=-30,
        cameraTargetPosition=[0, 0, 0.5]
    )
    
    print("\n=== Animated Demo Mode ===")
    print("Watch the robot perform an automated motion")
    print("Press Ctrl+C to exit")
    
    # Main animation loop
    time_step = 0
    try:
        while True:
            # Calculate sinusoidal joint positions
            for idx, joint_idx in enumerate(joint_indices):
                joint_info = p.getJointInfo(robot_id, joint_idx)
                lower_limit = joint_info[8]
                upper_limit = joint_info[9]
                
                # Different frequency for each joint
                frequency = 0.5 + idx * 0.2
                amplitude = (upper_limit - lower_limit) / 2
                center = (upper_limit + lower_limit) / 2
                
                target_pos = center + amplitude * 0.7 * math.sin(frequency * time_step)
                
                p.setJointMotorControl2(
                    robot_id,
                    joint_idx,
                    p.POSITION_CONTROL,
                    targetPosition=target_pos,
                    force=100
                )
            
            # Step the simulation
            p.stepSimulation()
            time.sleep(1./240.)
            time_step += 0.01
            
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        p.disconnect()

if __name__ == "__main__":
    import sys
    
    # Check command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        demo_animation()
    else:
        main()
