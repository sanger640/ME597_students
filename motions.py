# Imports
import rclpy

from rclpy.node import Node

from utilities import Logger, euler_from_quaternion
from rclpy.qos import QoSProfile

# TODO Part 3: Import message types needed: 
    # For sending velocity commands to the robot: Twist
    # For the sensors: Imu, LaserScan, and Odometry
# Check the online documentation to fill in the lines below
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Imu
from sensor_msgs.msg  import LaserScan
from nav_msgs.msg import Odometry

from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy

from rclpy.time import Time

# You may add any other imports you may need/want to use below
# import ...
from math import cos, sin

CIRCLE=0; SPIRAL=1; ACC_LINE=2
motion_types=['circle', 'spiral', 'line']

class motion_executioner(Node):
    
    def __init__(self, motion_type=0):
        
        super().__init__("motion_types")
        
        self.type=motion_type
        
        self.radius_=0.5

        # Define variables for motion callback. Allows for accelerationg speeds.
        self.accel=0.01
        
        self.successful_init=False
        self.imu_initialized=False
        self.odom_initialized=False
        self.laser_initialized=False
        
        # TODO Part 3: Create a publisher to send velocity commands by setting the proper parameters in (...)
        self.vel_publisher=self.create_publisher(Twist, "/cmd_vel", 10)
                
        # loggers
        self.imu_logger=Logger('imu_content_'+str(motion_types[motion_type])+'.csv', headers=["acc_x", "acc_y", "angular_z", "stamp"])
        self.odom_logger=Logger('odom_content_'+str(motion_types[motion_type])+'.csv', headers=["x","y","th", "stamp"])
        self.laser_logger=Logger('laser_content_'+str(motion_types[motion_type])+'.csv', headers=["ranges", "stamp"])
        
        # TODO Part 3: Create the QoS profile by setting the proper parameters in (...)
        qos=QoSProfile(reliability = ReliabilityPolicy.BEST_EFFORT, durability=DurabilityPolicy.VOLATILE, depth = 10)

        # TODO Part 5: Create below the subscription to the topics corresponding to the respective sensors
        # IMU subscription

        self.imu_sub = self.create_subscription(Imu, '/imu', self.imu_callback, qos_profile=qos)
        
        # ENCODER subscription

        self.enc_sub = self.create_subscription(Odometry, '/odom', self.odom_callback, qos_profile=qos)
        
        # LaserScan subscription 
        
        self.laser_sub = self.create_subscription(LaserScan, '/scan', self.laser_callback, 10)
        
        self.create_timer(0.25, self.timer_callback)


    # TODO Part 5: Callback functions: complete the callback functions of the three sensors to log the proper data.
    # To also log the time you need to use the rclpy Time class, each ros msg will come with a header, and then
    # inside the header you have a stamp that has the time in seconds and nanoseconds, you should log it in nanoseconds as 
    # such: Time.from_msg(imu_msg.header.stamp).nanoseconds
    # You can save the needed fields into a list, and pass the list to the log_values function in utilities.py

    def imu_callback(self, imu_msg: Imu):
       
       # Set True for timer call back
       self.imu_initialized = True

       # Assignment of message contents into variables for data logging
       stamp = Time.from_msg(imu_msg.header.stamp).nanoseconds
       ang_z = imu_msg.angular_velocity.z
       lin_x = imu_msg.linear_acceleration.x
       lin_y = imu_msg.linear_acceleration.y
       self.imu_logger.log_values([lin_x, lin_y, ang_z, stamp])
        
    def odom_callback(self, odom_msg: Odometry):
       
       # Set True for timer call back
       self.odom_initialized = True

       # Assignment of message contents into variables for data logging
       stamp = Time.from_msg(odom_msg.header.stamp).nanoseconds
       x = odom_msg.pose.pose.position.x
       y = odom_msg.pose.pose.position.y
       q = odom_msg.pose.pose.orientation

       # Angle of robot found from quaternion using function defined in utilities.py
       ql = [q.x, q.y, q.z, q.w]
       z = euler_from_quaternion(ql)
       self.odom_logger.log_values([x, y, z, stamp])
                
    def laser_callback(self, laser_msg: LaserScan):
       
       # Set True for timer call back
       self.laser_initialized = True

       # Assignment of message contents into variables for data logging
       stamp = Time.from_msg(laser_msg.header.stamp).nanoseconds
       ranges = laser_msg.ranges
       self.laser_logger.log_values([ranges, stamp])
                
    def timer_callback(self):
        if self.odom_initialized and self.laser_initialized and self.imu_initialized:
            self.successful_init=True
            
        if not self.successful_init:
            return
        
        cmd_vel_msg=Twist() 
        if self.type==CIRCLE:
            cmd_vel_msg=self.make_circular_twist()
        elif self.type==SPIRAL:
            cmd_vel_msg=self.make_spiral_twist()
                        
        elif self.type==ACC_LINE:
            cmd_vel_msg=self.make_acc_line_twist()
            
        else:
            print("type not set successfully, 0: CIRCLE 1: SPIRAL and 2: ACCELERATED LINE")
            raise SystemExit 

        self.vel_publisher.publish(cmd_vel_msg)
        
    
    # TODO Part 4: Motion functions: complete the functions to generate the proper messages corresponding to the desired motions of the robot

    def make_circular_twist(self):

        # Constant speed and angular velocity about z axis for circle motion
        msg=Twist()
        msg.linear.x = 0.5
        msg.angular.z = 1.0

         # fill up the twist msg for circular motion
        return msg

    def make_spiral_twist(self):

        # Outwards increasing spiral created by slowly increasing speed. Angular velocity maintained constant
        msg=Twist()
        msg.linear.x = self.accel
        msg.angular.z = self.radius_
        self.accel+=0.0025

         # fill up the twist msg for spiral motion
        return msg
    
    def make_acc_line_twist(self):

        # Acceleration in a straight line created by gradually increasing speed in x.
        msg=Twist()
        msg.linear.x = self.accel
        self.accel+=0.035

         # fill up the twist msg for line motion
        return msg

import argparse

if __name__=="__main__":
    

    argParser=argparse.ArgumentParser(description="input the motion type")


    argParser.add_argument("--motion", type=str, default="circle")



    rclpy.init()

    args = argParser.parse_args()

    if args.motion.lower() == "circle":

        ME=motion_executioner(motion_type=CIRCLE)
    elif args.motion.lower() == "line":
        ME=motion_executioner(motion_type=ACC_LINE)

    elif args.motion.lower() =="spiral":
        ME=motion_executioner(motion_type=SPIRAL)

    else:
        print(f"we don't have {arg.motion.lower()} motion type")


    
    try:
        rclpy.spin(ME)
    except KeyboardInterrupt:
        print("Exiting")
