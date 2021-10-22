import threading
import json
import requests
from ui_main_window import *
from PyQt5.QtCore import QTimer,QDateTime
from PyQt5.QtGui import QPixmap
from PyQt5.QtGui import QImage
from PyQt5.QtWidgets import QToolTip
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import *

from firebase import firebase
import yaml
import matplotlib as mp
import urllib
import http.client
import math
import datetime
import time
import numpy as np
import cv2
import sys


# import some PyQt5 modules


class MainWindow(QWidget):
    # class constructor
    def __init__(self):
        # call QWidget constructor
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        '''
        self.topFiller = QWidget()
        self.topFiller.setMinimumSize(250, 2000)
        self.scroll = QScrollArea()
        self.scroll.setWidget(self.topFiller)
        self.ui.Entrance.addWidget(self.scroll)
        '''
        self.detec = []
        self.count = 34
        #detec = []
        self.detect_y = []
        self.num = [0]
        # total remain parking space count
        self.remainA = 17
        self.remainB = 17
        # caculate center point's position
        self.offset = 2
        self.line_pos = 130
        # AVOID continuous counting
        # 1:   allow_count
        # 0:   disallow_count
        self.Iscount = 1
        # AVOID continuous counting in this time range
        self.restTime = 2
        # AVOID detec(x,y) remove again
        self.IsDOWNdetectRemove = 0
        self.IsUPdetectRemove = 0
        # allow upload to Cloud when count != pre_count
        # Assignment previous value(count) to pre_count
        self.pre_count = 34
        self.pre_countA = 17
        self.pre_countB = 17
        # Assignment cascadeDetect result to cars
        self.cars = 0

        # define da car in or out for traffic light (optional)
        self.Iscarin = 0

        # to check whether the carin or out
        self.framecount = 0
        self.Frame = 0

        # Car's direction
        # IN  :  1
        # OUT : -1
        self.direction = 0
        self.starttime = 0
        self.detail = ["","","","","",""]
        self.movement = "Initialization"
        self.lastFrame = 0
        
        self.firebase_url = 'https://test-7f2de.firebaseio.com/'
        self.key="Z61Y6gfIJzqhCWI5RHre35Xgsld8tvLZUWCWQ2Lo"
        self.authentication = firebase.FirebaseAuthentication(self.key, 'g0930421313@gmail.com')
        firebase.authentication = self.authentication 
        self.user = self.authentication.get_user() #獲取使用者資訊
        self.firebase = firebase.FirebaseApplication('https://test-7f2de.firebaseio.com/', authentication=self.authentication)
        
        self.firebase.put("/remain","Entrance",self.count)
        self.firebase.put("/remain","area_A",self.remainA)
        self.firebase.put("/remain","area_B",self.remainB)
        
        
        #print(datetime.toString())
        # load face cascade classifier
        self.car_cascade = cv2.CascadeClassifier('./car.xml')
        if self.car_cascade.empty():
            QMessageBox.information(self, "Error Loading cascade classifier",
                                    "Unable to load the Car cascade classifier xml file :(")
            #sys.exit()

        # create a timer
        self.timer = QTimer()
        self.timerA = QTimer()
        self.timerB = QTimer()
        self.timer2 = QTimer()
        self.timer_texttime = QTimer()
        self.timer_texttime.start()
        self.timer_texttime.timeout.connect(self.texttime)

        # set control_bt callback clicked  function
        
        self.cap = cv2.VideoCapture("./Entrance.mp4")
        self.capA = cv2.VideoCapture("./areaA.mp4")
        self.capB = cv2.VideoCapture("./areaB.mp4")
        
        self.ui.control_bt.clicked.connect(self.controlTimer)

        # set timer timeout callback function
        self.timer.timeout.connect(
            lambda: self.detectCarE(self.cap, self.ui.Entrance))
        self.timerA.timeout.connect(
            lambda: self.detectCarA(self.capA, self.ui.areaA))
        self.timerB.timeout.connect(
            lambda: self.detectCarB(self.capB, self.ui.areaB))

        self.ui.close_bt.clicked.connect(self.close_btn)
        #read YML
        self.ui.selectYML_btn.clicked.connect(self.getYMLpath)
        self.ui.confirm_path_btn.clicked.connect(self.confirmYMLpath)
    #####################space#########################################
        self.YMLPath = ""
        self.IsreadYML = False
        self.spaceopen = True
        if self.spaceopen == True:
            self.ui.control_bt.clicked.connect(self.detectspace)
            self.timer2.timeout.connect(self.detectspace)
        self.fn = "./parkinglot_1_480p.mp4"
        self.fn_yaml = ""
        self.capspace = cv2.VideoCapture(self.fn)
        self.config = {'save_video': False,
                       'text_overlay': True,
                       'parking_overlay': True,
                       'parking_id_overlay': True,
                       'parking_detection': True,
                       'motion_detection': False,
                       'pedestrian_detction': False,
                       'min_area_motion_contour': 200,
                       'park_laplacian_th': 1.8,
                       'park_sec_to_wait': 5,
                       'start_frame': 0}  # 35000
        self.video_info = {'fps': self.capspace.get(cv2.CAP_PROP_FPS),
                      'width':  int(self.capspace.get(cv2.CAP_PROP_FRAME_WIDTH)),
                      'height': int(self.capspace.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                      'fourcc': self.capspace.get(cv2.CAP_PROP_FOURCC),
                      'num_of_frames': int(self.capspace.get(cv2.CAP_PROP_FRAME_COUNT))}
        self.parking_contours = []  # Parking spaces four points
        self.parking_bounding_rects = []
        self.parking_mask = []
        self.pre_countSpace = int('100000000000000000',2)
        #self.countSpace = int('100000000000000000',2)
        self.capspace.set(cv2.CAP_PROP_POS_FRAMES,
                self.config['start_frame'])  # jump to frame
        '''
        if self.config['pedestrian_detction']:  # tracePeople
            self.hog = cv2.HOGDescriptor()
            self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        if self.config['motion_detection']:
            self.fgbg = cv2.createBackgroundSubtractorMOG2(
                history=300, varThreshold=16, detectShadows=True)
        '''
    
    #####################space#########################################
    def getYMLpath(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file',
                                            'home/stu/', "yml files (*.yml )")
        self.YMLPath = fname[0]
        
        self.ui.displayYMLpath.setText(self.YMLPath)
    def confirmYMLpath(self):
        self.fn_yaml = self.YMLPath
        with open(self.fn_yaml, 'r') as stream:
            self.parking_data = yaml.load(stream)  
        for park in self.parking_data:
                points = np.array(park['points'])
                rect = cv2.boundingRect(points)
                points_shifted = points.copy()
                points_shifted[:,0] = points[:,0] - rect[0] # shift contour to roi
                points_shifted[:,1] = points[:,1] - rect[1]
                self.parking_contours.append(points)

                self.parking_bounding_rects.append(rect)

                mask = cv2.drawContours(np.zeros((rect[3], rect[2]), dtype=np.uint8), [points_shifted], contourIdx=-1,
                                        color=255, thickness=-1, lineType=cv2.LINE_8)
                mask = mask == 255
                self.parking_mask.append(mask)
            #print(self.parking_bounding_rects)
        kernel_erode = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3)) # morphological kernel

        kernel_dilate = cv2.getStructuringElement(cv2.MORPH_RECT,(5,19))
        self.parking_status = [False]*len(self.parking_data)
        self.parking_buffer = [None]*len(self.parking_data)
        #print(self.parking_status)     
    def close_btn(self):
         # stop timer
        self.timer.stop()
        self.timerA.stop()
        self.timerB.stop()
        self.timer2.stop()
            # release video capture
        self.cap.release()
        self.capA.release()
        self.capB.release()
        self.capspace.release()
        QtWidgets.qApp.quit() 
    def textdetail(self):
        
        self.ui.text_detail.setText(str(self.detail[0])+"\n"+str(self.detail[1])+"\n"
            +str(self.detail[2])+"\n"+str(self.detail[3])+"\n"
            +str(self.detail[4])+"\n"+str(self.detail[5])+"\n")
    def texttime(self):
        t = time.time()
        date = datetime.datetime.fromtimestamp(t).strftime('%Y/%m/%d , %H:%M:%S')
        self.ui.Text_time.setText("現在時間 : "+date)

    def textCount(self,value):   
        self.ui.textCount.setText(str("入口 : ")+format(value))

    def textAremain(self, value):
        self.ui.textAremain.setText(str("A區  : ")+format(value))

    def textBremain(self, value):
        self.ui.textBremain.setText(str("B區  : ")+format(value))

    def Display(self, Qimg, Textlabel):
        Textlabel.setPixmap(QPixmap.fromImage(Qimg))

    def detectCarE(self, capV, labelshow):
        #print(self.text_detail)
        def catch_center(x, y, w, h):
            x1 = int(w / 2)
            y1 = int(h / 2)
            cx = x + x1
            cy = y + y1
            return cx, cy

        def center_y(x, y, w, h):
            x1 = int(w / 2)
            y1 = int(h / 2)
            cx = x + x1
            cy = y + y1
            return cy

        def post():
            '''
            
            self.detail.insert(0,str("Entrance : ")+post_to_thingspeak.post_to_thingspeak(params)+self.movement)
            self.textdetail()
            '''
            t = time.time()
            date = datetime.datetime.fromtimestamp(t).strftime('%Y/%m/%d , %H:%M:%S')
            #data = {'area':'A','remain':self.count}  
            self.firebase.put("/remain","Entrance",self.count)
            self.detail.insert(0,str("入口")+self.movement+'\n時間:'+date+'\n========================')
            self.textdetail()
            print("post_to_field1...")
    
        ret, frame = capV.read()
        
        if ret == False:
            QMessageBox.information(
                self, "Error Loading video", "Unable to load the Entrace video")
            self.timer.stop() 
            
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        self.cars = self.car_cascade.detectMultiScale(gray, 1.1, 10)

        cv2.line(frame, (25, self.line_pos),
                 (1200, self.line_pos), (255, 0, 0), 2)

        nowframetime = datetime.datetime.now()
        self.Iscarin = 0
        self.Frame += 1
        
        for (x, y, w, h) in self.cars:

            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

            self.Iscarin = 1
            center = catch_center(x, y, w, h)
            # print(self.detec)
            centery = center_y(x, y, w, h)
            self.detec.append(center)
            self.detect_y.append(centery)
            cv2.circle(frame, center, 4, (0, 0, 255), -1)
            startframetime = datetime.datetime.now()
            nowframetime = startframetime+datetime.timedelta(seconds=5)

            self.framecount += 1
            beforecount = self.framecount-3
            f1 = self.detect_y[self.framecount-1:self.framecount+1]
            f2 = self.detect_y[beforecount:beforecount+1]

            # 303,40
            num = list(map(lambda x: x[0]-x[1], zip(f1, f2)))

            self.direction = np.sign(num)

            for (x, y) in self.detec:

                if y < (self.line_pos+self.offset) and y > (self.line_pos-self.offset) and self.direction == 1:

                    if self.Iscount == 0:  # 0 remove x_y

                        endtime = datetime.datetime.now()
                        nowtime = self.starttime + \
                            datetime.timedelta(seconds=self.restTime)
                        self.detec.remove((x, y))
                        self.IsDOWNdetectRemove = 1
                        if endtime >= nowtime:
                            self.Iscount = 1
                    if self.Iscount == 1:

                        self.count -= 1

                        cv2.line(frame, (25, self.line_pos),
                                 (1200, self.line_pos), (0, 127, 255), 3)
                        if self.IsDOWNdetectRemove == 0:
                            self.detec.remove((x, y))
                        self.Iscount = 0
                        self.starttime = datetime.datetime.now()
                        #cv2.imwrite('frame%d.jpg'%Frame , frame)
                        # time.sleep(3)
                        self.lastFrame = self.Frame
                        print("Cars detected so far: "+str(self.count))
                        self.movement = "進來一輛車"

                if y > (self.line_pos-self.offset) and y < (self.line_pos+self.offset) and self.direction == -1:

                    if self.Iscount == 0:

                        endtime = datetime.datetime.now()
                        nowtime = self.starttime + \
                            datetime.timedelta(seconds=self.restTime)
                        self.detec.remove((x, y))
                        self.IsUPdetectRemove = 1
                        if endtime >= nowtime:
                            self.Iscount = 1
                    if self.Iscount == 1:

                        self.count += 1

                        cv2.line(frame, (25, self.line_pos),
                                 (1200, self.line_pos), (0, 127, 255), 3)
                        if self.IsUPdetectRemove == 0:
                            self.detec.remove((x, y))
                        self.Iscount = 0
                        self.starttime = datetime.datetime.now()
                        #cv2.imwrite('frame%d.jpg'%Frame , frame)
                        # time.sleep(3)
                        print("Cars detected so far: "+str(self.count))
                        self.movement ="出去一輛車"

            if self.pre_count != self.count:
                p = threading.Thread(target=post)
                p.start()
                # t.join()

            self.pre_count = self.count

        # time.sleep(0.15)
        if self.Iscarin == 1:
            cv2.circle(frame, (303, 40), 10, (0, 0, 255), -1)

        else:
            cv2.circle(frame, (303, 40), 10, (0, 255, 0), -1)
        self.Iscarin = 0
        if self.Frame == self.lastFrame+300:
            self.movement = ""
            self.lastFrame = 0

        # display the resulting frame

        self.textCount(self.count)
        # self.textAremain(self.remainA)
        # self.textBremain(self.remainB)
        cv2.putText(frame, "E", (27, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
       
        # get frame infos
        height, width, channel = frame.shape

        step = channel * width

        # create QImage from RGB frame
        qImg = QImage(frame.data, width, height, step, QImage.Format_RGB888)
        # show frame in img_label
        labelshow.setPixmap(QPixmap.fromImage(qImg))

    def detectCarA(self, capV, labelshow):

        def catch_center(x, y, w, h):
            x1 = int(w / 2)
            y1 = int(h / 2)
            cx = x + x1
            cy = y + y1
            return cx, cy

        def center_y(x, y, w, h):
            x1 = int(w / 2)
            y1 = int(h / 2)
            cx = x + x1
            cy = y + y1
            return cy

        def post():
            t = time.time()
            date = datetime.datetime.fromtimestamp(t).strftime('%Y/%m/%d , %H:%M:%S')
            #data = {'area':'A','remain':self.count}  
            self.firebase.put("/remain","area_A",self.remainA)
            self.detail.insert(0,str("A區")+self.movement+'\n時間:'+date+'\n========================')
            self.textdetail()
            print("post_to_field2...")

        

        ret, frame = capV.read()
        if ret == False:
            
            QMessageBox.information(
                self, "Error Loading video", "Unable to load the areaA video")
            self.timerA.stop() 

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        self.cars = self.car_cascade.detectMultiScale(gray, 1.1, 10)

        cv2.line(frame, (25, self.line_pos),
                 (1200, self.line_pos), (255, 0, 0), 2)

        nowframetime = datetime.datetime.now()
        self.Iscarin = 0
        self.Frame += 1

        for (x, y, w, h) in self.cars:

            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

            self.Iscarin = 1
            center = catch_center(x, y, w, h)
            # print(self.detec)
            centery = center_y(x, y, w, h)
            self.detec.append(center)
            self.detect_y.append(centery)
            cv2.circle(frame, center, 4, (0, 0, 255), -1)
            startframetime = datetime.datetime.now()
            nowframetime = startframetime+datetime.timedelta(seconds=5)

            self.framecount += 1
            beforecount = self.framecount-3
            f1 = self.detect_y[self.framecount-1:self.framecount+1]
            f2 = self.detect_y[beforecount:beforecount+1]

            # 303,40
            num = list(map(lambda x: x[0]-x[1], zip(f1, f2)))

            self.direction = np.sign(num)

            for (x, y) in self.detec:

                if y < (self.line_pos+self.offset) and y > (self.line_pos-self.offset) and self.direction == 1:

                    if self.Iscount == 0:  # 0 remove x_y

                        endtime = datetime.datetime.now()
                        nowtime = self.starttime + \
                            datetime.timedelta(seconds=self.restTime)
                        self.detec.remove((x, y))
                        self.IsDOWNdetectRemove = 1
                        if endtime >= nowtime:
                            self.Iscount = 1
                    if self.Iscount == 1:

                        self.remainA -= 1

                        cv2.line(frame, (25, self.line_pos),
                                 (1200, self.line_pos), (0, 127, 255), 3)
                        if self.IsDOWNdetectRemove == 0:
                            self.detec.remove((x, y))
                        self.Iscount = 0
                        self.starttime = datetime.datetime.now()
                        #cv2.imwrite('frame%d.jpg'%Frame , frame)
                        # time.sleep(3)
                        self.lastFrame = self.Frame
                        print("Cars detected so far: "+str(self.remainA))
                        self.movement = "進來一輛車"

                if y > (self.line_pos-self.offset) and y < (self.line_pos+self.offset) and self.direction == -1:

                    if self.Iscount == 0:

                        endtime = datetime.datetime.now()
                        nowtime = self.starttime + \
                            datetime.timedelta(seconds=self.restTime)
                        self.detec.remove((x, y))
                        self.IsUPdetectRemove = 1
                        if endtime >= nowtime:
                            self.Iscount = 1
                    if self.Iscount == 1:

                        self.remainA += 1

                        cv2.line(frame, (25, self.line_pos),
                                 (1200, self.line_pos), (0, 127, 255), 3)
                        if self.IsUPdetectRemove == 0:
                            self.detec.remove((x, y))
                        self.Iscount = 0
                        self.starttime = datetime.datetime.now()
                        #cv2.imwrite('frame%d.jpg'%Frame , frame)
                        # time.sleep(3)
                        print("Cars detected so far: "+str(self.remainA))
                        self.movement = "出去一輛車"

            if self.pre_countA != self.remainA:
                p = threading.Thread(target=post)
                p.start()
                # t.join()

            self.pre_countA = self.remainA

        # time.sleep(0.15)
        if self.Iscarin == 1:
            cv2.circle(frame, (303, 40), 10, (0, 0, 255), -1)

        else:
            cv2.circle(frame, (303, 40), 10, (0, 255, 0), -1)
        self.Iscarin = 0
        if self.Frame == self.lastFrame+300:
            self.movement = ""
            self.lastFrame = 0

        # display the resulting frame

        # self.textCount(self.count)
        self.textAremain(self.remainA)
        # self.textBremain(self.remainB)
        cv2.putText(frame, "A", (27, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
        
        # get frame infos
        height, width, channel = frame.shape
        step = channel * width

        # create QImage from RGB frame
        qImg = QImage(frame.data, width, height, step, QImage.Format_RGB888)
        # show frame in img_label
        labelshow.setPixmap(QPixmap.fromImage(qImg))

    def detectCarB(self, capV, labelshow):

        def catch_center(x, y, w, h):
            x1 = int(w / 2)
            y1 = int(h / 2)
            cx = x + x1
            cy = y + y1
            return cx, cy

        def center_y(x, y, w, h):
            x1 = int(w / 2)
            y1 = int(h / 2)
            cx = x + x1
            cy = y + y1
            return cy

        def post():
            t = time.time()
            date = datetime.datetime.fromtimestamp(t).strftime('%Y/%m/%d , %H:%M:%S')
            #data = {'area':'A','remain':self.count}  
            self.firebase.put("/remain","area_B",self.remainB)
            self.detail.insert(0,str("B區")+self.movement+'\n時間:'+date+'\n========================')
            self.textdetail()
            print("post_to_field3...")

       

        #ini = threading.Thread(target = init)
        # ini.start()

        # resize frame image
        # while True:

        ret, frame = capV.read()
        if ret == False:
            
            QMessageBox.information(
                self, "Error Loading video", "Unable to load the areaB video")
            self.timerB.stop() 

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        self.cars = self.car_cascade.detectMultiScale(gray, 1.1, 10)

        cv2.line(frame, (25, self.line_pos),
                 (1200, self.line_pos), (255, 0, 0), 2)

        nowframetime = datetime.datetime.now()
        self.Iscarin = 0
        self.Frame += 1
        
        for (x, y, w, h) in self.cars:

            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

            self.Iscarin = 1
            center = catch_center(x, y, w, h)
            # print(self.detec)
            centery = center_y(x, y, w, h)
            self.detec.append(center)
            self.detect_y.append(centery)
            cv2.circle(frame, center, 4, (0, 0, 255), -1)
            startframetime = datetime.datetime.now()
            nowframetime = startframetime+datetime.timedelta(seconds=5)

            self.framecount += 1
            beforecount = self.framecount-3
            f1 = self.detect_y[self.framecount-1:self.framecount+1]
            f2 = self.detect_y[beforecount:beforecount+1]

            # 303,40
            num = list(map(lambda x: x[0]-x[1], zip(f1, f2)))

            self.direction = np.sign(num)

            for (x, y) in self.detec:

                if y < (self.line_pos+self.offset) and y > (self.line_pos-self.offset) and self.direction == 1:

                    if self.Iscount == 0:  # 0 remove x_y

                        endtime = datetime.datetime.now()
                        nowtime = self.starttime + \
                            datetime.timedelta(seconds=self.restTime)
                        self.detec.remove((x, y))
                        self.IsDOWNdetectRemove = 1
                        if endtime >= nowtime:
                            self.Iscount = 1
                    if self.Iscount == 1:

                        self.remainB -= 1

                        cv2.line(frame, (25, self.line_pos),
                                 (1200, self.line_pos), (0, 127, 255), 3)
                        if self.IsDOWNdetectRemove == 0:
                            self.detec.remove((x, y))
                        self.Iscount = 0
                        self.starttime = datetime.datetime.now()
                        #cv2.imwrite('frame%d.jpg'%Frame , frame)
                        # time.sleep(3)
                        self.lastFrame = self.Frame
                        print("Cars detected so far: "+str(self.remainB))
                        self.movement = "進來一輛車"

                if y > (self.line_pos-self.offset) and y < (self.line_pos+self.offset) and self.direction == -1:

                    if self.Iscount == 0:

                        endtime = datetime.datetime.now()
                        nowtime = self.starttime + \
                            datetime.timedelta(seconds=self.restTime)
                        self.detec.remove((x, y))
                        self.IsUPdetectRemove = 1
                        if endtime >= nowtime:
                            self.Iscount = 1
                    if self.Iscount == 1:

                        self.remainB += 1

                        cv2.line(frame, (25, self.line_pos),
                                 (1200, self.line_pos), (0, 127, 255), 3)
                        if self.IsUPdetectRemove == 0:
                            self.detec.remove((x, y))
                        self.Iscount = 0
                        self.starttime = datetime.datetime.now()
                        #cv2.imwrite('frame%d.jpg'%Frame , frame)
                        # time.sleep(3)
                        print("Cars detected so far: "+str(self.remainB))
                        self.movement = "出去一輛車"

            if self.pre_countB != self.remainB:
                p = threading.Thread(target=post)
                p.start()
                # t.join()

            self.pre_countB = self.remainB

        # time.sleep(0.15)
        if self.Iscarin == 1:
            cv2.circle(frame, (303, 40), 10, (0, 0, 255), -1)

        else:
            cv2.circle(frame, (303, 40), 10, (0, 255, 0), -1)
        self.Iscarin = 0
        if self.Frame == self.lastFrame+300:
            self.movement = ""
            self.lastFrame = 0

        # display the resulting frame

        # self.textCount(self.count)
        self.textBremain(self.remainB)
        # self.textBremain(self.remainB)
        cv2.putText(frame, "B", (27, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
       
        # get frame infos
        height, width, channel = frame.shape
        step = channel * width

        # create QImage from RGB frame
        qImg = QImage(frame.data, width, height, step, QImage.Format_RGB888)
        # show frame in img_label
        labelshow.setPixmap(QPixmap.fromImage(qImg))

    def detectspace(self):
       #print(self.config)
        def job():
            self.firebase.put("/parkingspace","space",int(countSpace))
            print("post_to_field4...")
            
        
        
        
        
        # Create Background subtractor
        
       
       
        video_cur_pos = self.capspace.get(cv2.CAP_PROP_POS_MSEC) / 1000.0 # Current position of the video file in seconds
        video_cur_frame = self.capspace.get(cv2.CAP_PROP_POS_FRAMES) # Index of the frame to be decoded/captured next
        ret, frame = self.capspace.read()    
        if ret == False:
            
            QMessageBox.information(
                    self, "Error Loading video", "Unable to load the parkingspace video")
            self.timer2.stop()

          
    
        #frame_gray = cv2.cvtColor(frame.copy(), cv2.COLOR_BGR2GRAY)
        # Background Subtraction
        frame_blur = cv2.GaussianBlur(frame.copy(), (5,5), 3)
        frame_gray = cv2.cvtColor(frame_blur, cv2.COLOR_BGR2GRAY)
        frame_out = frame.copy()
    
    # Draw Overlay
        '''
        if self.config['text_overlay']:
            str_on_frame = "%d/%d" % (video_cur_frame, self.video_info['num_of_frames'])
            #textframecount
            cv2.putText(frame_out, str_on_frame, (5,30), cv2.FONT_HERSHEY_SIMPLEX,
                        0.8, (0,0,255), 2, cv2.LINE_AA)
        '''
        
        if self.config['motion_detection']:
            fgmask = self.fgbg.apply(frame_blur)
            bw = np.uint8(fgmask==255)*255    
            bw = cv2.erode(bw, kernel_erode, iterations=1)
            bw = cv2.dilate(bw, kernel_dilate, iterations=1)
            (_, cnts, _) = cv2.findContours(bw.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            # loop over the contours
            for c in cnts:
                # if the contour is too small, ignore it
                if cv2.contourArea(c) < self.config['min_area_motion_contour']:
                    continue
            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(frame_out, (x, y), (x + w, y + h), (255, 255, 255), 2)             
               
        if self.config['parking_detection']:        
            for ind, park in enumerate(self.parking_data):
                points = np.array(park['points'])
                rect = self.parking_bounding_rects[ind]
                roi_gray = frame_gray[rect[1]:(rect[1]+rect[3]), rect[0]:(rect[0]+rect[2])] # crop roi for faster calcluation            
                laplacian = cv2.Laplacian(roi_gray, cv2.CV_64F)
                points[:,0] = points[:,0] - rect[0] # shift contour to roi
                points[:,1] = points[:,1] - rect[1]
                delta = np.mean(np.abs(laplacian * self.parking_mask[ind]))
                status = delta < self.config['park_laplacian_th']
                # If detected a change in parking status, save the current time
                if status != self.parking_status[ind] and self.parking_buffer[ind]==None:
                    self.parking_buffer[ind] = video_cur_pos
                # If status is still different than the one saved and counter is open
                elif status != self.parking_status[ind] and self.parking_buffer[ind]!=None:
                    if video_cur_pos - self.parking_buffer[ind] > self.config['park_sec_to_wait']:
                        self.parking_status[ind] = status
                        self.parking_buffer[ind] = None
                # If status is still same and counter is open                    
                elif status == self.parking_status[ind] and self.parking_buffer[ind]!=None:
                    #if video_cur_pos - parking_buffer[ind] > config['park_sec_to_wait']:
                    self.parking_buffer[ind] = None                    
                #print("#%d: %.2f" % (ind, delta))
            #print(self.parking_buffer)
            
        if self.config['parking_overlay']:  
            
            countSpace = int('100000000000000000',2)
            for ind, park in enumerate(self.parking_data):
                points = np.array(park['points'])
                if self.parking_status[ind]:
                    countSpace+=pow(2,ind)
                    color = (255,0,0)#if no car change color
                #print(parking_status[ind])
                else: color = (0,0,255)
                
                
                countSpace << 1
                cv2.drawContours(frame_out, [points], contourIdx=-1,
                                color=color, thickness=2, lineType=cv2.LINE_8)            
                moments = cv2.moments(points)
                ##textID  
                
                centroid = (int(moments['m10']/moments['m00'])-3, int(moments['m01']/moments['m00'])+3)
                cv2.putText(frame_out, str(park['id']), (centroid[0]+1, centroid[1]+1), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1, cv2.LINE_AA)
                cv2.putText(frame_out, str(park['id']), (centroid[0]-1, centroid[1]-1), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1, cv2.LINE_AA)
                cv2.putText(frame_out, str(park['id']), (centroid[0]+1, centroid[1]-1), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1, cv2.LINE_AA)
                cv2.putText(frame_out, str(park['id']), (centroid[0]-1, centroid[1]+1), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0), 1, cv2.LINE_AA)
                cv2.putText(frame_out, str(park['id']), centroid, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1, cv2.LINE_AA)
            #print(str(ind)+" : ") 
            #print(str(countSpace))
            
                
            cv2.putText(frame_out,format(countSpace,'b'),(7,97), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 3)
            
            if self.pre_countSpace!=countSpace:
                p = threading.Thread(target = job)
                p.start()
                
                
            self.pre_countSpace = countSpace    
        if self.config['pedestrian_detction']:          
            # detect people in the image
            (rects, weights) = self.hog.detectMultiScale(frame, winStride=(4, 4), padding=(8, 8), scale=1.05)
        
            # draw the original bounding boxes
            for (x, y, w, h) in rects:
                cv2.rectangle(frame_out, (x, y), (x + w, y + h), (255, 0, 0), 2)
        #print(frame_out.shape)
        height, width, channel = frame_out.shape
        step = channel * width
        #print(self.countSpace)
        # create QImage from RGB frame
        spaceqImg = QImage(frame_out.data, width, height, step, QImage.Format_RGB888)
        # show frame in img_label
        self.ui.parkspace.setPixmap(QPixmap.fromImage(spaceqImg))       
        # start/stop timer

    def controlTimer(self):
        # if timer is stopped
        if not self.timer.isActive():
            # create video capture
            #self.cap = self.cap
            
            self.textdetail()
            self.cap = cv2.VideoCapture("./Entrance.mp4")
            self.capA = cv2.VideoCapture("./areaA.mp4")
            self.capB = cv2.VideoCapture("./areaB.mp4")
            if self.spaceopen ==True:
                self.fn = r"./parkinglot_1_480p.mp4"
                self.fn_yaml = r"./parking2.yml"
                self.capspace = cv2.VideoCapture(self.fn)
            # start timer
            self.timer.start(5)
            self.timerA.start(5)
            self.timerB.start(5)
            self.timer2.start(5)
            # update control_bt text
            self.ui.control_bt.setText("暫停")
        # if timer is started
        else:
            # stop timer
            self.timer.stop()
            self.timerA.stop()
            self.timerB.stop()
            self.timer2.stop()
            # release video capture
            self.cap.release()
            self.capA.release()
            self.capB.release()
            self.capspace.release()
            # update control_bt text
            self.ui.control_bt.setText("開始")
if __name__ == '__main__':
    app = QApplication(sys.argv)

    # create and show mainWindow
    mainWindow = MainWindow()
    mainWindow.show()

    sys.exit(app.exec_())

