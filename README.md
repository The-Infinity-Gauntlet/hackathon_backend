# hackathon_backend

Project includes a flood camera monitoring module with a single unified CLI: `./aqua`.

## Setup

- Ensure Python 3.13 is installed. Optional: install PDM for development tasks.
- Make the CLI executable (one time):
  - chmod +x ./aqua

## Run server

- ./aqua dev

## Predict from image or URL

- ./aqua predict PATH_OR_URL

## Streaming prediction

- ./aqua stream STREAM_URL

Example:

- ./aqua stream <https://example.com/live.m3u8>

For HLS (.m3u8) streams, ffmpeg must be installed on the system (in PATH).

## Training with real images

- Put images under core/flood_camera_monitoring/data/train/{flooded,normal}
- ./aqua train

The best checkpoint is copied to core/flood_camera_monitoring/infra/machine_model/best_real_model.pth for inference.

## Aqua CLI commands

- ./aqua help
- ./aqua install # pdm install (if PDM installed)
- ./aqua dev
- ./aqua migrate | ./aqua makemigrations | ./aqua createsuperuser
- ./aqua train [--data_dir DIR] [--model_name resnet50] [--epochs 120] [--batch_size 8] [--lr 1e-4] [--min_images 20]
- ./aqua train-min [--data_dir DIR] [--min_images 10] [--epochs 10]
- ./aqua stream URL [--interval 3.0] [--device cpu] [--model PATH] [--save] [--out predictions]
- ./aqua predict SOURCE [--device cpu] [--model PATH]
- ./aqua inspect [--ckpt PATH]
- ./aqua smoke
- ./aqua status
- ./aqua clean

## Configuration: Camera installation URL

Expose a link for installing/adding cameras in API responses by setting an environment variable:

- CAMERA_INSTALL_URL="https://your-portal.example.com/install-camera"

When set, the following endpoints include `camera_install_url` in the JSON:

- GET /api/flood_monitoring/predict/all
- POST /api/flood_monitoring/stream/snapshot
- POST /api/flood_monitoring/stream/batch
- POST /api/flood_monitoring/analyze/run
- GET /api/flood_monitoring/cameras
