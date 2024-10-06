from sgp4.api import Satrec, jday
import requests
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime

# Step 1: Fetch and Parse TLE Data
@st.cache
def fetch_tle_data():
    url = "https://celestrak.com/NORAD/elements/stations.txt"
    tle_data = requests.get(url).text
    lines = tle_data.splitlines()

    tle_name = lines[0].strip()
    tle_line1 = lines[1].strip()
    tle_line2 = lines[2].strip()

    return tle_name, tle_line1, tle_line2

tle_name, tle_line1, tle_line2 = fetch_tle_data()

# Step 2: Create satellite object using SGP4
satellite = Satrec.twoline2rv(tle_line1, tle_line2)

# Get current date and time for satellite position
now = datetime.utcnow()
jd, fr = jday(now.year, now.month, now.day, now.hour, now.minute, now.second)

# Step 2: Predict Future Movements of Debris
def predict_trajectory(satellite, start_jd, start_fr, hours=24):
    positions = []
    times = np.linspace(0, hours, num=hours*60)  # Every minute

    for delta_hour in times:
        jd, fr = start_jd + (delta_hour / 24), start_fr
        e, r, v = satellite.sgp4(jd, fr)
        if e == 0:
            positions.append(r)
        else:
            print(f"Error at t={delta_hour} hours")

    return np.array(positions)

positions = predict_trajectory(satellite, jd, fr, hours=24)

# Step 3: Plot the predicted debris trajectory in 3D
fig = go.Figure(data=[go.Scatter3d(x=positions[:, 0], y=positions[:, 1], z=positions[:, 2],
                                   mode='lines', name='Debris Trajectory')])

fig.update_layout(scene=dict(xaxis_title='X (km)', yaxis_title='Y (km)', zaxis_title='Z (km)'),
                  title='Predicted Space Debris Trajectory for Next 24 Hours')

# Step 4: Create Streamlit Web Dashboard
st.title("Space Debris Tracking and Prediction")
st.write(f"Tracking debris object: {tle_name}")

# Show the predicted trajectory
st.plotly_chart(fig)

# Display the current position and velocity
e, r, v = satellite.sgp4(jd, fr)
if e == 0:
    st.write(f"Current Position (km): {r}")
    st.write(f"Current Velocity (km/s): {v}")
else:
    st.write("Error in computation of current position and velocity.")
