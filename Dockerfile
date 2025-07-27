FROM python:3.9-slim
ADD server.py object_detection.py /
COPY /yolo_tiny_configs /yolo_tiny_configs
RUN pip install flask numpy opencv-python-headless
CMD ["python", "/server.py"]
