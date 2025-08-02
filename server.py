from flask import Flask, request
import object_detection
import cv2
import numpy as np
import json
import base64

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "Use command: python Cloudiod_client.py <inputfolder> <endpoint> <num_threads>"

@app.route("/api/", methods=["GET"])
def get():
    return "/api, use [POST] method"

@app.route("/api/", methods=["POST"])
def api():
    ## Yolov3-tiny versrion
    yolo_path  = object_detection.yolo_path
    labelsPath=  object_detection.labelsPath
    cfgpath=  object_detection.cfgpath
    wpath=  object_detection.wpath

    LABELS = object_detection.get_labels(labelsPath)
    cfg = object_detection.get_config(cfgpath)
    weights = object_detection.get_weights(wpath)

    # data = request.get_json()

    # #Handle JSON request, JSON -> dict
    json_str = request.get_json()
    data = json.loads(json_str)

    id = data["id"]
    image_str = data["image"]

    #Clean temp file
    del data

    #image setting
    image_bytes = base64.b64decode(image_str)
    img = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
    npimg = np.array(img)
    image = npimg.copy()
    image = cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
    nets = object_detection.load_model(cfg, weights)

    #main
    response = {"id": id}
    response.update({"object": object_detection.do_prediction(image, nets, LABELS)})
    return json.dumps(response, indent=2)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5050, threaded=True)
