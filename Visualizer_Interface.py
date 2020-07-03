# -*- coding: utf-8 -*-

import warnings
warnings.filterwarnings("ignore", "(?s).*MATPLOTLIBDATA.*", category=UserWarning)
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QApplication, QFileDialog
from PyQt5.QtCore import *
from PyQt5.QtCore import QTimer
import serial
import matplotlib.pyplot as plt
import time, threading
import sys
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from time import sleep
import random
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor, Button
from matplotlib import cm
#from mpl_toolkits.mplot3d import Axes3D
import struct 
#from mpldatacursor import datacursor

MMWDEMO_OUTPUT_MSG_DETECTED_POINTS          = 1;
MMWDEMO_OUTPUT_MSG_RANGE_PROFILE            = 2;
MMWDEMO_OUTPUT_MSG_NOISE_PROFILE            = 3;
MMWDEMO_OUTPUT_MSG_AZIMUT_STATIC_HEAT_MAP   = 4;
MMWDEMO_OUTPUT_MSG_RANGE_DOPPLER_HEAT_MAP   = 5;
MMWDEMO_OUTPUT_MSG_STATS                    = 6;
MMWDEMO_OUTPUT_MSG_MAX                      = 7;
print_frequency = 1 # Plot the graph for every x frames
plot_mode = 1    # 1 Represents plotting x,y info. 0 represents plotting doppler,range info
algorithm_button = 0; # For future use
Threshold = 0 # Set a Threshold Factor between 0 < Threshold < 10000 for detected object amplitudes to cut off
FPS = 10.0 # Frames per second of the radar update
ScatterX = [] # X axis coordinates for the scatter plot
ScatterY = [] # Y axis coordinates for the scatter plot
ScatterZ = [] # Z axis coordinates for the scatter plot
RangeXY = []
DopplerXY = []
ScatterAmp = [] # Brightness values for each point
rangeDoppler = [[]]
rangeArray = []
dopplerArray = []

FrameCount = 0 # Counter for number of frames plotted
#Position = np.array([0,0,0]) # Starting Position 
PosArray = np.array([]) 
Velocity = np.array([-0.018433,0,0]) # XYZ Velocity of Radar in m/s, assume some constant average velocity

# Data is saved as a dictionary containing all frames. The structure is as follows:
data = {}
#counter = 1
configFileName = '1642config.cfg'
CLIport = {}
Dataport = {}
byteBuffer = np.zeros(2 ** 15, dtype='uint8')
byteBufferLength = 0


class Ui_MainWindow(object):
    def setupUi(self, MainWindow, fileName, fin, port1, port2):
        if MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1282, 724)
       
        font = QFont()
        font.setFamily(u"Yu Gothic Medium")
        font.setBold(False)
        font.setWeight(50)
        MainWindow.setFont(font)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        #self.MainWindow.setMouseTracking(True)
        self.TitreIHM = QtWidgets.QLabel(self.centralwidget)
        self.TitreIHM.setObjectName(u"TitreIHM")
        self.TitreIHM.setGeometry(QRect(390, 30, 221, 31))
        self.fileName = fileName
        self.fin = fin
        self.port1 = port1
        self.port2 = port2 
        palette = QPalette()
        brush = QBrush(QColor(85, 85, 127, 255))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Text, brush)
        brush1 = QBrush(QColor(85, 85, 127, 128))
        brush1.setStyle(Qt.SolidPattern)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette.setBrush(QPalette.Active, QPalette.PlaceholderText, brush1)
#endif
        palette.setBrush(QPalette.Inactive, QPalette.Text, brush)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette.setBrush(QPalette.Inactive, QPalette.PlaceholderText, brush1)
#endif
        brush2 = QBrush(QColor(120, 120, 120, 255))
        brush2.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Disabled, QPalette.Text, brush2)
        brush3 = QBrush(QColor(0, 0, 0, 128))
        brush3.setStyle(Qt.SolidPattern)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette.setBrush(QPalette.Disabled, QPalette.PlaceholderText, brush3)
