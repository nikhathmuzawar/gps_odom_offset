import sqlite3
import csv
from rosidl_runtime_py.utilities import get_message
from rclpy.serialization import deserialize_message
import rclpy

rclpy.init()

# Path to your .db3 file
db_path = "/home/bob/ros2_px4_offboard_example_ws/rosbag2_2025_06_26-11_28_46/rosbag2_2025_06_26-11_28_46_0.db3"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get topic IDs
cursor.execute("SELECT id, name, type FROM topics")
topic_info = cursor.fetchall()

# Map topic names to their IDs and types
topics = {}
for tid, name, msg_type in topic_info:
    topics[name] = {"id": tid, "type": msg_type}

# === ODOMETRY CSV ===
odom_topic = "/odom"
if odom_topic in topics:
    OdomMsg = get_message(topics[odom_topic]["type"])
    cursor.execute("SELECT timestamp, data FROM messages WHERE topic_id=?", (topics[odom_topic]["id"],))
    with open("odom.csv", "w", newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["timestamp", "x", "y", "z"])
        for t, d in cursor.fetchall():
            msg = deserialize_message(d, OdomMsg)
            writer.writerow([
                t,
                msg.pose.pose.position.x,
                msg.pose.pose.position.y,
                msg.pose.pose.position.z
            ])
    print("Saved odom.csv")

# === GPS CSV ===
gps_topic = "/fmu/out/vehicle_gps_position"
if gps_topic in topics:
    GpsMsg = get_message(topics[gps_topic]["type"])
    cursor.execute("SELECT timestamp, data FROM messages WHERE topic_id=?", (topics[gps_topic]["id"],))
    with open("gps.csv", "w", newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["timestamp", "latitude_deg", "longitude_deg", "altitude_msl_m"])
        for t, d in cursor.fetchall():
            msg = deserialize_message(d, GpsMsg)
            writer.writerow([
                t,
                msg.latitude_deg,
                msg.longitude_deg,
                msg.altitude_msl_m
            ])
    print("Saved gps.csv")

conn.close()