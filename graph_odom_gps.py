import pandas as pd
from pyproj import Proj, transform
from math import sqrt
import matplotlib.pyplot as plt

# Load your data
odom_df = pd.read_csv('odom.csv')
gps_df = pd.read_csv('gps.csv')

# UTM conversion
ref_lat = gps_df['latitude_deg'].iloc[0]
ref_lon = gps_df['longitude_deg'].iloc[0]
utm_zone = int((ref_lon + 180) / 6) + 1
is_northern = ref_lat > 0
in_proj = Proj(proj='latlong', datum='WGS84')
out_proj = Proj(proj='utm', zone=utm_zone, ellps='WGS84', south=not is_northern)
gps_x, gps_y = transform(in_proj, out_proj, gps_df['longitude_deg'].values, gps_df['latitude_deg'].values)
gps_df['utm_x'] = gps_x
gps_df['utm_y'] = gps_y

# Sort and merge asof (nearest timestamp match)
odom_df = odom_df.sort_values('timestamp')
gps_df = gps_df.sort_values('timestamp')
merged = pd.merge_asof(gps_df, odom_df, on='timestamp', direction='nearest')

# Compute offset
merged['offset_x'] = merged['utm_x'] - merged['x']
merged['offset_y'] = merged['utm_y'] - merged['y']
merged['offset_z'] = merged['altitude_msl_m'] - merged['z']
merged['offset_magnitude'] = merged.apply(lambda row: sqrt(row['offset_x']**2 + row['offset_y']**2 + row['offset_z']**2), axis=1)
merged['timestamp_norm'] = merged['timestamp'] - merged['timestamp'].min()

# Plot
plt.figure(figsize=(12,6))
plt.plot(merged['timestamp_norm'], merged['offset_magnitude'], label='Offset Magnitude (m)')
plt.xlabel('Normalized Timestamp')
plt.ylabel('Offset Magnitude (m)')
plt.title('GPS vs Odometry Position Offset Over Time')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
