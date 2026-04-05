import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def import_data(path):
  df = pd.read_excel(path)
  df = df.iloc[1:] # Remove the first row
  return df

def data_cleaning(df):
  df = df[(df['GPS PosAccuracy'] < 100) & (df['GPS SpdAccuracy'] < 1)].copy()        # data cleaning
  df = df.apply( pd.to_numeric, errors='coerce')     # convert object to float, faster than for cycle

  print(df['Time'].diff().describe()    )                    # data validation sampling freq = 50 Hz
  df = df.dropna(subset=["Time", "GPS Speed"])        # drop NA values
  df = df.sort_values("Time").reset_index(drop=True)   # sort values
  dt = df['Time'].diff().fillna(0)
  speed_ms = df['GPS Speed']/3.6
  df['Distance'] = (speed_ms * dt).cumsum()           # define cumulative distance
  return df

def select_sf_line(df):
  """
  Plot the full GPS trajectory and ask the user to click
  on the start/finish line. Returns (lat, lon).

  Usage in notebook:
      sf_lat, sf_lon = select_sf_line(df)
      df = compute_laps(df, sf_lat, sf_lon)
  """
  fig = plt.figure(figsize=(12, 6))
  plt.plot(df['GPS Longitude'], df['GPS Latitude'], color='steelblue', linewidth=0.8, alpha=0.7)
  plt.ylabel('Latitude')
  plt.xlabel('Longitude')
  plt.title('Select the s/f line point on the map and then close the window')
  plt.grid(True)
  plt.show()

  # define an empty variable
  clicked = []

  def onclick(event):
    # if the click is inside the plot append the coordinates to clicked
    if event.inaxes != None:
      clicked.append((event.ydata, event.xdata))
      # plot a marker to identify the coordinates
      plt.plot(event.xdata, event.ydata, 'ro',markersize=10, zorder=5)
      # draw the marker
      fig.canvas.draw()

  # when a click event occurs, the function onclick is called
  fig.canvas.mpl_connect('button_press_event', onclick)
  plt.show(block=True)

  if not clicked:
    raise error('Start/finish line not selected. Run select_sf_line again.')
  start_lat, start_long = clicked[-1]
  print(f"The start line is located at lat = {start_lat:.4f} and long = {start_long:.4f}")
  return start_lat, start_long

def compute_laps(df, start_lat, start_long):
  lat = np.radians(df['GPS Latitude'])                              # convert lat and long in radians
  lon = np.radians(df['GPS Longitude'])
  lat0 = np.radians(start_lat)
  lon0 = np.radians(start_long)
  R = 6371000                                                          # earth radius
  df["Dist_sf"] = R * np.sqrt( (lat - lat0)**2 +
                               (np.cos(lat0)*(lon - lon0))**2)          # distance approximation
  treshold = 10
  df['Cross_sf'] = df['Dist_sf']< treshold                                   # boolean to define sf line crossing (tolerance 5 m)

  df['Lap_id'] = 1+ (df['Cross_sf'] & ~df['Cross_sf'].shift(1).fillna(False).astype(bool)).cumsum()         # lap number increase only when approach sf line (boolean turn true)
  print ('The number of lap is', df['Lap_id'].iloc[-1])
  return df

def braking_zones(best_lap,min_dec:float = -1):
  # identify breaking zones
  """
      Detect braking zones based on longitudinal deceleration threshold.

      Parameters
      ----------
      best_lap : pd.DataFrame
      min_decel_g : float
          Deceleration threshold [g]. Default -1.0 g.
          Adjust for softer karts (e.g. -0.7) or high-grip conditions (e.g. -1.3).
      """
  best_lap['Braking_zone'] = best_lap['AccelerometerX'] < min_dec
  # starting point
  best_lap['Braking_event'] = (
            best_lap['Braking_zone'] & ~best_lap['Braking_zone'].shift(1).fillna(False).astype(bool))     # choose only the first instant in which deceleration overcome the threshold
  best_lap['Brake_id'] = best_lap['Braking_event'].cumsum()
  print('the number of braking event is', best_lap['Brake_id'].iloc[-1])
  best_lap.loc[~best_lap['Braking_zone'],['Brake_id']] = 0           # assign 0 to the instants in which the kart is not braking
  return best_lap


def corner_detector(best_lap,acc_threshold: float = 0.8):
  """
      Detect cornering zones based on lateral acceleration threshold.

      Parameters
      ----------
      best_lap : pd.DataFrame
      lat_acc_threshold : float
          Lateral acceleration threshold [g]. Default 0.8 g.
      """

  best_lap['Turn'] = abs(best_lap['AccelerometerY']) > acc_threshold
  best_lap['Turn_start'] = (best_lap['Turn'] & ~best_lap['Turn'].shift(1).fillna(0).astype(bool))
  best_lap['Turn_id'] = (best_lap['Turn_start'])[best_lap['Turn'] == True].cumsum()
  best_lap.loc[best_lap['Turn'] == False, 'Turn_id'] = 0
  return best_lap


