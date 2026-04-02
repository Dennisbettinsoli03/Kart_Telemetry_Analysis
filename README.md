# 🏎️ Kart Telemetry Analysis

A Python framework to turn raw kart sensor data into actionable insights — because fast laps don't come from guessing.

---

## What is this?

This started as a personal project after spending too many track days wondering *why* I was losing time and *where* exactly. The answer was in the data — GPS position, speed, accelerometer readings, RPM — all recorded every 20ms by the onboard logger. The problem was making sense of it.

This framework automates the boring parts: cleaning the data, finding the lap boundaries, identifying braking zones and corners, and generating visualizations that actually tell you something useful. The goal is to go from a raw `.xlsx` export to a complete lap analysis in a few lines of code.

---

## What it can do

**Lap detection**
Automatically identifies individual laps from continuous session data using GPS proximity to the start/finish line. No manual splitting needed.

**Braking analysis**
Detects braking zones based on longitudinal deceleration threshold, assigns a unique ID to each event, and computes per-event KPIs: entry speed, minimum speed, average and peak deceleration, braking distance. The GG diagram (lateral vs longitudinal acceleration) gives you a quick read on how well you're using the available grip under braking.

**Corner detection & apex analysis**
Identifies corners from lateral acceleration data, finds the apex (minimum speed point) of each turn, and calculates the acceleration pickup distance — how far past the apex you wait before getting on the throttle. One of the more useful metrics for improving corner exit.

**Trajectory visualization**
Plots the full lap trajectory color-coded by speed, RPM, and longitudinal/lateral acceleration. Useful for spotting where you're carrying speed and where you're not.

**KPI summary**
Max and mean speed, max and mean RPM — quick numbers to compare sessions or drivers.

---

## Project structure

```
├── preprocessing.py   # Data import, cleaning, lap detection, zone identification
├── kpi.py             # KPI computation: lap summary, braking metrics, pickup point
├── plotting.py        # All visualizations
├── Notebook.ipynb     # Main analysis workflow — start here
└── telemetry.xlsx     # Example dataset
```

---

## Getting started

**Requirements**
```
pandas
numpy
matplotlib
openpyxl
```

Install with:
```bash
pip install pandas numpy matplotlib openpyxl
```

**Run the analysis**

Open `Notebook.ipynb` and follow the cells sequentially. The workflow is:

1. Load and clean the raw data
2. Detect lap boundaries
3. Select the best lap
4. Identify braking zones and corners
5. Generate plots and KPI tables

---

## Data format

The framework expects an `.xlsx` file exported from a compatible GPS/IMU logger with the following columns:

| Column | Description |
|---|---|
| `Time` | Timestamp [s] |
| `GPS Speed` | Speed [km/h] |
| `GPS Latitude` | Latitude [°] |
| `GPS Longitude` | Longitude [°] |
| `GPS PosAccuracy` | Position accuracy [m] |
| `GPS SpdAccuracy` | Speed accuracy [m/s] |
| `AccelerometerX` | Longitudinal acceleration [g] |
| `AccelerometerY` | Lateral acceleration [g] |
| `RPM` | Engine speed [rpm] |

Data quality filtering is applied automatically: rows with GPS position accuracy > 100m or speed accuracy > 1 m/s are dropped.

---

## Parameters you can tune

A few thresholds are set with sensible defaults but can be adjusted depending on your kart, tyres, or driving style:

| Parameter | Default | Where |
|---|---|---|
| Braking threshold | -1.0 g | `preprocessing.braking_zones()` |
| Corner threshold | 0.8 g | `preprocessing.corner_detector()` |
| SF line tolerance | 10 m | `preprocessing.compute_laps()` |
| Acceleration pickup threshold | 0.1 g | `kpi.acceleration_pickup_point()` |

---

## Background

I'm a Master's student in Automotive Engineering at Politecnico di Torino, specializing in Autonomous and Connected Vehicles. I also race karts — so vehicle dynamics isn't just theory for me. This project sits at the intersection of both worlds: real sensor data, real physics, real lap times.

The analysis methods are inspired by professional motorsport telemetry software, adapted for the data quality and budget constraints of amateur karting.

---

## License

MIT — use it, modify it, build on it. If you find it useful or want to contribute, feel free to open an issue or a pull request.
