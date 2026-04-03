import matplotlib.pyplot as plt

# base analysis
def base_analysis_plot (best_lap):
  plt.figure (figsize=(12,6))                                            # Plot speed of the best lap over distance
  plt.plot(best_lap['Distance'], best_lap['GPS Speed'])
  plt.xlabel('Distance [m]')
  plt.ylabel('GPS Speed (km/h)')
  plt.title('GPS Speed over distance - best lap')
  plt.grid()
  plt.show()

  plt.figure (figsize=(12,6))                                            # Plot speed of the best lap over time
  plt.plot(best_lap['t'], best_lap['GPS Speed'])
  plt.xlabel('Time (s)')
  plt.ylabel('GPS Speed (km/h)')
  plt.title('GPS Speed over Time best lap')
  plt.grid()
  plt.show()

  plt.figure (figsize=(12,6))                                            # Plot speed of the best lap
  plt.plot(best_lap['Distance'], best_lap['RPM'])
  plt.xlabel('Distance [m]')
  plt.ylabel('Engine speed (RPM)')
  plt.title('Engine speed over distance')
  plt.grid()
  plt.show()

  plt.figure(figsize=(12,5))                                             # Plot longitudinal acceleration
  plt.plot(best_lap['Distance'], best_lap['AccelerometerX'])
  plt.xlabel('Distance [m]')
  plt.ylabel('Longitudinal Acc [g]')
  plt.title('Best Lap – Longitudinal Acceleration')
  plt.grid()
  plt.show()

  plt.figure(figsize=(12,5))                                             # Plot lateral acceleration
  plt.plot(best_lap['Distance'], best_lap['AccelerometerY'])
  plt.xlabel('Distance [m]')
  plt.ylabel('Lateral Acceleration [g]')
  plt.title('Best Lap – Lateral Acceleration')
  plt.grid()
  plt.show()

# advanced analysis part 1 - trajectory plot
def trajectory_plot (best_lap):
  latitude = best_lap['GPS Latitude'].values
  longitude = best_lap['GPS Longitude'].values
  speed = best_lap['GPS Speed'].values
  plt.figure(figsize=(12,6))
  plt.scatter(longitude, latitude, c=speed, cmap='jet', s=20)
  plt.axis('equal')
  plt.xlabel('Latitude')
  plt.ylabel('Longitude')
  plt.title('Trajectory Plot')
  plt.colorbar(label='Speed (km/h)')
  plt.show()

  rpm = best_lap['RPM'].values
  plt.figure(figsize=(12,6))
  plt.scatter(longitude,latitude,  c=rpm,cmap='jet', s=20)
  plt.axis('equal')
  plt.xlabel('Latitude')
  plt.ylabel('Longitude')
  plt.title('Engine Speed Plot')
  plt.colorbar(label='Engine speed plot [RPM]')
  plt.show()

  long_acc = best_lap['AccelerometerX'].values
  plt.figure(figsize=(12,6))
  plt.scatter(longitude,latitude,  c=long_acc, cmap='jet', s=20)
  plt.axis('equal')
  plt.xlabel('Latitude')
  plt.ylabel('Longitude')
  plt.title('Longitudinal Acceleration')
  plt.colorbar(label='Longitudinal Acceleration [g]')
  plt.show()

  lat_acc = best_lap['AccelerometerY'].values
  plt.figure(figsize=(12,6))
  plt.scatter(longitude,latitude,  c=lat_acc, cmap='jet', s=20)
  plt.axis('equal')
  plt.xlabel('Latitude')
  plt.ylabel('Longitude')
  plt.title('Lateral Acceleration')
  plt.colorbar(label='Lateral Acceleration [g]')
  plt.show()


