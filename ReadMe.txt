![Architecture](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*HSDDIi1tCf5IKfdqXVzSLQ.png)

# Image Object Detection Service

## Overview
This is a RESTful web service for real-time image object detection using Flask, YOLOv3-tiny, and OpenCV. Deployed in Docker containers on a Kubernetes cluster (Docker Desktop), it processes base64-encoded images via HTTP POST requests, returning detected objects with labels, accuracy, and bounding boxes. Scalability is tested by varying pod counts (1-16) and client threads (1-16).

## System Design
- **Client**: `client.py` sends images with UUIDs.
- **Service**: NodePort (default `30008`) routes requests to Flask app (default port `5050`).
- **Pods**: Docker containers with 0.5 CPU, 512MiB memory (adjustable for YOLO model requirements).
- **YOLOv3-tiny + OpenCV**: Detects objects in images.

## Project Structure
```
project/
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

### System Requirements
- **Docker Desktop** with Kubernetes enabled
- **Python 3.9+** with pip
- **kubectl** CLI tool (included with Docker Desktop)
- At least **4GB RAM** available for Docker (recommended 8GB for multiple pods)

### Required Python Packages
```bash
pip install flask opencv-python numpy requests base64 uuid
```

## Installation and Setup

### 1. Environment Setup
```bash
# Verify Docker Desktop is running with Kubernetes enabled
docker version
kubectl version --client

# Verify Kubernetes context is set to docker-desktop
kubectl config current-context
# Should output: docker-desktop
```

### 2. Clone and Setup Repository
```bash
git clone <repository-url>

# Create input folder for test images
mkdir -p inputfolder
```

### 3. Download YOLOv3-tiny Configuration Files
```bash
# Create YOLO configuration directory
mkdir -p yolo_tiny_configs
cd yolo_tiny_configs

# Download required YOLO files
wget https://pjreddie.com/media/files/yolov3-tiny.weights
wget https://raw.githubusercontent.com/pjreddie/darknet/master/cfg/yolov3-tiny.cfg  
wget https://raw.githubusercontent.com/pjreddie/darknet/master/data/coco.names

# Verify downloads
ls -la
# Should show: yolov3-tiny.weights (33.7MB), yolov3-tiny.cfg, coco.names

