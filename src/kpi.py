from itertools import groupby

import numpy as np


def lap_kpi(lap_times, best_lap):
  lap_kpi = {
      "Max speed [km/h]": best_lap['GPS Speed'].max(),
      "Mean speed [km/h]": best_lap['GPS Speed'].mean(),
      "Max RPM": best_lap['RPM'].max(),
      "Mean RPM": best_lap['RPM'].mean()
  }

  return lap_kpi

def braking_kpi(best_lap):
    braking_data = best_lap[best_lap['Braking_zone'] > 0]
    braking_kpi = (
       braking_data.groupby("Brake_id").agg(
            avg_decel=("AccelerometerX", "mean"),
            max_decel=("AccelerometerX", "min"),
            braking_length=("Distance", lambda x: x.iloc[-1] - x.iloc[0]),
            entry_speed=("GPS Speed", lambda x:x.iloc[0]),
            min_speed=("GPS Speed", "min"),
        )
    )

    return braking_kpi

