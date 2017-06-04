#!/usr/bin/python3

import argparse
import datetime
import json
import sys
import time
import warnings
from cv2 import VideoCapture

import bypy
import cv2

from package.deamon import Daemon
from package.tempimage import TempImage


class MyDeamon(Daemon):
    width=None
    height=None
    brightness=None

    def run(self):
        monitor()

def monitor():
    cam = VideoCapture()
    if cam.open(0):
        cam.set(cv2.CAP_PROP_FRAME_WIDTH, conf["width"])
        cam.set(cv2.CAP_PROP_FRAME_HEIGHT, conf["height"])
        #cam.set(cv2.CAP_PROP_BRIGHTNESS, conf["brightness"])
        #cam.set(cv2.CAP_PROP_CONTRAST,conf["contrast"])
        #cam.set(cv2.CAP_PROP_SATURATION, conf["saturation"])
        #cam.set(cv2.CAP_PROP_GAIN, conf["gain"])

        while True:
            ret, frame = cam.read()
            print("camera start...")
            uploadimg(frame)
            time.sleep(conf["inc"] * 60)
    cam.release()
    print("camera stop...")

def uploadimg(frame):
    t=TempImage()
    dst=cv2.resize(frame,None,fx=0.5,fy=0.5,interpolation=cv2.INTER_CUBIC)
    cv2.imwrite(t.path,dst)
    remotedir = time.strftime("%Y-%m-%d", time.localtime())
    yesterdaydir = (datetime.datetime.now() + datetime.timedelta(days=-1)).date().strftime("%Y-%m-%d")
    bp = bypy.ByPy()
    bp.remove(yesterdaydir)
    bp.mkdir(remotedir)
    bp.upload(t.path, remotedir)
    print("upload: "+t.path)
    t.cleanup()

if __name__=="__main__":
    # 构建 argument parser 并解析参数
    ap = argparse.ArgumentParser()
    ap.add_argument("<option>", help="start|stop|restart to control this program")
    args = vars(ap.parse_args())
    # 过滤警告，加载配置文件
    warnings.filterwarnings("ignore")
    conf = json.load(open("./conf.json"))
    option =args["<option>"]
    dm=MyDeamon("/tmp/monitor.pid")
    if option=='start':
        #dm.conf=conf
        #dm.start()
        monitor()
    elif option=='stop':
        dm.stop()
    elif option=='restart':
        dm.restart()
    else:
        ap.error("unrecognized arguments: "+option)
        sys.exit(3)
    sys.exit(0)