#endif
        self.TitreIHM.setPalette(palette)
        font1 = QFont()
        font1.setFamily(u"Cambria")
        font1.setPointSize(24)
        font1.setBold(False)
        font1.setWeight(50)
        self.TitreIHM.setFont(font1)
        self.TitreIHM.setLineWidth(12)
        self.TitreIHM.setTextFormat(Qt.PlainText)
        self.Type_radar = QLabel(self.centralwidget)
        self.Type_radar.setObjectName(u"Type_radar")
        self.Type_radar.setGeometry(QRect(960, 30, 141, 21))
        font2 = QFont()
        font2.setFamily(u"Yu Gothic Medium")
        font2.setPointSize(12)
        font2.setBold(True)
        font2.setWeight(50)
        self.Type_radar.setFont(font2)
        self.Plot_RangeDoppler = QGraphicsView(self.centralwidget)
        self.Plot_RangeDoppler.setObjectName(u"Plot_RangeDoppler")
        self.Plot_RangeDoppler.setGeometry(QRect(850, 130, 491, 221))
        self.Plot_BitFreq_Pow = QGraphicsView(self.centralwidget)
        self.Plot_BitFreq_Pow.setObjectName(u"Plot_BitFreq_Pow")
        self.Plot_BitFreq_Pow.setGeometry(QRect(850, 390, 491, 291))
        self.PlotXY = QGraphicsView(self.centralwidget)
        self.PlotXY.setObjectName(u"PlotXY")
        self.PlotXY.setGeometry(QRect(20, 250, 361, 271))
        self.PlotXY.setMouseTracking(True)
        self.PlotXY.mouseMoveEvent = self.mouseMoveEvent
        self.Plot_BitFreq_Pow.setMouseTracking(True)
        self.Plot_BitFreq_Pow.mouseMoveEvent = self.mouseMoveEvent
        
        #scene = QGraphicsView(self.centralwidget)

        self.Connecter = QPushButton(self.centralwidget)
        self.Connecter.setObjectName(u"Connecter")
        self.Connecter.setGeometry(QRect(300, 190, 75, 31))
        self.NomPort = QLabel(self.centralwidget)
        self.NomPort.setObjectName(u"NomPort")
        self.NomPort.setGeometry(QRect(170, 200, 121, 21))
        self.NomPort.setLineWidth(12)
        self.NomPort.setTextFormat(Qt.PlainText)
        self.Param = QLabel(self.centralwidget)
        self.Param.setObjectName(u"Param")
        self.Param.setGeometry(QRect(380, 230, 211, 21))
        self.Param.setLineWidth(12)
        self.Param.setTextFormat(Qt.PlainText)
        self.RangeDoppler = QLabel(self.centralwidget)
        self.RangeDoppler.setObjectName(u"RangeDoppler")
        self.RangeDoppler.setGeometry(QRect(870, 100, 91, 21))
        self.RangeDoppler.setLineWidth(12)
        self.RangeDoppler.setTextFormat(Qt.PlainText)
        self.BitFreqPw = QLabel(self.centralwidget)
        self.BitFreqPw.setObjectName(u"BitFreqPw")
        self.BitFreqPw.setGeometry(QRect(870, 360, 141, 21))
        self.BitFreqPw.setLineWidth(12)
        self.BitFreqPw.setTextFormat(Qt.PlainText)
        self.nomGraphXY = QLabel(self.centralwidget)
        self.nomGraphXY.setObjectName(u"nomGraphXY")
        self.nomGraphXY.setGeometry(QRect(20, 220, 41, 21))
        self.nomGraphXY.setLineWidth(12)
        self.nomGraphXY.setTextFormat(Qt.PlainText)
        self.logo_mascir = QLabel(self.centralwidget)
        self.logo_mascir.setObjectName(u"logo_mascir")
        self.logo_mascir.setGeometry(QRect(30, 0, 271, 151))
        self.logo_mascir.setPixmap(QPixmap(u"2007.png"))
        self.StopBouton = QPushButton(self.centralwidget)
        self.StopBouton.setObjectName(u"StopBouton")
        self.StopBouton.setGeometry(QRect(760, 560, 75, 23))
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(126, 550, 211, 20))
        self.Ouvrir = QPushButton(self.centralwidget)
        self.Ouvrir.setObjectName(u"Ouvrir")
        self.Ouvrir.setGeometry(QRect(620, 130, 91, 31))
        self.textBrowser = QTextBrowser(self.centralwidget)
        self.textBrowser.setObjectName(u"textBrowser")
        self.textBrowser.setGeometry(QRect(230, 130, 381, 31))
        self.textBrowser.setText("Entrer le dataframe file")
        self.textEdit = QTextEdit(self.centralwidget)
        self.textEdit.setObjectName(u"textEdit")
        self.textEdit.setGeometry(QRect(710, 190, 104, 31))
        self.textEdit_2 = QTextEdit(self.centralwidget)
        self.textEdit_2.setObjectName(u"textEdit_2")
        self.textEdit_2.setGeometry(QRect(470, 190, 104, 31))
        self.NomPort_2 = QLabel(self.centralwidget)
        self.NomPort_2.setObjectName(u"NomPort_2")
        self.NomPort_2.setGeometry(QRect(400, 200, 71, 21))
        self.NomPort_2.setLineWidth(12)
        self.NomPort_2.setTextFormat(Qt.PlainText)
        self.NomPort_3 = QLabel(self.centralwidget)
        self.NomPort_3.setObjectName(u"NomPort_3")
        self.NomPort_3.setGeometry(QRect(640, 200, 61, 21))
        self.NomPort_3.setLineWidth(12)
        self.NomPort_3.setTextFormat(Qt.PlainText)
        self.groupBox = QGroupBox(self.centralwidget)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setGeometry(QRect(410, 240, 431, 311))
        self.coord = QLabel(self.centralwidget)
        self.coord.setObjectName(u"coord")
        self.coord.setGeometry(QRect(280, 640, 421, 31))
        self.connected_state = QLabel(self.centralwidget)
        self.connected_state.setObjectName(u"connected_state")
        self.connected_state.setGeometry(QRect(30, 600, 481, 31))
    
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1021, 22))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(126, 550, 211, 20))

        self.timer = QTimer(MainWindow)
        self.timer.setInterval(500)
      
        #self.pushButton.clicked.connect(self.plot_dataXY)
         
        self.StopBouton.clicked.connect(self.file_close)
        self.StopBouton.clicked.connect(MainWindow.close)
        
        self.Connecter.clicked.connect(self.connection)
        
        self.Ouvrir.clicked.connect(self.file_open)


        QMetaObject.connectSlotsByName(MainWindow)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)

    def mouseMoveEvent(self,event):
        
        self.connected_state.setText(
                    QCoreApplication.translate("MASCiR", u"position = " + str(8*(event.x()*2.0-365)/257) + "  " 
                        + str(-80*(event.y()*0.1+269)/193 + 80*1.5134715025906738), None))
   

    def file_open(self, MainWindow):

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(None,"Ouvrir un fichier", "","All Files (*);;Hexadecimal file (*.HEX)", options=options)
        
        self.fileName = fileName
        self.textBrowser.setText(str(fileName))
        if fileName:
            print(fileName)
        try:
            self.fin = open(fileName,'rb')
            self.plot_dataXY(MainWindow)
        except:

            print("No such file or directory")

    def file_close(self, MainWindow):

        self.fin.close() # fermer le fichier


    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.TitreIHM.setText(QCoreApplication.translate("MainWindow", u"PROJET APPHOS", None))
        self.Type_radar.setText(QCoreApplication.translate("MainWindow", u"77 GHz  RADAR", None))
        self.Connecter.setText(QCoreApplication.translate("MainWindow", u"Connecter ", None))
        self.NomPort.setText(QCoreApplication.translate("MainWindow", u"Connexion au port COM", None))
        self.RangeDoppler.setText(QCoreApplication.translate("MainWindow", u"Range Doppler", None))
        self.BitFreqPw.setText(QCoreApplication.translate("MainWindow", u"Coords x,y", None))
        self.nomGraphXY.setText(QCoreApplication.translate("MainWindow", u"RADAR interfacé ", None))
        self.logo_mascir.setText("")
        self.StopBouton.setText(QCoreApplication.translate("MainWindow", u"Arreter ", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Developp\u00e9 par Fatahou Ahamadi @2020", None))
        self.Ouvrir.setText(QCoreApplication.translate("MainWindow", u"ouvrir un fichier", None))
        #self.pushButton.setText(QCoreApplication.translate("MainWindow", u"D\u00e9marrer", None))
        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"Param\u00e8tres du RADAR AWR1642", None))
        self.NomPort_2.setText(QCoreApplication.translate("MainWindow", u"Cli port UART", None))
        self.NomPort_3.setText(QCoreApplication.translate("MainWindow", u"Data PORT ", None))
        
    

    def update_data(self,MainWindow):

        frameData = {}
        currentIndex = 0
        detObj = {}
        print("fonction update_data ...")
        for i in range(32):
            try:
                dataOK = self.update(MainWindow)
                if dataOk:
                # Store the current frame into frameData
                    frameData[currentIndex] = detObj
                    currentIndex += 1

                time.sleep(0.03)  # Sampling frequency of 30 Hz

            except:

                print("erreur dans la fonction update_data...")
            #time.sleep(0.5)

    def update(self, MainWindow):
        dataOk = 0
        global detObj
        rangeDoppler = [[]]
        rangeArray = []
        dopplerArray = []
        x = []
        y = []
        rangeVal = []
        dopplerVal = []
        peakVal = []


        # Read and parse the received data
        #configParameters = parseConfigFile(configFileName)

        dataOk, frameNumber, detObj, rangeDoppler, rangeArray, dopplerArray = readAndParseData16xx(self.port1)
        print(rangeDoppler)

        if dataOk and len(detObj["x"]) > 0:

            # print(detObj)
            
            scene = QGraphicsScene()
            scene1 = QGraphicsScene()
            self.Plot_BitFreq_Pow.setScene(scene) 
            self.Plot_RangeDoppler.setScene(scene1)
            figure = Figure()
            figure1 = Figure()
            axes = figure.gca()
            axes1 = figure1.gca()
            
            for i in range(1600):
              try:

                #configParameters = parseConfigFile(configFileName)
                dataOk, frameNumber, detObj, rangeDoppler, rangeArray, dopplerArray = readAndParseData16xx(self.port1)      
                longitud = detObj["x"]
                lateral = -detObj["y"]
                rangeVal = detObj["RangeXY"]
                dopplerVal = detObj["dopplerVal"]
                peakVal = detObj["peakVal"]
                print(detObj["x"])
                

               # lateral,longitud,peakVal,rangeVal,dopplerVal = filtrer(dopplerVal,rangeVal,peakVal,20,longitud,lateral)
             # filtrage
                Longitude = []
                Laterale = []
                Portee = []
                Velocity = []
                Power = []
                for ii in range(len(rangeVal)):
                    if rangeVal[ii] <= 20:
                        Longitude.append(longitud[ii])
                        Laterale.append(lateral[ii])
                        Portee.append(rangeVal[ii])
                        Velocity.append(dopplerVal[ii])
                        Power.append(peakVal[ii])

                axes1.set_title("Range Doppler")

                axes.set_title("Plot X and Y")
                axes.set_xlim(xmin=-20, xmax=20)
                axes.set_ylim(ymin=0, ymax=20)
                axes.set_xlabel('left',text = 'X Position (m)')
                axes.set_ylabel('bottom', text= 'Y Position (m)')

                #print(i)
                if len(lateral) > 2:
                    plt.draw()
                    #plt.connect('motion_notify_event', mouse_move)
                    plt.pause(0.1)
                    axes.clear()
                    axes1.clear()
                    axes1.imshow(rangeDoppler,interpolation='nearest', aspect='auto',
                                extent = [np.min(rangeArray) , np.max(rangeArray), np.min(dopplerArray) , -np.min(dopplerArray)])
                    axes.scatter(Laterale, Longitude, c=Power,cmap=cm.rainbow)
                    datacursor(display='multiple', draggable=True)
                    canvas = FigureCanvas(figure)
                    canvas1 = FigureCanvas(figure1)
                    canvas.setGeometry(QRect(850, 390, 491, 291))
                    canvas1.setGeometry(QRect(850, 130, 491, 221))
                    scene.addWidget(canvas)
                    scene1.addWidget(canvas1) 

              except BaseException:
                print("File no Traitable!!!")


        return dataOk

    # retranslateUi
    def connection(self, MainWindow):
        etat_connection = False
        # QCoreApplication.instance().quit()
        CliPort = self.textEdit.toPlainText()
        DataPort = self.textEdit_2.toPlainText()
        #print(CliPort, DataPort)


        if CliPort == "" and DataPort == "":
            self.connected_state.setGeometry(QRect(30, 600, 481, 31))
            self.connected_state.setStyleSheet('color: red')
            self.connected_state.setText(QCoreApplication.translate("MASCiR", u"Veuillez saisir les ports", None))

        else:
            val = False
            try:
                eval(CliPort)
                eval(DataPort)
                val = True

            except:
                self.connected_state.setGeometry(QRect(30, 600, 481, 31))
                self.connected_state.setStyleSheet('color: red')
                self.connected_state.setText(
                    QCoreApplication.translate("MASCiR", u"Saisir des valeurs numeriques", None))
            if val == True:
                try:
                    com1 = "COM" + CliPort
                    com2 = "COM" + DataPort

                    self.port1 = serial.Serial(com1, 921600, exclusive=True)
                    self.port2 = serial.Serial(com2, 115200, exclusive=True)

                    self.connected_state.setStyleSheet('color: green')
                    self.connected_state.setText(QCoreApplication.translate("MASCiR", u"Connected", None))
                    self.update(MainWindow)
                    etat_connection = True

                except:
                    self.connected_state.setGeometry(QRect(30, 600, 481, 31))
                    self.connected_state.setStyleSheet('color: red')
                    self.connected_state.setText(
                        QCoreApplication.translate("MASCiR", u"Echec de connexion, vérifier les ports ", None))

        if etat_connection == True:
            #parse()
            print("Connecter")
            
              

    def plot_dataXY(self,MainWindow):

        counter = 0
        Position = np.array([0,0,0])
        ScatterX = []
        ScatterY = []
        ScatterAmp = []
        RangeXY = []
        DopplerXY = []
        rangeArray = []
        dopplerArray = []
        rangeDoppler = [[]]
        scene = QGraphicsScene()
        self.PlotXY.setScene(scene) 
        figure = Figure()
        axes = figure.gca()
        scene1 = QGraphicsScene()
        self.Plot_RangeDoppler.setScene(scene1) 
        figure1 = Figure()
        axes1 = figure1.gca()

        print(self.fileName)
        print(self.fin)
        for i in range(164):   

            try:
                
                ScatterX, ScatterY, ScatterZ, ScatterAmp, RangeXY, DopplerXY, rangeArray, dopplerArray, rangeDoppler = processing(self.fin,counter,Position)
                
                #axes.clf()
                
                #plt.style.use('dark_background')
                plt.clf()
                ax = plt.gca()
                #axes.clear()
                lines = axes.scatter(ScatterX,ScatterY,c=ScatterAmp,cmap=cm.rainbow)    
                axes.set_title("Range Doppler")
                axes.set_xlim(xmin=-8, xmax=8)
                axes.set_ylim(ymin= 0, ymax=8)
                axes.set_xlabel('left',text = 'X Position (m)')
                axes.set_ylabel('bottom', text= 'Y position (m)')
                #axes.grid()

                #mplcursors.cursor(lines)
                cursor = Cursor(axes, horizOn=True, vertOn=True, color='green', linewidth=2.0)

                #fig.canvas.mpl_connect('button_press_event',onclick)
               
