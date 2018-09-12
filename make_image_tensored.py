import os
import cv2
import numpy as np
import tensorflow as tf
import json
from threading import Thread
from queue import Queue
import time
from jsontocsv import read_json_files
import pandas as pd
import logging
import sys

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' #for remove tf warnings

MODEL_NAME = 'faster_rcnn_inception_v2_coco_2018_01_28'
IMAGE_PATH = 'pins/q/'
PATH_TO_CKPT = os.path.join(os.getcwd(),MODEL_NAME,'frozen_inference_graph.pb')
PATH_TO_FOLDER= os.path.join(os.getcwd(),IMAGE_PATH)

class infos:
    IMAGE_PATH = IMAGE_PATH
    PATH_TO_FOLDER = PATH_TO_FOLDER
    CSV_NAME = f"humans_for_{IMAGE_PATH.replace('/','_').strip('_')}_csv.csv"
    logger = None
    jsons = []

def set_session():
    try:
        detection_graph = tf.Graph()
        with detection_graph.as_default():
            od_graph_def = tf.GraphDef()
            with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')

            sess = tf.Session(graph=detection_graph)
            return sess,detection_graph
    except Exception as e:
        infos.logger.error(f"Error in {sys._getframe().f_code.co_name} function! Here error is: {e}")

def set_tensors():
    try:
        image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
        detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
        detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
        detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')
        num_detections = detection_graph.get_tensor_by_name('num_detections:0')

        return image_tensor,detection_boxes,detection_scores,detection_classes,num_detections
    except Exception as e:
        infos.logger.error(f"Error in {sys._getframe().f_code.co_name} function! Here error is: {e}")

def find_faces_in_image(PATH_TO_FOLDER,PATH,sess,image_tensor,detection_boxes,detection_scores,detection_classes,num_detections,show,save_to_folder):
        try:
            image = cv2.imread(PATH)
            image_expanded = np.expand_dims(image, axis=0)
            try:
                height, width, _ = image.shape
            except Exception as e:
                infos.logger.error(f"Error in {sys._getframe().f_code.co_name} function! Here error is: {e}")

            (boxes, scores, classes, num) = sess.run(
                [detection_boxes, detection_scores, detection_classes, num_detections],
                feed_dict={image_tensor: image_expanded})

            humans = []
            for scr in np.squeeze(scores):#all of scores
                if(scr >= 0.8):#kind of threshold
                    for ias in np.where(np.squeeze(scores) == scr)[0]:#get all scores that can passed threshold
                        if int(np.squeeze(classes).astype(np.int32)[ias]) == 1:#if human
                            i = int(ias)
                            ymin = int((boxes[0][i][0] * height))
                            xmin = int((boxes[0][i][1] * width))
                            ymax = int((boxes[0][i][2] * height))
                            xmax = int((boxes[0][i][3] * width))

                            w = xmax-xmin
                            h = ymax-ymin
                            y = ymin
                            x = xmin

                            humans.append(
                                {
                                    "x":x, "y":y, "w":w, "h":h,
                                    "img_w":width, "img_h":height ,
                                    "path":PATH ,"gender":"unknown",
                                    "xmax":xmax,"ymax":ymax
                                }
                            )

                            if show:
                                try:
                                    result = np.array(image[y:y + h, x:x + w])
                                    cv2.imshow('human', result)
                                    cv2.imshow('image', image)
                                    cv2.waitKey(0)
                                    cv2.destroyAllWindows()
                                except Exception as e:
                                    print(e)
                                    pass

                            if save_to_folder:
                                result = np.array(image[y:y + h, x:x + w])
                                cv2.imwrite(os.path.join(PATH_TO_FOLDER,"tensored_images/")+f"face{PATH.rstrip('/').split('/')[-1]}{i}.png",result)

            return humans

        except Exception as e:
            infos.logger.error(f"Error in {sys._getframe().f_code.co_name} function! Here error is: {e}")

def to_json(humans,PATH):
    try:
        JSON_PATH = PATH + ".json"
        dicts = []
        for human in humans:#['filename', 'width', 'height', 'class', 'xmin', 'ymin', 'xmax', 'ymax']
            dicts.append(
                {
                    "filename": human["path"],
                    "width": human["img_w"], "height": human["img_h"],
                    "class": "person",
                    "xmin":human["x"],"ymin":human["y"],"xmax":human["xmax"],"ymax":human["ymax"],
                    "w":human["w"],"h":human["h"],
                    "gender":human["gender"]
                }
            )

        with open(JSON_PATH,"w") as file:
            json.dump(dicts, file)

        infos.jsons.append(JSON_PATH)
        return dicts

    except Exception as e:
        infos.logger.error(f"Error in {sys._getframe().f_code.co_name} function! Here error is: {e}")

