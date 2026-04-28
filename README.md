# Train Seat Monitor

A simulation project for the lecture: **"Big Data Pipelines for Computer Vision: Real-Time Processing of Video Streams"** in AZTU (Azerbaijan Technical University)

## Overview

Real-time seat occupancy detection for train wagons. Processing runs on the edge device, only lightweight JSON events are forwarded, not raw video streams.

## Architecture

```
Camera → Frame Skip → YOLO (person detection) → ROI Check → RabbitMQ → .NET API Consumer
```

- **Frame skip**: every 5th frame is analyzed, reducing load by 80%
- **ROI**: only the marked seat region is cropped and passed to YOLO, not the full frame
- **YOLO (yolov8n)**: detects persons inside the cropped region
- **Change-only publish**: event is sent only when seat status changes (free ↔ occupied)
- **RabbitMQ**: `passenger-seat` queue (quorum, durable) decouples CV from backend
- **Multiprocessing**: each camera runs in its own process in parallel

## Scale

| Level | Count |
|---|---|
| Cameras per wagon | 10 |
| Wagons per train | 10 |
| Trains | 50 |
| **Total cameras** | **5,000** |
| Frames analyzed/sec (15fps, every 5th) | **15,000/sec** |

Sending raw video at this scale is infeasible: this is why the pipeline exists.

## Project Structure

```
├── cv/
│   ├── main.py            # Production: multiprocessing, one process per camera, publishes to RabbitMQ
│   ├── main_simple.py     # Demo: single camera, no RabbitMQ, draws bounding boxes on screen
│   ├── mark_roi.py        # Tool to mark seat regions and save to config.json
│   ├── settings.py        # Paths (config, video source, model)
│   └── yolov8n.pt         # YOLO model weights
├── api/
│   └── SeatMonitorApi/    # .NET BackgroundService consuming RabbitMQ, logs received events
└── config.json            # Train → wagon → camera → seat coords
```

## Running

**Prerequisites**
```bash
docker start rabbitmq   # or: docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:management
```

**CV (producer)**
```bash
cd cv
source venv/bin/activate

python main_simple.py   # demo mode: shows video with seat labels
python main.py          # full mode: all cameras in parallel, publishes to RabbitMQ
```

**API (consumer)**
```bash
cd api/SeatMonitorApi
dotnet run
```

**RabbitMQ management panel:** `http://localhost:15672` (guest / guest)

## Setup from scratch

```bash
cd cv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Edit `config.json` — define trains, wagons, and cameras.

```bash
python mark_roi.py      # mark seat regions, saves coords to config.json
```