cd ..
```

### 4. Prepare Test Images
```bash
# Add some JPEG images to inputfolder for testing
cp your_test_images/*.jpg inputfolder/

# Verify images are valid JPEGs
file inputfolder/*.jpg
```

## Configuration

### Key Configuration Points

#### server.py
```python
# Ensure Flask app runs on correct port (integer, not string)
app.run(host='0.0.0.0', port=5050, threaded=True)  # ✓ Correct
# NOT: port='5050'  # ✗ This will cause startup failures
```

#### deployment.yml
```yaml
# Ensure container port matches Flask app port
containers:
- name: k8s-app-container
  ports:
  - containerPort: 5050  # Must match Flask port

  # Resource limits (adjust based on your needs)
  resources:
    limits:
      memory: "2Gi"      # Increased for YOLO model
      cpu: "1"
    requests:
      memory: "1Gi"
      cpu: "0.5"
```

#### service.yml
```yaml
# NodePort can be auto-assigned or manually specified
spec:
  ports:
  - protocol: TCP
    port: 5050
    targetPort: 5050
    # nodePort: 30008  # Optional - let Kubernetes auto-assign if not specified
  type: NodePort
```

## Deployment

### 1. Build and Push Docker Image
```bash
# Build Docker image
docker build -t <your_username>/k8s-app:latest .  # replace to your docker account name

# Push to registry (optional, if using remote registry)
docker push <your_username>/k8s-app:latest  # replace to your docker account name
```

### 2. Deploy to Kubernetes
```bash
# Deploy application and service
kubectl apply -f deployment.yml
kubectl apply -f service.yml

# Wait for deployment to complete
kubectl rollout status deployment/k8s-app

# Verify deployment
kubectl get pods -l app=k8s-app
kubectl get svc my-service
```

### 3. Get Service Access Information
```bash
# Check assigned NodePort
kubectl get svc my-service
# Example output:
# NAME         TYPE       CLUSTER-IP      EXTERNAL-IP   PORT(S)          AGE
# my-service   NodePort   10.108.122.27   <none>        5050:30834/TCP   2m

# Note the NodePort (30834 in this example)
```

## Testing and Usage

### Basic Connectivity Test
```bash
# Replace 30834 with your actual NodePort
export NODEPORT=$(kubectl get svc my-service -o jsonpath='{.spec.ports[0].nodePort}')

# Test basic connectivity
curl http://localhost:$NODEPORT/
```

### API Functionality Test
```bash
# Test with a small base64-encoded image
curl -X POST http://localhost:$NODEPORT/api/ \
  -H "Content-Type: application/json" \
  -d '{"id":"test","image":"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="}' \
  --max-time 30 -v

# Expected: JSON response with detection results
```

### Client Application Test
```bash
# Test with single thread
python3 client.py inputfolder/ http://localhost:$NODEPORT/api/ 1

# Test with multiple threads for load testing
python3 client.py inputfolder/ http://localhost:$NODEPORT/api/ 4
```

### Scaling Test
```bash
# Scale up pods
kubectl scale deployment k8s-app --replicas=4

# Wait for scaling to complete
kubectl rollout status deployment/k8s-app

# Test with increased load
python3 client.py inputfolder/ http://localhost:$NODEPORT/api/ 8
```

## Monitoring and Debugging

### Common Monitoring Commands
```bash
# Check pod status and restart counts
kubectl get pods -l app=k8s-app

# View service configuration
kubectl get svc my-service

# Check all pods in cluster
kubectl get pods

# View node information
kubectl get nodes -o wide

# Describe specific pod (replace with actual pod name)
kubectl describe pod k8s-app-xxxxxxxxx-xxxxx

# View application logs
kubectl logs -l app=k8s-app --tail=50

# Follow logs in real-time
kubectl logs -l app=k8s-app -f

# Check resource usage (if metrics-server is available)
kubectl top pods -l app=k8s-app
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Pod Keeps Restarting
**Symptoms**: `kubectl get pods` shows restart count > 0
```bash
# Check pod logs for errors
kubectl logs -l app=k8s-app --previous

# Common causes and solutions:
# - Flask port type error: Ensure port=5050 (integer) not port='5050' (string)
# - Memory issues: Increase memory limits in deployment.yml
# - Missing YOLO files: Verify yolo_tiny_configs/ directory contents
```

#### 2. Connection Refused/RemoteDisconnected
**Symptoms**: Client gets connection errors
```bash
# Verify service is running
kubectl get svc my-service

# Test direct pod connection (bypass service)
kubectl port-forward deployment/k8s-app 5050:5050 &
curl http://localhost:5050/

# Check if containerPort matches Flask app port
kubectl describe deployment k8s-app | grep -A5 "Ports"
```

#### 3. API Returns 500 Error
**Symptoms**: curl returns HTTP 500 Internal Server Error
```bash
# Check application logs for detailed error
kubectl logs -l app=k8s-app --tail=20

# Common causes:
# - Invalid base64 image data
# - YOLO model loading failure
# - JSON parsing errors from double-encoding
```

#### 4. Client JSON Encoding Issues
**Problem**: Double JSON encoding in client code
```python
# ❌ Wrong: Double encoding
response = requests.post(url, json=json.dumps(data), headers=headers)

# ✅ Correct: Let requests handle JSON encoding
response = requests.post(url, json=data, headers=headers, timeout=60)
```

### Complete Reset Procedure
When things go wrong, use this complete reset:
```bash
# Delete existing resources
kubectl delete deployment k8s-app
kubectl delete service my-service

# Wait a moment for cleanup
sleep 5

# Redeploy everything
kubectl apply -f deployment.yml
kubectl apply -f service.yml

# Force restart (useful for Docker image updates)
kubectl rollout restart deployment k8s-app

# Wait for completion
kubectl rollout status deployment/k8s-app

# Verify everything is running
kubectl get pods -l app=k8s-app
kubectl get svc my-service
```

### Emergency Debugging Commands
```bash
# Get shell access to pod for debugging
kubectl exec -it $(kubectl get pods -l app=k8s-app -o jsonpath='{.items[0].metadata.name}') -- /bin/bash

# Test Flask app directly inside pod
kubectl exec -it $(kubectl get pods -l app=k8s-app -o jsonpath='{.items[0].metadata.name}') -- curl http://localhost:5050/

# Check if YOLO files are present
kubectl exec -it $(kubectl get pods -l app=k8s-app -o jsonpath='{.items[0].metadata.name}') -- ls -la yolo_tiny_configs/
```

## Performance Tuning

### Resource Optimization
```yaml
# For development/testing (minimal resources)
resources:
  limits:
    memory: "1Gi"
    cpu: "0.5"
  requests:
    memory: "512Mi"
    cpu: "0.25"

# For production/heavy load (recommended)
resources:
  limits:
    memory: "4Gi"
    cpu: "2"
  requests:
    memory: "2Gi"  
    cpu: "1"
```

### Load Testing
```bash
# Test different pod counts
for replicas in 1 2 4 8; do
  echo "Testing with $replicas replicas"
  kubectl scale deployment k8s-app --replicas=$replicas
  kubectl rollout status deployment/k8s-app
  python3 client.py inputfolder/ http://localhost:$NODEPORT/api/ $((replicas * 2))
  sleep 10
done
```

## Important Notes

### Docker Desktop Specific
- **Network Access**: Use `localhost` instead of node IP for NodePort services
- **Resource Limits**: Docker Desktop has memory limits that may need adjustment
- **Context**: Ensure kubectl context is set to `docker-desktop`

### Production Considerations
- Use `LoadBalancer` or `Ingress` instead of `NodePort` for production
- Implement proper logging and monitoring
- Use persistent volumes for model files
- Consider using `ConfigMaps` for YOLO configuration
- Implement health checks and readiness probes

### Security Notes
- NodePort services expose ports on all nodes - use with caution in production
- Consider using network policies to restrict pod-to-pod communication
- Use secrets for sensitive configuration data

## API Reference

### Endpoints

#### GET /
Returns welcome message to verify service is running.

#### POST /api/
Processes image for object detection.

**Request Format:**
```json
{
  "id": "unique-identifier",
  "image": "base64-encoded-image-data"
}
```

**Response Format:**
```json
{
  "id": "unique-identifier",
  "detections": [
    {
      "label": "person",
      "confidence": 0.85,
      "bbox": [x, y, width, height]
    }
  ]
}
```

**Content-Type:** `application/json`