def all_images_in_folder(FOLDER_PATH,que):
    try:
        for PATH in os.listdir(FOLDER_PATH):
            if(PATH.endswith(".png") or PATH.endswith(".jpg")):
                que.put(os.path.join(FOLDER_PATH,PATH))

    except Exception as e:
        infos.logger.error(f"Error in {sys._getframe().f_code.co_name} function! Here error is: {e}")

def que_chechker(PATH_TO_FOLDER,que,show,save_to_folder):
    tojson = True
    try:
        while True:
            path = que.get()
            face_finder(PATH_TO_FOLDER,path,tojson,show,save_to_folder)
            que.task_done()

    except Exception as e:
        infos.logger.error(f"Error in {sys._getframe().f_code.co_name} function! Here error is: {e}")

def face_finder(PATH_TO_FOLDER,PATH,tojson,show,save_to_folder):
    try:
        del tojson
        humans = find_faces_in_image(PATH_TO_FOLDER,PATH,sess,image_tensor,detection_boxes,detection_scores,detection_classes,num_detections,show,save_to_folder)
        to_json(humans,PATH)
    except Exception as e:
        infos.logger.error(f"Error in {sys._getframe().f_code.co_name} function! Here error is: {e}")

def start_tensoring(PATH_TO_FOLDER,show = False,save_to_folder = False):
    try:
        json_que = Queue()
        th = int(len(os.listdir(PATH_TO_FOLDER)) / 20)
        if th == 0:
            th = 1

        if save_to_folder:
            try:
                os.mkdir(os.path.join(PATH_TO_FOLDER,"tensored_images/"))
            except FileExistsError as e:
                infos.logger.warning(f"Filename that {os.path.join(PATH_TO_FOLDER,'tensored_images/')} already exists. I'm not gonna create again ")
                pass
            except Exception as e:
                infos.logger.error(f"Error in {sys._getframe().f_code.co_name} function! Here error is: {e}")

        for i in range(th):
            t = Thread(target=que_chechker, args=(PATH_TO_FOLDER,json_que,show,save_to_folder))
            t.daemon = True
            t.start()

        all_images_in_folder(PATH_TO_FOLDER, json_que)
        json_que.join()

    except Exception as e:
        infos.logger.error(f"Error in {sys._getframe().f_code.co_name} function! Here error is: {e}")

def delete_jsons():
    for jsf in infos.jsons:
        try:
            os.remove(jsf)
        except FileNotFoundError:
            infos.logger.warning(f"File named {jsf} can't delete. It might be deleted before, I'm not gonna try delete this again")
            pass
        except Exception as e:
            infos.logger.error(f"Error in {sys._getframe().f_code.co_name} function! Here error is: {e}")

def set_loger(name='tensor',level = 2):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    ch = logging.StreamHandler()
    ch.setLevel(level)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    ch.setFormatter(formatter)
    logger.addHandler(ch)

    return logger

if __name__ == "__main__":

    infos.logger = set_loger()

    t1 = time.time()
    infos.logger.info("Starting...")

    sess, detection_graph = set_session()
    infos.logger.info("Session created")
    image_tensor, detection_boxes, detection_scores, detection_classes, num_detections = set_tensors()
    infos.logger.info("Sensors created")
    infos.logger.info("Starting to find faces...")
    start_tensoring(PATH_TO_FOLDER,show = False,save_to_folder = True)
    infos.logger.info("Faces founded")

    infos.logger.info("Starting to make json files csv file...")
    dataframes = read_json_files(infos.PATH_TO_FOLDER)
    csv_data = pd.concat(dataframes)
    csv_data.to_csv(os.path.join(infos.PATH_TO_FOLDER, infos.CSV_NAME), index=None)
    infos.logger.info("All json files converted to csv file")

    infos.logger.info("Starting to delete json files...")
    delete_jsons()
    infos.logger.info("All json files deleted")

    infos.logger.info(f"All jobes done in {round(time.time() - t1,2)} seconds -God")

