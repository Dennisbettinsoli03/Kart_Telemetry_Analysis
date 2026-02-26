import pandas as pd
import numpy as np

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

def compute_laps(df):
  start_lat = df['GPS Latitude'].iloc[100]                    # define starting line
  start_long = df['GPS Longitude'].iloc[100]
  lat = np.radians(df['GPS Latitude'])                              # convert lat and long in radians
  lon = np.radians(df['GPS Longitude'])
  lat0 = np.radians(start_lat)
  lon0 = np.radians(start_long)
  R = 6371000                                                          # earth radius
  df["Dist_sf"] = R * np.sqrt( (lat - lat0)**2 + (np.cos(lat0)*(lon - lon0))**2)          # distance approximation
  treshold = 10
  df['Cross_sf'] = df['Dist_sf']< treshold                                   # boolean to define sf line crossing (tolerance 5 m)

  df['Lap_id'] = 1+ (df['Cross_sf'] & ~df['Cross_sf'].shift(1).fillna(False).astype(bool)).cumsum()         # lap number increase only when approach sf line (boolean turn true)
  print ('The number of lap is', df['Lap_id'].iloc[-1])
  return df

def braking_zones(best_lap):
  # identify breaking zones
  min_dec = -1  # g
  best_lap['Braking_zone'] = best_lap['AccelerometerX'] < min_dec

  # starting point
  best_lap['Braking_event'] = (
            best_lap['Braking_zone'] & ~best_lap['Braking_zone'].shift(1).fillna(False).astype(bool))     # choose only the first instant in which deceleration overcome the threshold
  best_lap['Brake_id'] = best_lap['Braking_event'].cumsum()
  print('the number of braking event is', best_lap['Brake_id'].iloc[-1])
  best_lap.loc[~best_lap['Braking_zone'],['Brake_id']] = 0           # assign 0 to the instants in which the kart is not braking
  return best_lap


def corner_detector(best_lap):
  # identify corners
    acc_threshold = 0.8
    best_lap['Turn'] = abs(best_lap['AccelerometerY']) > acc_threshold
    best_lap['Turn_start'] = (best_lap['Turn'] & ~best_lap['Turn'].shift(1).fillna(0).astype(bool))
    best_lap['Turn_id'] = (best_lap['Turn_start'])[best_lap['Turn'] == True].cumsum()
    best_lap.loc[best_lap['Turn'] == False, 'Turn_id'] = 0
    return best_lap