# ********************************************************************
                #axes1.clear()
                #axes1.imshow(rangeDoppler)
                axes1.imshow(rangeDoppler,interpolation='nearest', aspect='auto',
                    extent = [np.min(rangeArray) , np.max(rangeArray), np.min(dopplerArray) , -np.min(dopplerArray)])
                
                #axes1.grid()
                #axes.scatter(RangeXY,Doppler_Value)
                plt.draw()
                plt.pause(0.1)
                canvas = FigureCanvas(figure)
                 
                canvas1 = FigureCanvas(figure1)

                canvas.setGeometry(QRect(10, 240, 331, 251))
                canvas1.setGeometry(QRect(850, 130, 481, 191))
                scene.addWidget(canvas) 
                scene1.addWidget(canvas1)
            except BaseException:
                print("File no Traitable!!!")


    

def Pos(S,V,T):

    return (S+(V*T))

#********************************************************************************************************************

def processing(fin, counter, Position):

     
        position = np.array([0,0,0])
        counter = 1
        magicword = []
        nbyte = 0
        a = np.fromfile(fin,'uint16',4)
        for i in a:
            magicword.append(hex(i))
        try:
            if magicword[0]!='0x102' or magicword[1]!='0x304' or magicword[2]!='0x506' or magicword[3]!='0x708':
                print ("the magic word now is ", magicword)
                print ("Data not correct!")
                print (counter)
        except BaseException:
            print ("end of file")

        version = np.int((np.fromfile(fin,'uint32',1)  ) )
        totalPacketLen = np.int((np.fromfile(fin,'uint32',1)  ) )
        platform = np.int((np.fromfile(fin,'uint32',1)  ) )
        frameNumber = np.int((np.fromfile(fin,'uint32',1)  ) )
        timeCpuCycles = np.int((np.fromfile(fin,'uint32',1)  ) )
        numDetectedObj = np.int((np.fromfile(fin,'uint32',1)  ) )
        numTLVs = np.int((np.fromfile(fin,'uint32',1)  ) )
        subFrameNumber = np.int((np.fromfile(fin,'uint32',1)  ) )
        nbyte += 40

        #print("numTLVs")

        tlv = {}
        data[counter] = {"magicword":magicword,"version":version,"totalPacketLen":totalPacketLen,"platform":platform,\
                   "frameNumber":frameNumber,"timeCpuCycles":timeCpuCycles,\
                   "numDetectedObj":numDetectedObj,"numTLVs":numTLVs,\
                   "tlv":tlv}
        
        for i in range(0,numTLVs):
            tlv_type = np.int(np.fromfile(fin,'uint32',1))
            tlv_length = np.int((np.fromfile(fin,'uint32',1)))
            nbyte += 8
            max_x = 0
            max_y = 0
            max_range = 0
            max_doppler = 0          
            
            if tlv_type == MMWDEMO_OUTPUT_MSG_DETECTED_POINTS:     # case 1
                
                tlv_numDetectedObj = np.int(np.fromfile(fin,'uint16',1))
                tlv_xyzQformat = np.int(np.fromfile(fin,'uint16',1))
                nbyte+=4
                
                for numObject in range(0,tlv_numDetectedObj):
                    the_obj_data = {}
                    the_obj_data["rangeidx"] = np.int(np.fromfile(fin,'uint16',1))
                    the_obj_data["dopplerIdx"] = np.float((np.fromfile(fin,'int16',1)) *(2**(-1*tlv_xyzQformat)))
                    the_obj_data["peakVal"] = np.int(np.fromfile(fin,'uint16',1))**0.1
                    the_obj_data["x"] = np.float((np.fromfile(fin,'int16',1))*(2**(-1*tlv_xyzQformat))) - Position[0]
                    the_obj_data["y"] = np.float((np.fromfile(fin,'int16',1))*(2**(-1*tlv_xyzQformat))) - Position[1]
                    the_obj_data["z"] = np.float((np.fromfile(fin,'int16',1))*(2**(-1*tlv_xyzQformat))) - Position[2]
                    nbyte+=12
                    tlv[numObject]=the_obj_data

                    if (counter % print_frequency == 0) and (the_obj_data["peakVal"] > Threshold):
                        ScatterX.append(the_obj_data["x"])
                        ScatterY.append(the_obj_data["y"])
                        ScatterZ.append(the_obj_data["z"]) # Z axis data depends on the drone's altitude output
                        ScatterAmp.append(the_obj_data["peakVal"])
                        #Doppler_Value.append(the_obj_data["dopplerIdx"])
                        RangeXY.append(the_obj_data["x"]**2 + the_obj_data["y"]**2)
                        DopplerXY.append(the_obj_data["dopplerIdx"])

                        #Doppler_Value.append(the_obj_data["doppler"])

                # Get a position update of the drone    
                Position = Pos(Position,Velocity,1/FPS)
                
        
               # print(Position)
            # Read the other MMDEMO output messages
            elif tlv_type == MMWDEMO_OUTPUT_MSG_RANGE_PROFILE:
                np.fromfile(fin,'int8',tlv_length)
                nbyte += tlv_length    #second case
            elif tlv_type == MMWDEMO_OUTPUT_MSG_NOISE_PROFILE:
                #third case
                np.fromfile(fin,'int8',tlv_length)
                nbyte += tlv_length            
            elif tlv_type == MMWDEMO_OUTPUT_MSG_AZIMUT_STATIC_HEAT_MAP:
                #fourth case
                np.fromfile(fin,'int8',tlv_length)
                nbyte += tlv_length
            elif tlv_type == MMWDEMO_OUTPUT_MSG_RANGE_DOPPLER_HEAT_MAP:
                #fifth case
                payload = np.fromfile(fin,'int8',tlv_length)
                nbyte += tlv_length
                rangeDoppler = payload.view(dtype=np.int16)
                
                chirpEndIdx = 2
                chirpStartIdx  = 1
                numLoops = 32
                numTxAnt = 2
                numAdcSamplesRoundTo2 = 256
                digOutSampleRate = 5500
                freqSlopeConst = 68
                startFreq = 77
                idleTime = 7
                rampEndTime = 58
                numChirpsPerFrame = (chirpEndIdx - chirpStartIdx + 1) * numLoops
                numDopplerBins = int(numChirpsPerFrame / numTxAnt)
                numRangeBins = numAdcSamplesRoundTo2
                rangeIdxToMeters = (3e8 * digOutSampleRate * 1e3) / (2 * freqSlopeConst * 1e12 * numRangeBins)

                dopplerResolutionMps = 3e8 / (2 * startFreq * 1e9 * (idleTime + rampEndTime) * 1e-6 * numDopplerBins * numTxAnt)
                #print(numDopplerBins)
                #print(numRangeBins)
                #print(len(rangeDoppler))
                # Convert the range doppler array to a matrix
                rangeDoppler = np.reshape(rangeDoppler, (numDopplerBins, numRangeBins),'F') #Fortran-like reshape
                #rangeDoppler = np.append(rangeDoppler[int(len(rangeDoppler)/2):], rangeDoppler[:int(len(rangeDoppler)/2)], axis=0)

                # Generate the range and doppler arrays for the plot
                rangeArray = np.array(range(numRangeBins))*rangeIdxToMeters
                dopplerArray = np.multiply(np.arange(-numDopplerBins/2 , numDopplerBins/2), dopplerResolutionMps)



            elif tlv_type == MMWDEMO_OUTPUT_MSG_STATS:
                #sixth case
                np.fromfile(fin,'int8',tlv_length)
                nbyte += tlv_length
            elif tlv_type == MMWDEMO_OUTPUT_MSG_MAX:
                #seventh case
                np.fromfile(fin,'int8',tlv_length)
                nbyte += tlv_length
            ###### last case #####
            else:
                '''
                print "tlv data not correct in round %i"%i
                '''
                np.fromfile(fin,'int8',tlv_length)
                nbyte += tlv_length
                    
        counter += 1
        np.fromfile(fin,'int8',totalPacketLen-nbyte)

        return ScatterX, ScatterY, ScatterZ, ScatterAmp, RangeXY, DopplerXY,rangeArray,dopplerArray,rangeDoppler

