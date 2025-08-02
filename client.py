# Generate the parallel requests based on the ThreadPool Executor
from concurrent.futures import ThreadPoolExecutor as PoolExecutor
import sys
import time
import glob
import requests
import threading
import uuid
import base64
import  json
import os

#send http request
def call_object_detection_service( image):
    try:

        url = str(sys.argv[2])
        #generate uuid for image
        id =   uuid.uuid5(uuid.NAMESPACE_OID, image)
        # Encode image into base64 string
        with open (image, 'rb') as image_file:
            image_data =  base64.b64encode(image_file.read()).decode('utf-8')

        data = {
            'image': image_data,
            'id': str(id)
        }
        headers = {'Content-Type': 'application/json'}

        response = requests.post(url, json= data, headers = headers, timeout=60)

        if response.ok:
            output = "Thread : {}, input image: {}, output:{}".format(
                threading.current_thread().getName(),
                image, response.text)
            print(output)
        else:
            print("Error, response status: {} - {}".format(response.status_code, response.text))

    except requests.exceptions.ConnectionError as e:
        print("Connection error for {}: {}".format(image, e))
    except requests.exceptions.Timeout as e:
        print("Timeout error for {}: {}".format(image, e))
    except Exception as e:
        print("Exception in webservice call for {}: {}".format(image, e))

# gets list of all images path from the input folder
def get_images_to_be_processed(input_folder):
    images = []
    for image_file in glob.iglob(input_folder + "*.jpg"):
        images.append(image_file)
    return images

def main():
    ## provide argumetns-> input folder, url, number of wrokers
    if len(sys.argv) != 4:
        raise ValueError("Arguments list is wrong. Please use the following format: {} {} {} {}".
                         format("python Cloudiod_client.py", "<input_folder>", "<URL>", "<number_of_workers>"))

    input_folder = os.path.join(sys.argv[1], "")
    images = get_images_to_be_processed(input_folder)
    num_images = images.__len__()
    num_workers = int(sys.argv[3])
    start_time = time.time()
    
    #craete a worker  thread  to  invoke the requests in parallel
    with PoolExecutor(max_workers=num_workers) as executor:
        for _ in executor.map(call_object_detection_service,  images):
            pass
    elapsed_time =  time.time() - start_time
    print("Total time spent: {} average response time: {}".format(elapsed_time, elapsed_time/num_images))


if __name__ == "__main__":
    main()


