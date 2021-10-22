import json
import requests
from firebase import firebase
from second import *
from PyQt5.QtCore import *
from PyQt5.QtCore import QTimer,QDateTime
from PyQt5.QtGui import QPixmap
from PyQt5.QtGui import QImage
from PyQt5.QtWidgets import QToolTip
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QGridLayout

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
sys.path.append(r"/home/stu/aaa")

class MainWindow(QWidget):
    # class constructor
    def __init__(self):
        # call QWidget constructor
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.timer = QTimer()
        self.timer.start()
        self.timer.timeout.connect(self.Entrance_Get)
        self.timer.timeout.connect(self.RemainA_Get)
        self.timer.timeout.connect(self.RemainB_Get)
        self.timer.timeout.connect(self.Parking_Space)
        #self.timer.timeout.connect(self.text_Aremain)
        self.totalvalue = 0
        self.pre_totalvalue = 0
        self.remain_E = 0
        self.remain_RA = 0
        self.remain_RB = 0
        self.firebase_url = 'https://test-7f2de.firebaseio.com/'
        self.key="Z61Y6gfIJzqhCWI5RHre35Xgsld8tvLZUWCWQ2Lo"
        self.authentication = firebase.FirebaseAuthentication(self.key, 'g0930421313@gmail.com')
        firebase.authentication = self.authentication 
        self.user = self.authentication.get_user() #獲取使用者資訊
        self.firebase = firebase.FirebaseApplication('https://test-7f2de.firebaseio.com/', authentication=self.authentication)
        self.count=0
        self.position = ["","","","","","","","","","","","","","","","","","",""]
        self.position1 = ["","","","","","","","","","","","","","","","","","",""]
        
    def Reset(self):
            self.ui.zero.setStyleSheet("background-color: black;")
            self.ui.one.setStyleSheet("background-color: black;")
            self.ui.two.setStyleSheet("background-color: black;")
            self.ui.three.setStyleSheet("background-color: black;")
            self.ui.four.setStyleSheet("background-color: black;")      
            self.ui.five.setStyleSheet("background-color: black;")
            self.ui.six.setStyleSheet("background-color: black;")
            self.ui.seven.setStyleSheet("background-color: black;")
            self.ui.eight.setStyleSheet("background-color: black;")
            self.ui.nine.setStyleSheet("background-color: black;")
            self.ui.ten.setStyleSheet("background-color: black;")
            self.ui.eleven.setStyleSheet("background-color: black;")
            self.ui.twelve.setStyleSheet("background-color: black;")
            self.ui.thirteen.setStyleSheet("background-color: black;")
            self.ui.fourteen.setStyleSheet("background-color: black;")
            self.ui.fifteen.setStyleSheet("background-color: black;")
            self.ui.sixteen.setStyleSheet("background-color: black;")
            self.ui.num0.setStyleSheet("background-color: black;")
            self.ui.num1.setStyleSheet("background-color: black;")
            self.ui.num2.setStyleSheet("background-color: black;")
            self.ui.num3.setStyleSheet("background-color: black;")
            self.ui.num4.setStyleSheet("background-color: black;")
            self.ui.num5.setStyleSheet("background-color: black;")
            self.ui.num6.setStyleSheet("background-color: black;")
            self.ui.num7.setStyleSheet("background-color: black;")
            self.ui.num8.setStyleSheet("background-color: black;")
            self.ui.num9.setStyleSheet("background-color: black;")
            self.ui.num10.setStyleSheet("background-color: black;")
            self.ui.num11.setStyleSheet("background-color: black;")
            self.ui.num12.setStyleSheet("background-color: black;")
            self.ui.num13.setStyleSheet("background-color: black;")
            self.ui.num14.setStyleSheet("background-color: black;")
            self.ui.num15.setStyleSheet("background-color: black;")
            self.ui.num16.setStyleSheet("background-color: black;")

    def Entrance_Get(self):
            remain_E = self.firebase.get("/remain","Entrance")
            self.ui.text_count.setText(format(remain_E))
        
    def RemainA_Get(self):
            remain_RA = self.firebase.get("/remain","area_A")
            self.ui.text_A.setText(format(remain_RA))

    def RemainB_Get(self):
            remain_RB = self.firebase.get("/remain","area_B")
            self.ui.text_B.setText(format(remain_RB))
    def keyPressEvent(self, event):
            if  (event.key() == Qt.Key_Q):
              #print('qqqq')
              self.timer.stop()
              self.close()
    
    def Parking_Space(self):
            self.count = 0
            
            self.totalvalue = self.firebase.get("/parkingspace","space")
            if self.totalvalue!= self.pre_totalvalue:
                self.Reset()
                self.position = ["","","","","","","","","","","","","","","",""]
                self.position1 = ["","","","","","","","","","","","","","","",""]
                while(self.count<17):
                        if int(self.totalvalue) % 2 == 1:
                                
                                print(self.count)
                                
                                if self.count == 0 :
                                        self.position.insert(0,self.count)
                                        self.ui.zero.setStyleSheet("background-color: red; color: white")
                                        self.position1.insert(0,self.count)
                                        self.ui.num0.setStyleSheet("background-color: red; color: white")
                                elif self.count == 1 :
                                        self.position.insert(1,self.count)
                                        self.ui.one.setStyleSheet("background-color: red; color: white")
                                        self.position1.insert(1,self.count)
                                        self.ui.num1.setStyleSheet("background-color: red; color: white")
                                elif self.count == 2 :
                                        self.position.insert(2,self.count)
                                        self.ui.two.setStyleSheet("background-color: red; color: white")
                                        self.position1.insert(2,self.count)
                                        self.ui.num2.setStyleSheet("background-color: red; color: white")
                                elif self.count == 3 :
                                        self.position.insert(3,self.count)
                                        self.ui.three.setStyleSheet("background-color: red; color: white")
                                        self.position1.insert(3,self.count)
                                        self.ui.num3.setStyleSheet("background-color: red; color: white")
                                elif self.count == 4 :
                                        self.position.insert(4,self.count)
                                        self.ui.four.setStyleSheet("background-color: red; color: white")
                                        self.position1.insert(4,self.count)
                                        self.ui.num4.setStyleSheet("background-color: red; color: white")  
                                elif self.count == 5 :
                                        self.position.insert(5,self.count)
                                        self.ui.five.setStyleSheet("background-color: red; color: white")
                                        self.position1.insert(5,self.count)
                                        self.ui.num5.setStyleSheet("background-color: red; color: white")
                                elif self.count == 6 :
                                        self.position.insert(6,self.count)
                                        self.ui.six.setStyleSheet("background-color: red; color: white")
                                        self.position1.insert(6,self.count)
                                        self.ui.num6.setStyleSheet("background-color: red; color: white")
                                elif self.count == 7 :
                                        self.position.insert(7,self.count)
                                        self.ui.seven.setStyleSheet("background-color: red; color: white")
                                        self.position1.insert(7,self.count)
                                        self.ui.num7.setStyleSheet("background-color: red; color: white")    
                                elif self.count == 8 :
                                        self.position.insert(8,self.count)
                                        self.ui.eight.setStyleSheet("background-color: red; color: white")
                                        self.position1.insert(8,self.count)
                                        self.ui.num8.setStyleSheet("background-color: red; color: white")
                                elif self.count == 9 :
                                        self.position.insert(9,self.count)
                                        self.ui.nine.setStyleSheet("background-color: red; color: white")
                                        self.position1.insert(9,self.count)
                                        self.ui.num9.setStyleSheet("background-color: red; color: white")
                                elif self.count == 10 :
                                        self.position.insert(10,self.count)
                                        self.ui.ten.setStyleSheet("background-color: red; color: white")
                                        self.position1.insert(10,self.count)
                                        self.ui.num10.setStyleSheet("background-color: red; color: white")
                                elif self.count == 11 :
                                        self.position.insert(11,self.count)
                                        self.ui.eleven.setStyleSheet("background-color: red; color: white")
                                        self.position1.insert(11,self.count)
                                        self.ui.num11.setStyleSheet("background-color: red; color: white")        
                                elif self.count == 12 :
                                        self.position.insert(12,self.count)
                                        self.ui.twelve.setStyleSheet("background-color: red; color: white")
                                        self.position1.insert(12,self.count)
                                        self.ui.num12.setStyleSheet("background-color: red; color: white")         
                                elif self.count == 13 :
                                        self.position.insert(13,self.count)
                                        self.ui.thirteen.setStyleSheet("background-color: red; color: white")
                                        self.position1.insert(13,self.count)
                                        self.ui.num13.setStyleSheet("background-color: red; color: white")               
                                elif self.count == 14 :
                                        self.position.insert(14,self.count)
                                        self.ui.fourteen.setStyleSheet("background-color: red; color: white")
                                        self.position1.insert(14,self.count)
                                        self.ui.num14.setStyleSheet("background-color: red; color: white")
                                elif self.count == 15 :
                                        self.position.insert(15,self.count)
                                        self.ui.fifteen.setStyleSheet("background-color: red; color: white")
                                        self.position1.insert(15,self.count)
                                        self.ui.num15.setStyleSheet("background-color: red; color: white")
                                elif self.count == 16 :
                                        self.position.insert(16,self.count)
                                        self.ui.fifteen.setStyleSheet("background-color: red; color: white")
                                        self.position1.insert(16,self.count)
                                        self.ui.num15.setStyleSheet("background-color: red; color: white")       
                                
                        self.totalvalue = int(self.totalvalue) / 2
                        self.count+=1
                self.pre_totalvalue = self.totalvalue
            self.ui.zero.setText(str(self.position[0]))
            self.ui.one.setText(str(self.position[1]))
            self.ui.two.setText(str(self.position[2]))         
            self.ui.three.setText(str(self.position[3]))
            self.ui.four.setText(str(self.position[4]))
            self.ui.five.setText(str(self.position[5]))
            self.ui.six.setText(str(self.position[6]))
            self.ui.seven.setText(str(self.position[7]))
            self.ui.eight.setText(str(self.position[8]))
            self.ui.nine.setText(str(self.position[9]))
            self.ui.ten.setText(str(self.position[10]))
            self.ui.eleven.setText(str(self.position[11]))
            self.ui.twelve.setText(str(self.position[12]))
            self.ui.thirteen.setText(str(self.position[13]))
            self.ui.fourteen.setText(str(self.position[14]))
            self.ui.fifteen.setText(str(self.position[15]))
            self.ui.sixteen.setText(str(self.position[16]))
            self.ui.num0.setText(str(self.position[0]))
            self.ui.num1.setText(str(self.position[1]))
            self.ui.num2.setText(str(self.position[2]))
            self.ui.num3.setText(str(self.position[3]))
            self.ui.num4.setText(str(self.position[4]))
            self.ui.num5.setText(str(self.position[5]))
            self.ui.num6.setText(str(self.position[6]))
            self.ui.num7.setText(str(self.position[7]))
            self.ui.num8.setText(str(self.position[8]))
            self.ui.num9.setText(str(self.position[9]))
            self.ui.num10.setText(str(self.position[10]))
            self.ui.num11.setText(str(self.position[11]))
            self.ui.num12.setText(str(self.position[12]))
            self.ui.num13.setText(str(self.position[13]))
            self.ui.num14.setText(str(self.position[14]))
            self.ui.num15.setText(str(self.position[15]))
            self.ui.num16.setText(str(self.position[16]))

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # create and show mainWindow
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