# ********************************************************************************************************************************

# *******************************************************************---------------------**********/////

def readAndParseData16xx(Dataport):
    global byteBuffer, byteBufferLength

    # Constants
    OBJ_STRUCT_SIZE_BYTES = 12
    BYTE_VEC_ACC_MAX_SIZE = 2 ** 15
    MMWDEMO_UART_MSG_DETECTED_POINTS = 1
    MMWDEMO_UART_MSG_RANGE_PROFILE = 2
    MMWDEMO_OUTPUT_MSG_RANGE_DOPPLER_HEAT_MAP = 5
    maxBufferSize = 2 ** 15
    magicWord = [2, 1, 4, 3, 6, 5, 8, 7]


    # Initialize variables
    magicOK = 0  # Checks if magic number has been read
    dataOK = 0  # Checks if the data has been read correctly
    frameNumber = 0
    detObj = {}
    rangeDoppler = [[]]
    rangeArray = []
    dopplerArray = []
    tlv_type = 0
    chirpEndIdx = 2
    chirpStartIdx  = 1
    numLoops = 32
    numTxAnt = 2
    numAdcSamplesRoundTo2 = 256
    digOutSampleRate = 5500
    freqSlopeConst = 68
    startFreq = 77
    idleTime = 7
    rampEndTime = 58
    numChirpsPerFrame = (chirpEndIdx - chirpStartIdx + 1) * numLoops
    numDopplerBins = int(numChirpsPerFrame / numTxAnt)
    numRangeBins = numAdcSamplesRoundTo2
    rangeIdxToMeters = (3e8 * digOutSampleRate * 1e3) / (2 * freqSlopeConst * 1e12 * numRangeBins)

    dopplerResolutionMps = 3e8 / (2 * startFreq * 1e9 * (idleTime + rampEndTime) * 1e-6 * numDopplerBins * numTxAnt)

    readBuffer = Dataport.read(Dataport.in_waiting)
    byteVec = np.frombuffer(readBuffer, dtype='uint8')
    byteCount = len(byteVec)
    print(byteCount)
    #print(byteVec)

    # Check that the buffer is not full, and then add the data to the buffer
    if (byteBufferLength + byteCount) < maxBufferSize:
        byteBuffer[byteBufferLength:byteBufferLength + byteCount] = byteVec[:byteCount]
        byteBufferLength = byteBufferLength + byteCount

    # Check that the buffer has some data
    if byteBufferLength > 16:

        # Check for all possible locations of the magic word
        possibleLocs = np.where(byteBuffer == magicWord[0])[0]

        # Confirm that is the beginning of the magic word and store the index in startIdx
        startIdx = []
        for loc in possibleLocs:
            check = byteBuffer[loc:loc + 8]
            if np.all(check == magicWord):
                startIdx.append(loc)

        # Check that startIdx is not empty
        if startIdx:

            # Remove the data before the first start index
            if startIdx[0] > 0 and startIdx[0] < byteBufferLength:
                byteBuffer[:byteBufferLength - startIdx[0]] = byteBuffer[startIdx[0]:byteBufferLength]
                byteBuffer[byteBufferLength - startIdx[0]:] = np.zeros(len(byteBuffer[byteBufferLength - startIdx[0]:]),
                                                                       dtype='uint8')
                byteBufferLength = byteBufferLength - startIdx[0]

            # Check that there have no errors with the byte buffer length
            if byteBufferLength < 0:
                byteBufferLength = 0

            # word array to convert 4 bytes to a 32 bit number
            word = [1, 2 ** 8, 2 ** 16, 2 ** 24]

            # Read the total packet length
            totalPacketLen = np.matmul(byteBuffer[12:12 + 4], word)

            # Check that all the packet has been read
            if (byteBufferLength >= totalPacketLen) and (byteBufferLength != 0):
                magicOK = 1

    # If magicOK is equal to 1 then process the message
    if magicOK:
        # word array to convert 4 bytes to a 32 bit number
        word = [1, 2 ** 8, 2 ** 16, 2 ** 24]

        # Initialize the pointer index
        idX = 0

        # Read the header
        magicNumber = byteBuffer[idX:idX + 8]
        idX += 8
        version = format(np.matmul(byteBuffer[idX:idX + 4], word), 'x')
        idX += 4
        totalPacketLen = np.matmul(byteBuffer[idX:idX + 4], word)
        idX += 4
        platform = format(np.matmul(byteBuffer[idX:idX + 4], word), 'x')
        idX += 4
        frameNumber = np.matmul(byteBuffer[idX:idX + 4], word)
        idX += 4
        timeCpuCycles = np.matmul(byteBuffer[idX:idX + 4], word)
        idX += 4
        numDetectedObj = np.matmul(byteBuffer[idX:idX + 4], word)
        idX += 4
        numTLVs = np.matmul(byteBuffer[idX:idX + 4], word)
        idX += 4
        subFrameNumber = np.matmul(byteBuffer[idX:idX + 4], word)
        idX += 4
        
        # Read the TLV messages
        for tlvIdx in range(numTLVs):

            # word array to convert 4 bytes to a 32 bit number
            word = [1, 2 ** 8, 2 ** 16, 2 ** 24]

            # Check the header of the TLV message
            try:
                tlv_type = np.matmul(byteBuffer[idX:idX + 4], word)
                idX += 4
                tlv_length = np.matmul(byteBuffer[idX:idX + 4], word)
                idX += 4
            except:
                pass
           # print("Type TLV")
           # print(tlv_type)


            # Read the data depending on the TLV message
            if tlv_type == MMWDEMO_UART_MSG_DETECTED_POINTS:

                # word array to convert 4 bytes to a 16 bit number
                word = [1, 2 ** 8]
                tlv_numObj = np.matmul(byteBuffer[idX:idX + 2], word)
                idX += 2
                tlv_xyzQFormat = 2 ** np.matmul(byteBuffer[idX:idX + 2], word)
                idX += 2

                # Initialize the arrays
                rangeIdx = np.zeros(tlv_numObj, dtype='int16')
                dopplerIdx = np.zeros(tlv_numObj, dtype='int16')
                peakVal = np.zeros(tlv_numObj, dtype='int16')
                x = np.zeros(tlv_numObj, dtype='int16')
                y = np.zeros(tlv_numObj, dtype='int16')
                z = np.zeros(tlv_numObj, dtype='int16')

                for objectNum in range(tlv_numObj):
                    # Read the data for each object
                    rangeIdx[objectNum] = np.matmul(byteBuffer[idX:idX + 2], word)
                    idX += 2
                    dopplerIdx[objectNum] = np.matmul(byteBuffer[idX:idX + 2], word)
                    idX += 2
                    peakVal[objectNum] = np.matmul(byteBuffer[idX:idX + 2], word)
                    idX += 2
                    x[objectNum] = np.matmul(byteBuffer[idX:idX + 2], word)
                    idX += 2
                    y[objectNum] = np.matmul(byteBuffer[idX:idX + 2], word)
                    idX += 2
                    z[objectNum] = np.matmul(byteBuffer[idX:idX + 2], word)
                    idX += 2

                # Make the necessary corrections and calculate the rest of the data
                rangeVal = rangeIdx * rangeIdxToMeters
                dopplerIdx[dopplerIdx > (numDopplerBins / 2 - 1)] = dopplerIdx[dopplerIdx > (
                            numDopplerBins / 2 - 1)] - 65535
                dopplerVal = dopplerIdx * dopplerResolutionMps
                # x[x > 32767] = x[x > 32767] - 65536
                # y[y > 32767] = y[y > 32767] - 65536
                # z[z > 32767] = z[z > 32767] - 65536

                x = x / tlv_xyzQFormat
                y = y / tlv_xyzQFormat
                z = z / tlv_xyzQFormat

                RangeXY = np.sqrt(x**2+y**2)
                dopplerVal = dopplerVal/tlv_xyzQFormat

                # Store the data in the detObj dictionary
                detObj = {"numObj": tlv_numObj, "rangeIdx": rangeIdx, "RangeXY": RangeXY, "dopplerIdx": dopplerIdx, \
                          "dopplerVal": dopplerVal, "peakVal": peakVal, "x": x, "y": y, "z": z}

                #┐print(detObj)

                dataOK = 1


            elif tlv_type == MMWDEMO_OUTPUT_MSG_RANGE_DOPPLER_HEAT_MAP:

                # Get the number of bytes to read
                numBytes = 2*numRangeBins*numDopplerBins

                # Convert the raw data to int16 array
                payload = byteBuffer[idX:idX + tlv_length]
                idX += numBytes
                rangeDoppler = payload.view(dtype=np.int16)

                # Some frames have strange values, skip those frames
                # TO DO: Find why those strange frames happen
                # if np.max(rangeDoppler) > 10000:
                   # continue

                # Convert the range doppler array to a matrix
                rangeDoppler = np.reshape(rangeDoppler, (numDopplerBins, numRangeBins),'F') #Fortran-like reshape
                rangeDoppler = np.append(rangeDoppler[int(len(rangeDoppler)/2):], rangeDoppler[:int(len(rangeDoppler)/2)], axis=0)

                # Generate the range and doppler arrays for the plot
                rangeArray = np.array(range(numRangeBins))*rangeIdxToMeters
                dopplerArray = np.multiply(np.arange(-numDopplerBins/2 , numDopplerBins/2), dopplerResolutionMps)
                

        # Remove already processed data
        if idX > 0 and byteBufferLength > idX:
            shiftSize = totalPacketLen

            byteBuffer[:byteBufferLength - shiftSize] = byteBuffer[shiftSize:byteBufferLength]
            byteBuffer[byteBufferLength - shiftSize:] = np.zeros(len(byteBuffer[byteBufferLength - shiftSize:]),
                                                                 dtype='uint8')
            byteBufferLength = byteBufferLength - shiftSize

            # Check that there are no errors with the buffer length
            if byteBufferLength < 0:
                byteBufferLength = 0

    return dataOK, frameNumber, detObj, rangeDoppler, rangeArray, dopplerArray
#***************************************************************************************##

def main():
      
      app = QtWidgets.QApplication(sys.argv)
      MainWindow = QtWidgets.QMainWindow()
      demo = Ui_MainWindow()
      fileName = "fichier.txt"
      demo.setupUi(MainWindow,fileName,open(fileName,'rb'),CLIport,Dataport)  
      MainWindow.show()
      sys.exit(app.exec_())

if __name__ == '__main__':

       main()

 