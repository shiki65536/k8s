# Cloudiod: Image Object Detection Service

## Overview
Cloudiod is a RESTful web service for real-time image object detection using Flask, YOLOv3-tiny, and OpenCV. Deployed in Docker containers on a Kubernetes cluster (Docker Desktop), it processes base64-encoded images via HTTP POST requests, returning detected objects with labels, accuracy, and bounding boxes. Scalability is tested by varying pod counts (1-16) and client threads (1-16).

## System Design
- **Client**: `client.py` sends images with UUIDs.
- **Service**: NodePort (`30008`) routes requests to Flask app (port `5050`).
- **Pods**: Docker containers with 0.5 CPU, 512MiB memory.
- **YOLOv3-tiny + OpenCV**: Detects objects in images.

## Project Structure
```
cloudiod/
├── server.py                 # Flask web service
├── object_detection.py       # YOLO object detection logic
├── Dockerfile                # Docker container build file
├── deployment.yml            # Kubernetes deployment configuration
├── service.yml               # Kubernetes service configuration
├── client.py                 # Client test script
├── yolo_tiny_configs/        # YOLO model configuration
│   ├── yolov3-tiny.cfg
│   ├── yolov3-tiny.weights
│   └── coco.names
└── inputfolder/              # Folder for input JPEG images
```

## Prerequisites
- Docker Desktop with Kubernetes enabled
- Python 3.9
- YOLOv3-tiny configuration files
- Input images (JPEG) in `inputfolder/`

## Setup and Usage
1. **Clone Repository**:
   ```bash
   git clone <repository-url>
   cd cloudiod
   ```

2. **Create Input Folder**:
   ```bash
   mkdir inputfolder
   ```
   Place valid JPEG images in `inputfolder/` (e.g., download sample images or use your own).

3. **Download YOLOv3-tiny Configuration**:
   Create the `yolo_tiny_configs/` folder and download required files:
   ```bash
   mkdir yolo_tiny_configs
   cd yolo_tiny_configs
   wget https://pjreddie.com/media/files/yolov3-tiny.weights
   wget https://raw.githubusercontent.com/pjreddie/darknet/master/cfg/yolov3-tiny.cfg
   wget https://raw.githubusercontent.com/pjreddie/darknet/master/data/coco.names
   cd ..
   ```

4. **Build Docker Image**:
   ```bash
   docker build -t cloudiod:latest .
   ```

5. **Deploy to Kubernetes**:
   ```bash
   kubectl apply -f deployment.yml
   kubectl apply -f service.yml
   ```

6. **Verify Deployment**:
   ```bash
   kubectl get pods
   kubectl get svc my-service
   ```

7. **Test Service**:
   ```bash
   curl http://localhost:30008/
   python3 client.py inputfolder/ http://localhost:30008/api/ 2
   ```
   - The number at the end (e.g., `2`) specifies the number of threads for parallel requests.

8. **Scale and Test**:
   ```bash
   kubectl scale deployment k8s-app --replicas=4
   python3 client.py inputfolder/ http://localhost:30008/api/ 8
   ```

9. **Monitor Logs**:
   ```bash
   kubectl logs -l app=k8s-app -f
   ```

## Troubleshooting
- **NodePort Failure**: Use port-forward:
  ```bash
  kubectl port-forward service/my-service 5050:5050
  python3 client.py inputfolder/ http://localhost:5050/api/ 2
  ```
- **Invalid Images**: Ensure `inputfolder/` contains valid JPEGs.
- **Errors**: Check logs for JSON or image processing issues.

## Notes
- Ensure `yolo_tiny_configs/` contains `yolov3-tiny.weights`, `yolov3-tiny.cfg`, and `coco.names`.
- NodePort `30008` may require Docker Desktop restart if inaccessible.
