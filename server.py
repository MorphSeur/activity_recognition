# -*- coding: utf-8 -*-

import os
from flask import Flask, jsonify, request
import json
import jsonschema

from iai_toolbox import AnalyticsRequest, AnalyticsAgent, get_analytics_pool
import time

print("rrrrrr")

import os
import cv2
import numpy as np
from collections import deque
from tensorflow.keras.models import load_model

os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

"""
C3ISP export utility.
"""

__author__ = "Vincenzo Farruggia"
__license__ = "GPL"
__version_info__ = ('2022','09','21')
__version__ = ''.join(__version_info__)

app = Flask(__name__)
DEBUG=('DEBUG' in os.environ and os.environ['DEBUG'] in ['1', 'true'])

def dpoDecodeOne(dpoInfo, pathToTmp):

    ext1 = dpoInfo['iai_dpo_metadata'][0]['file:extension']

    if ext1 == 'png':
        imageName1 = dpoInfo['iai_dpo_metadata'][0]['id'] + '.dpo'

        statusPNG1 = os.system("base64 -d " + pathToTmp + '/' + imageName1 + "> " + pathToTmp + '/' + "r.png")
    elif ext1 == 'jpg':
        imageName1 = dpoInfo['iai_dpo_metadata'][0]['id'] + '.dpo'

        statusPNG1 = os.system("base64 -d " + pathToTmp + '/' + imageName1 + "> " + pathToTmp + '/' + "r.jpg")
    else:
        if ext1 == 'mp4':
            videoName1 = dpoInfo['iai_dpo_metadata'][0]['id'] + '.dpo'

            if 'mp4' in ext1:
                videoName = videoName1
            statusMP4 = os.system("base64 -d " + pathToTmp + '/' + videoName + "> " + pathToTmp + '/' + "g.mp4")

        if ext1 == 'avi':
            videoName1 = dpoInfo['iai_dpo_metadata'][0]['id'] + '.dpo'

            if 'avi' in ext1:
                videoName = videoName1
            statusMP4 = os.system("base64 -d " + pathToTmp + '/' + videoName + "> " + pathToTmp + '/' + "g.avi")

        if ext1 == 'png':
            imageName1 = dpoInfo['iai_dpo_metadata'][0]['id'] + '.dpo'

            if 'png' in ext1:
                imageName = imageName1

            statusPNG = os.system("base64 -d " + pathToTmp + '/' + imageName + "> " + pathToTmp + '/' + "r.png")

        if ext1 == 'jpg':
            imageName1 = dpoInfo['iai_dpo_metadata'][0]['id'] + '.dpo'

            if 'jpg' in ext1:
                imageName = imageName1

            statusJPG = os.system("base64 -d " + pathToTmp + '/' + imageName + "> " + pathToTmp + '/' + "f.jpg")

def predict_video(video_path):
    IMAGE_HEIGHT, IMAGE_WIDTH = 64, 64
    SEQUENCE_LENGTH = 20
    CLASSES_LIST = ["sitting ","walking","Standing"]

    savemodel_path = "./activityRecognition20102022.hdf5"

    new_model = load_model(savemodel_path)

    video_reader = cv2.VideoCapture(video_path)
    length = int(video_reader.get(cv2.CAP_PROP_FRAME_COUNT))
    frames_queue = deque(maxlen = SEQUENCE_LENGTH)
    predicted_class_name = ''

    while video_reader.isOpened():
        ok, frame = video_reader.read() 
        
        if not ok:
            break

        resized_frame = cv2.resize(frame, (IMAGE_HEIGHT, IMAGE_WIDTH))
        normalized_frame = resized_frame / 255
        frames_queue.append(normalized_frame)

        if len(frames_queue) == SEQUENCE_LENGTH:
            predicted_labels_probabilities = new_model.predict(np.expand_dims(frames_queue, axis = 0))[0]
            predicted_label = np.argmax(predicted_labels_probabilities)
            predicted_class_name = CLASSES_LIST[predicted_label]
            store = predicted_class_name + " " + str(predicted_labels_probabilities[predicted_label])
            # print(f'{predicted_class_name} {predicted_labels_probabilities[predicted_label]}')
    video_reader.release()
    return store

class SampleAnalytics(AnalyticsAgent):
  def run(self):
    app.logger.info("--- run() started!")

    dpoInfo = request.json
    dpoInfo = json.loads(json.dumps(dpoInfo))
    pathToTmp = dpoInfo['iai_datalake']

    print(pathToTmp)

    dpoDecodeOne(dpoInfo, pathToTmp)

    time.sleep(3)

    fileList = []
    fileListExt = []

    for element in os.listdir(pathToTmp):
        file = os.path.join(pathToTmp, element)
        if os.path.isfile(file):
            fileList.append(file)
            fileListExt.append(file[-4:])

    counting = {i:fileListExt.count(i) for i in fileListExt}

    if ".avi" in fileListExt:
            if counting[".avi"]:
                for fileElement in fileList:
                    if fileElement[-4:] == '.mp4' or fileElement[-4:] == '.avi':
                        contentMP4AVI = fileElement
                        app.logger.info('[dump input:{}]: {}'.format(fileElement, contentMP4AVI))
                
                print(contentMP4AVI)
                store = predict_video(contentMP4AVI)

    # Because write_output will manage byte streams we need to convert string to
    # bytes content
    plaintext_output = store.encode('UTF-8')
    self.write_output('outfile', plaintext_output)

    app.logger.info('--- run() ended!')

    # when analytics finished do callback to server
    success = True
    value = "Sample analytics finished with success!!!"
    results = []
    self.on_finish(success, value, results)

  def end(self):
    app.logger.info('--- Termination request for analytics')
    # insert code here for graceful terminate analytics
    # and after signal IAI for termination

    success = False
    value = "Sample analytics interrupted!!!"
    results = []
    self.on_finish(success, value, results)

@app.route("/startAnalytics", methods = ['POST'])
def do_start_analytics():
  payload = request.json

  jsonschema.validate(payload, AnalyticsRequest.SCHEMA)

  app.logger.debug('New request: {}'.format(payload))

  try:
    iai_req = AnalyticsRequest.from_params(payload)
    
    # Create analytics process object
    process = SampleAnalytics(iai_req)

    analytics_pool = get_analytics_pool()
    
    # Add analytics process to the pool of running analytics
    analytics_pool.add(process)

    # Start analytics
    process.start()

    # Return 204 (empty response) when the processing doesn't produce output files
    # to be stored into ISI
    # Otherwise return HTTP 200 status with json array containing paths of the
    # files which will be stored into ISI.
    #
    # IMPORTANT: All the files have to be placed inside the datalake provided
    
    return ('', 204)

    # return (jsonify(['file1.ext', 'file2.ext']), 200)
  except Exception as e:
    app.logger.exception(e)

    return (jsonify({'error': 'Error occured'}), 500)

@app.route('/stopAnalytics', methods = ['PUT'])
def do_stop_analytics():
  session_id = request.args.get('session_id')

  try:
    # Retrieve running analytics from pool
    analytics_pool = get_analytics_pool()
    process = analytics_pool.get(session_id)

    # Signal analytics to terminate
    process.terminate()

    analytics_pool.remove(session_id)

    return ('', 204)
  except KeyError:
    return (jsonify({'error': 'Analytics {} not running'.format(session_id)}), 500)
  except Exception as e:
    app.logger.exception(e)
    return (jsonify({'error': 'Error occured'}), 500)

if __name__ == '__main__':
  app.run(host = '0.0.0.0', port = 50000, debug = DEBUG)