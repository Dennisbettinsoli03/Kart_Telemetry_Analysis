from itertools import groupby

import numpy as np
import pandas as pd


def lap_kpi(best_lap: pd.DataFrame) -> dict:
    """
    Compute summary KPIs for the best lap.

    Returns
    -------
    dict with max/mean speed and RPM.
    """
    return {
        "Max speed [km/h]": round(best_lap['GPS Speed'].max(), 1),
        "Mean speed [km/h]": round(best_lap['GPS Speed'].mean(), 1),
        "Max RPM": int(best_lap['RPM'].max()),
        "Mean RPM": int(best_lap['RPM'].mean()),
    }

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
def acceleration_pickup_point(best_lap,acc_min: float = 0.1):
    """
        Calculate the distance between apex and traction point for each corner.

        Parameters
        ----------
        best_lap : pd.DataFrame
        acc_threshold_g : float
            Longitudinal acceleration threshold to detect traction point [g].

        Returns
        -------
        best_lap : pd.DataFrame (with Acceleration and Acc_start columns added)
        pickup_table : pd.DataFrame with columns [Turn_id, pickup_distance]
        """
    # Apex detection: find the point of minimum speed for each turn
    turns_only = best_lap[best_lap['Turn_id'] > 0]
    idx_apex = turns_only.groupby('Turn_id')['GPS Speed'].idxmin()

    # Traction point detection: identify when acceleration exceeds the threshold
    best_lap['Acceleration'] = (best_lap['AccelerometerX']) > acc_min
    best_lap['Acc_start'] = (best_lap['Acceleration'] & ~best_lap['Acceleration'].shift(1).fillna(0).astype(bool))

    # Distance calculation (Initialize empty list to store results)
    pickup_distances = []

    for turn_id in idx_apex.index:
        # Reference indices and distances for the current turn
        current_apex_idx = idx_apex[turn_id]
        apex_dist = best_lap.loc[current_apex_idx, 'Distance']
        # Search area: look for acceleration events from the apex onwards
        searching_area = best_lap.loc[current_apex_idx:]
        pickup_event = searching_area[searching_area['Acc_start'] == True]
        # Safety logic: if an acceleration event is found, calculate the delta distance
        if not pickup_event.empty:
            # EXTRACT ONLY THE FIRST VALUE (.iloc[0])
            pickup_dist_val = pickup_event['Distance'].iloc[0]
            pickup_interval = pickup_dist_val - apex_dist
        else:
            # Handle cases where telemetry ends before the driver accelerates
            pickup_interval = None
        # Append ONLY the clean dictionary for each turn
        pickup_distances.append({
            'Turn_id': turn_id,
            'pickup_distance': pickup_interval
        })

    # Final Table Creation
    pickup_table = pd.DataFrame(pickup_distances)

    return best_lap, pickup_table
