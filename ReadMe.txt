# Image Object Detection Service

## Overview
This is a RESTful web service for real-time image object detection using Flask, YOLOv3-tiny, and OpenCV. Deployed in Docker containers on a Kubernetes cluster (Docker Desktop), it processes base64-encoded images via HTTP POST requests, returning detected objects with labels, accuracy, and bounding boxes. Scalability is tested by varying pod counts (1-16) and client threads (1-16).

## System Design
- **Client**: `client.py` sends images with UUIDs.
- **Service**: NodePort (`30008`) routes requests to Flask app (port `5050`).
- **Pods**: Docker containers with 0.5 CPU, 512MiB memory.
- **YOLOv3-tiny + OpenCV**: Detects objects in images.

## Prerequisites
- Docker Desktop with Kubernetes enabled
- Python 3.9
- YOLOv3-tiny configs (`yolov3-tiny.weights`, `yolov3-tiny.cfg`, `coco.names`)
- Input images (JPEG) in `inputfolder/`

## Setup and Usage
1. **Clone Repository**:
   ```bash
   git clone <repository-url>
   cd cloudiod
   ```

2. **Build Docker Image**:
   ```bash
   docker build -t cloudiod:latest .
   ```

3. **Deploy to Kubernetes**:
   ```bash
   kubectl apply -f deployment.yml
   kubectl apply -f service.yml
   ```

4. **Verify Deployment**:
   ```bash
   kubectl get pods
   kubectl get svc my-service
   ```

5. **Test Service**:
   ```bash
   curl http://localhost:30008/
   python3 client.py inputfolder/ http://localhost:30008/api/ 2
   ```
The number at the end (e.g., 2) specifies the number of threads for parallel requests.

6. **Scale and Test**:
   ```bash
   kubectl scale deployment k8s-app --replicas=4
   python3 client.py inputfolder/ http://localhost:30008/api/ 8
   ```

7. **Monitor Logs**:
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
- Ensure `yolo_tiny_configs/` is in the project directory.
- NodePort `30008` may require Docker Desktop restart if inaccessible.
