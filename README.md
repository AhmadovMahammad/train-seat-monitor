# Train Seat Monitor

A simulation project for the lecture: **"Big Data Pipelines for Computer Vision: Real-Time Processing of Video Streams"** in AZTU (Azerbaijan Technical University)

## Overview

This project simulates a real-time seat occupancy detection system for train wagons.
Instead of sending heavy video streams to a central server, processing happens locally on the edge device (edge computing) - only lightweight JSON status updates are forwarded.
This is the core Big Data pipeline optimization the lecture demonstrates.

## Architecture

```
Camera → MOG (Background subtraction in future) → Frame Skip → 
YOLO (person detection) → ROI Check → [Pipeline] → Backend API → Display
```

- **Frame skip** - process every Nth frame instead of all, reduces load significantly
- **ROI (Region of Interest)** - only analyze the seat area, not the full frame
- **YOLO** - detects persons in the cropped seat region
- **Pipeline** - planned: RabbitMQ message queue + .NET backend API + SignalR push to display

## Scale Example

| Level | Count |
|---|---|
| Cameras per wagon | 10 |
| Wagons per train | 10 |
| Trains | 50 |
| **Total cameras** | **5,000** |
| Frames/sec (15fps, every 5th) | **15,000 frames/sec** |

Sending raw video at this scale is impossible - this is why pipelines matter.

## Usage

```bash
# 1. Set up environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Mark seat regions on an empty frame (saves to roi_data.json)
python mark_roi.py

# 3. Run detection
python main.py
```