def braking_plot(best_lap):
  # Braking events plot
  latitude = best_lap['GPS Latitude'].values
  longitude = best_lap['GPS Longitude'].values
  braking = best_lap['Braking_event'].values  # boolean True/False
  plt.figure(figsize=(12, 6))
  # base trajectory
  plt.plot(longitude, latitude, color='gray', linewidth=1, label='Trajectory')
  # marker in breaking points
  plt.scatter(
    longitude[braking],
    latitude[braking],
    color='red',
    s=30,
    marker='x',
    label='Brake event')
  starting_lat = best_lap['GPS Latitude'].values[0]
  starting_long = best_lap['GPS Longitude'].values[0]
  plt.scatter(
    starting_long, starting_lat, color= 'blue', marker='o', s=50, label='Start point'
  )
  plt.axis('equal')
  plt.xlabel('Longitude')
  plt.ylabel('Latitude')
  plt.title('Braking points – Best lap')
  plt.legend()
  plt.show()

def braking_analysis(best_lap):
  braking_data = best_lap[best_lap['Braking_zone'] > 0]
  braking_groups = braking_data.groupby("Brake_id")
  n_events = len(braking_groups)
  fig, ax = plt.subplots(1, len(braking_groups), figsize=(4* n_events, 8), sharex=True, sharey=True)
  # iteration on each braking event
  for i, (br_id, event_df) in enumerate(braking_groups):
    # Extract data from current df
    lat_acc = event_df['AccelerometerY']
    long_acc = event_df['AccelerometerX']

    # plot lat acc vs long acc
    ax[i].plot(lat_acc, long_acc, color='cyan', linewidth=1.5, zorder=1)
    ax[i].set_title(f'Braking n. {br_id}')
    if i == 0: ax[i].set_ylabel('Longitudinal acceleration [g]')
    ax[i].axhline(0, color='white', linewidth=0.5, alpha=0.5)
    ax[i].axvline(0, color='white', linewidth=0.5, alpha=0.5)
    ax[i].set_aspect('equal')
    ax[i].set_xlabel('Lateral acceleration [g]')

  plt.show()

  braking_data = best_lap[best_lap['Brake_id'] > 0].copy()
  groups = braking_data.groupby("Brake_id")
  n_events = len(groups)

  # speed plot
  fig, axes = plt.subplots(2, n_events, figsize=(4 * n_events, 8), sharex='col')

  for i, (br_id, event_df) in enumerate(groups):
    local_time = event_df['Time'] - event_df['Time'].iloc[0]
    ax_speed = axes[0, i]
    ax_speed.plot(local_time, event_df['GPS Speed'], color='white', linewidth=2)
    ax_speed.set_title(f'Braking n. {br_id}')
    if i == 0: ax_speed.set_ylabel('Speed [km/h]')
    ax_speed.grid(True, alpha=0.3)
    # deceleration plot
    ax_acc = axes[1, i]
    ax_acc.plot(local_time, event_df['AccelerometerX'], color='cyan', linewidth=1.5)
    ax_acc.axhline(-1.5, color='red', linestyle='--', alpha=0.5)
    if i == 0: ax_acc.set_ylabel("Deceleration [g]")
    ax_acc.set_xlabel("Time [s]")
    ax_acc.grid(True, alpha=0.3)

  plt.tight_layout()
  plt.show()

def turning_plot(best_lap):
  # Braking events plot
  latitude = best_lap['GPS Latitude'].values
  longitude = best_lap['GPS Longitude'].values
  turning = best_lap['Turn'].values  # boolean True/False
  plt.figure(figsize=(12, 6))
  # base trajectory
  plt.plot(longitude, latitude, color='gray', linewidth=1, label='Trajectory')
  # marker in breaking points
  plt.scatter(
    longitude[turning],
    latitude[turning],
    color='red',
    s=30,
    marker='.',
    label='Turn zone')
  starting_lat = best_lap['GPS Latitude'].values[0]
  starting_long = best_lap['GPS Longitude'].values[0]
  plt.scatter(
    starting_long, starting_lat, color='blue', marker='o', s=50, label='Start point'
  )
  plt.axis('equal')
  plt.xlabel('Longitude')
  plt.ylabel('Latitude')
  plt.title('Corners – Best lap')
  plt.legend()
  plt.show()


