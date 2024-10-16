from PyQt5 import QtWidgets, uic
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QTextEdit, QFileDialog, QScrollBar, QComboBox, QColorDialog, QCheckBox, QSlider
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QTimer, QFile, QTextStream,Qt,QUrl
import scipy.io
from scipy import signal
import numpy as np
from datetime import datetime
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent, QMediaPlaylist
import soundfile as sf
import pandas as pd
from pyqtgraph import PlotWidget
import pyqtgraph as pg
import sys
import csv
import os
import time

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('mainwindow.ui', self)
        self.apply_stylesheet("ManjaroMix.qss")
        self.originalPlayer = QMediaPlayer()
        self.equalizerPlayer = QMediaPlayer()

        self.slidersArr=[self.slider1,self.slider2,self.slider3,self.slider4,self.slider5, 
                         self.slider6,self.slider7,self.slider8,self.slider9,self.slider10]
        self.all_labels = [self.sliderLabel1,self.sliderLabel2,self.sliderLabel3,self.sliderLabel4,
                           self.sliderLabel5, self.sliderLabel6, self.sliderLabel7, self.sliderLabel8, self.sliderLabel9, self.sliderLabel10]
        init_connectors(self)
        # Flags
        self.pauseFlagLink=False
        self.isSyncingX = False
        self.isCsv = False
        self.isOverFlow = True
        self.hideSpectro=False
        self.stdDevGaussian=0.1
        # Linking Graphs initialize
        self.originalSignalGraph.getViewBox().sigXRangeChanged.connect(self.synchronizeXGraph1)
        self.equalizedSignalGraph.getViewBox().sigXRangeChanged.connect(self.synchronizeXGraph2)

        self.slidersGain = [1,1,1,1,1,1,1,1,1,1]
        # this array memo window overlay data
        self.windowPlot=[]
        for slider in self.slidersArr:
            slider.setMinimum(0)
            slider.setMaximum(10)
            slider.setValue(1)

        self.emptyIcon = QtGui.QIcon()
        self.resetSliders()
        all_icons = [self.firstIcon , self.secondIcon , self.thirdIcon , self.fourthIcon , self.fifthIcon, self.sixthIcon , self.seventhIcon , self.eighthIcon , self.ninthIcon, self.tenthIcon ]
        for icon in all_icons:
                 icon.show()   
                 icon.setIcon(self.emptyIcon)
                 icon.setFixedWidth(90)
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        # Modes Data
        self.modes = {
            1: {
                'slidersGain': [1, 1, 1, 1, 0, 0, 0, 0, 0, 0],
                'sliders_to_hide': [self.slider5, self.slider6, self.slider7, self.slider8, self.slider9, self.slider10],
                'labels_to_hide': [self.sliderLabel5, self.sliderLabel6, self.sliderLabel7, self.sliderLabel8, self.sliderLabel9, self.sliderLabel10],
                'icons': [self.firstIcon, self.secondIcon, self.thirdIcon, self.fourthIcon, self.fifthIcon, self.sixthIcon, self.seventhIcon, self.eighthIcon, self.ninthIcon, self.tenthIcon],
                'iconObjectsPaths': ["icons/fox.png", "icons/dolphin.png", "icons/cat.png", "icons/owl.png"],
            },
            2: {
                'slidersGain': [1, 1, 1, 0, 1, 0, 0, 0, 0, 0],
                'sliders_to_hide': [self.slider4, self.slider6, self.slider7, self.slider8, self.slider9, self.slider10],
                'labels_to_hide': [self.sliderLabel4, self.sliderLabel6, self.sliderLabel7, self.sliderLabel8, self.sliderLabel9, self.sliderLabel10],
                'icons': [self.firstIcon, self.secondIcon, self.thirdIcon, self.fourthIcon, self.fifthIcon, self.sixthIcon, self.seventhIcon, self.eighthIcon, self.ninthIcon, self.tenthIcon],
                'iconObjectsPaths': ["icons/violin.png", "icons/trumpet_1.png", "icons/xylophone_1.png", "icons/triangle_1.png"],
                'iconToHide': self.fourthIcon,
            },
            3: {
                'sliders_to_hide': [self.slider3, self.slider5, self.slider6, self.slider7, self.slider8, self.slider9, self.slider10],
                'labels_to_hide': [self.sliderLabel3, self.sliderLabel5, self.sliderLabel6, self.sliderLabel7, self.sliderLabel8, self.sliderLabel9, self.sliderLabel10],
                'icons': [self.thirdIcon, self.fifthIcon, self.sixthIcon, self.seventhIcon, self.eighthIcon, self.ninthIcon, self.tenthIcon],
                'iconsToShow': [self.secondIcon, self.firstIcon, self.fourthIcon],
                'iconsToShowText': ["extra systole", "Ventricular Fib", "Atrial Fib"],
                'hideAllIcons': True,
            },
        }
  
    def browse(self):
            self.fileName = QFileDialog.getOpenFileName(None,"Open a File","./",filter="Audio File(*.wav *.csv)")
            if self.fileName[0]:
                 arr = self.fileName[0]
                 fileExtension = arr[len(arr)-3:]
                 if fileExtension == "wav":
                    self.sampleRate,  self.sampleArr = scipy.io.wavfile.read(arr)
                    self.originalPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(arr)))
                    self.isCsv = False
                    self.plotOriginalSignal()
                 else:
                     self.isCsv = True
                     self.timeArr , self.amplitudeArr = [],[] 
                     with open(arr, 'r') as file:
                      csv_data = csv.reader(file, delimiter=',')
                      for row in csv_data:
                           self.timeArr.append(float(row[0]))
                           self.amplitudeArr.append(float(row[1]))
                     self.plotOriginalSignal()       

    def apply_stylesheet(self, stylesheet_path):
        stylesheet = QFile(stylesheet_path)
        if stylesheet.open(QFile.ReadOnly | QFile.Text):
            stream = QTextStream(stylesheet)
            qss = stream.readAll()
            self.setStyleSheet(qss)
        else:
            print(f"Failed to open stylesheet file: {stylesheet_path}")

    def plotSignal(self,time_arr,sample_arr,graph,is_csv):
          graph.clear()
          self.equalizedSignalGraph.clear()
          graph.plotItem.setLabel(axis="left",text="Amplitude ")
          graph.plotItem.setLabel(axis="bottom",text="Time(s) ")  
          if is_csv==False:
                graph.plot(time_arr,sample_arr,pen=pg.mkPen(color=(255, 0, 0), width=1))
                self.equalizedSignalGraph.plot(time_arr,sample_arr,pen=pg.mkPen(color=(255,0,0), width=1))
                graph.setXRange(0,0.1)
          else:
                graph.plot(time_arr,sample_arr,pen=pg.mkPen(color=(255, 0, 0), width=1))
                self.equalizedSignalGraph.plot(time_arr,sample_arr,pen=pg.mkPen(color=(255,0,0), width=1)) 
        
    def plotOriginalSignal(self): 
          if self.isCsv==False:
            self.plotSignal(list(np.linspace(0, len(self.sampleArr) / self.sampleRate, len(self.sampleArr))),self.sampleArr,self.originalSignalGraph,self.isCsv)
            self.originalPlayer.play()                  
          else:    
             self.plotSignal(self.timeArr,self.amplitudeArr,self.originalSignalGraph,self.isCsv)   
          self.plotOriginalSpectro()

    def plotEqualizedSignal(self):
        if self.isCsv == False:
             self.sampleRate2,  self.sampleArr2 = scipy.io.wavfile.read(f'musicout/{self.curTime}mama.wav')
             timeArr = list(np.linspace(0,len(self.sampleArr2)/self.sampleRate2, len(self.sampleArr2) ))
             self.plotSignal(timeArr,self.sampleArr2,self.equalizedSignalGraph,self.isCsv)
        else:
             self.plotSignal(self.timeArr,self.amplitudeArr2,self.equalizedSignalGraph,self.isCsv)
        self.plotEqualizedSpectro()

    def plotEqualizedSignalSpectroGraph(self,frequencies, fftoutput):
        self.equalizedSignalSpectroGraph.clear()
        self.equalizedSignalSpectroGraph.plotItem.setLabel(axis="left",text="Amplitude ")
        self.equalizedSignalSpectroGraph.plotItem.setLabel(axis="bottom",text="Frequency(HZ) ")
        fftoutput = [abs(val) for val in fftoutput]
        plotItems = []
        for i in range(len(self.windowPlot)):
             plotItems.append(self.equalizedSignalSpectroGraph.plot(name="plot"+str(i) ,pen=pg.mkPen(color=(0,255,0), width=1)))
        for i in range(len(plotItems)):
             plotItems[i].setData(self.windowPlot[i][0],self.windowPlot[i][1]*max(fftoutput),pen=pg.mkPen(color=(0,255,0)), name="plot"+str(i))
        self.equalizedSignalSpectroGraph.plot(frequencies,fftoutput,pen=pg.mkPen(color=(255,0,0), width=1))      
        
    def plotSpectrogram(self,canvas,signal,sample_rate,is_csv):
          canvas.axes.clear()
          if self.isCsv==False:
                canvas.axes.specgram(signal,Fs=sample_rate)
          else:
                canvas.axes.specgram(signal,Fs=(1/self.timeArr[1]-self.timeArr[0]))
          canvas.draw()

    def plotOriginalSpectro(self):
         self.plotSpectrogram(
                canvas=self.originalSpectro.canvas,
                signal=self.sampleArr if not self.isCsv else self.amplitudeArr,
                sample_rate=self.sampleRate if not self.isCsv else 1 / (self.timeArr[1] - self.timeArr[0]),
                is_csv=self.isCsv
            )

    def plotEqualizedSpectro(self):
        self.plotSpectrogram(
        canvas=self.equalizedSpectro.canvas,
        signal=self.sampleArr2 if not self.isCsv else self.amplitudeArr2,
        sample_rate=self.sampleRate2 if not self.isCsv else 1 / (self.timeArr[1] - self.timeArr[0]),
        is_csv=self.isCsv
            )    

    def alterBands(self,fftOutput, frequencies,sampleRate,factor,selectedWindow):
         self.windowPlot = []
         for i, gain in enumerate(self.slidersGain):
                    freqMinRange =(i)*sampleRate/(2*factor)
                    freqMaxRange =(i+1)*sampleRate/(2*factor)
                    freqL = frequencies > freqMinRange
                    freqR = frequencies <= freqMaxRange
                    freqIndices = np.where((frequencies > freqMinRange) & (frequencies <= freqMaxRange))[0]
                    intersection = []
                    for j , k  in zip(freqL , freqR): 
                        intersection.append(j and k)
                    windowsParams={
                       "Rectangle": np.ones(len(fftOutput[intersection])),
                       "Gaussian" : signal.windows.gaussian(len(fftOutput[intersection]), std=self.stdDevGaussian* len(fftOutput[intersection])),
                       "Hamming"  : np.hamming(len(fftOutput[intersection])),
                       "Hanning"  : np.hanning(len(fftOutput[intersection])) ,
                    }    
                    window = windowsParams[selectedWindow]
                    fftOutput[intersection]*=gain
                    if gain!=0 and gain!=1:
                        self.windowPlot.append([frequencies[freqIndices],window])
                    if gain!=1:
                         fftOutput[intersection]*=window             
         return fftOutput

    def setModeParams(self,selectedMode):
         modes_params={
              "Normal Mode":[1,10,-1],
              "Animal Mode":[2,15,15],
              "Musical Mode":[3,22,23],
              "ECG Mode":[4,6,-1],
         }
         mode = modes_params[selectedMode][0] 
         factor = modes_params[selectedMode][1]
         lastIndex = modes_params[selectedMode][2]
         return mode,factor,lastIndex
    
    def saveCsvData(self):
        self.newSampleArr= self.newSampleArr.tolist()
        if self.isOverFlow == True and len(self.timeArr) != len(self.newSampleArr):
            self.timeArr.pop()
            self.isOverFlow = False
        np.savetxt(f"musicout/{self.curTime}mama.csv", np.column_stack((self.timeArr,self.newSampleArr)), delimiter=',') 
        with open(f"musicout/{self.curTime}mama.csv", 'r') as file:
            csv_data = csv.reader(file, delimiter=',')
            self.amplitudeArr2 = []
            for row in csv_data:
                self.amplitudeArr2.append(float(row[1]))

    def saveWavData(self,ifft_data):
        scipy.io.wavfile.write(f'musicout/{self.curTime}mama.wav', self.sampleRate, ifft_data)      

    def goFFT(self):
             selectedWindow = self.windowSelection()
             selectedMode = self.modeSelection()
             mode,factor,lastIndex = self.setModeParams(selectedMode)
             if self.isCsv == False:
                frequencies = np.fft.rfftfreq(len(self.sampleArr), d= 1/self.sampleRate)
                fftOutput = np.fft.rfft(self.sampleArr)
             else:
                self.sampleRate = 1/(self.timeArr[1]-self.timeArr[0])
                frequencies = np.fft.rfftfreq(len(self.amplitudeArr), d= (self.timeArr[1]-self.timeArr[0]))
                fftOutput = np.fft.rfft(self.amplitudeArr)
             sampleRateArr = [100,self.sampleRate,self.sampleRate,500]   
             fftOutput = self.alterBands(fftOutput, frequencies ,sampleRateArr[mode-1],factor,selectedWindow )
             # Inverse FFT
             self.newSampleArr = np.fft.irfft(fftOutput).real
             ifft_data = np.int16(self.newSampleArr) 
             self.curTime = datetime.now()
             self.curTime = f'{self.curTime:%Y-%m-%d %H-%M-%S.%f %p}' 
             if self.isCsv == False: 
                    self.saveWavData(ifft_data)
                    self.equalizerPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(f'musicout/{self.curTime}mama.wav')))
                    self.originalPlayer.setMuted(1)
                    self.equalizerPlayer.play()
                    self.originalPlayer.play()
             else:  
                  self.saveCsvData()      
             self.plotEqualizedSignal()
             self.plotEqualizedSignalSpectroGraph(frequencies,fftOutput)

    def playPauseLink(self,playPauseBtn):
             icon = QtGui.QIcon()
             self.pauseFlagLink ^= True
             if self.pauseFlagLink == True :
                     icon.addPixmap(QtGui.QPixmap("Images/play.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
                     playPauseBtn.setIcon(icon)
                     self.originalPlayer.pause() 
                     self.equalizerPlayer.pause()  
                   
             else:
                    icon.addPixmap(QtGui.QPixmap("Images/pause.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
                    playPauseBtn.setIcon(icon)
                    self.originalPlayer.play() 
                    self.equalizerPlayer.play()

    def updateXAxis(self,position):
         if position>0: 
            self.originalSignalGraph.setXRange((position/1000) , (position/1000)+0.1)
            self.equalizedSignalGraph.setXRange((position/1000)  , (position/1000)+0.1)
         self.timeSlider.blockSignals(True)
         self.timeSlider.setValue(position)
         self.timeSlider.blockSignals(False)

    def updateTime(self,time):
        self.timeSlider.setMaximum(time)
            
    def synchronizeXGraph1(self):
        if not self.isSyncingX:
            self.equalizedSignalGraph.getViewBox().sigXRangeChanged.disconnect(self.synchronizeXGraph2)
            xRange = self.originalSignalGraph.getViewBox().viewRange()[0]
            self.isSyncingX = True
            self.equalizedSignalGraph.getViewBox().setXRange(*xRange)
            self.isSyncingX = False
            self.equalizedSignalGraph.getViewBox().sigXRangeChanged.connect(self.synchronizeXGraph2)

    def synchronizeXGraph2(self):
        if not self.isSyncingX:
            self.originalSignalGraph.getViewBox().sigXRangeChanged.disconnect(self.synchronizeXGraph1)
            xRange = self.equalizedSignalGraph.getViewBox().viewRange()[0]
            self.isSyncingX = True
            self.originalSignalGraph.getViewBox().setXRange(*xRange)
            self.isSyncingX = False
            self.originalSignalGraph.getViewBox().sigXRangeChanged.connect(self.synchronizeXGraph1)
    def updateSlider(self,index,label):
         self.slidersGain[index]= self.slidersArr[index].value()
         label.setText(str(self.slidersArr[index].value()))
         self.goFFT()
           
    def windowSelection(self):
            mode = self.windowMenu.currentText()
            return mode
    
    def modeSelection(self):
            mode = self.equalizerModeMenu.currentText()
            return mode
    def resetSliders(self):
                    self.slidersGain = [1,1,1,1,1,1,1,1,1,1]
                    all_icons = [self.firstIcon , self.secondIcon , self.thirdIcon , self.fourthIcon , self.fifthIcon, self.sixthIcon , self.seventhIcon , self.eighthIcon , self.ninthIcon, self.tenthIcon ] 
                    all_sliders = [self.slider1, self.slider2, self.slider3, self.slider4, self.slider5, self.slider6, self.slider7, self.slider8, self.slider9, self.slider10]
                    all_labels = [self.sliderLabel1,self.sliderLabel2,self.sliderLabel3,self.sliderLabel4, self.sliderLabel5, self.sliderLabel6, self.sliderLabel7, self.sliderLabel8, self.sliderLabel9, self.sliderLabel10]
                    for slider, label in zip(all_sliders, all_labels):
                        slider.setValue(1)
                        slider.show()
                        label.setText(str(slider.value()))
                        label.show()
                    freq_bands = []
                    for i, gain in enumerate(self.slidersGain):
                        freqMinRange =(i)*100/(2*10)
                        freqMaxRange =(i+1)*100/(2*10)
                        freq_bands.append(f"{int(freqMinRange)}-{int(freqMaxRange)}") 
                    for icon,freq_band_value in zip( all_icons , freq_bands ):
                         icon.show()
                         icon.setIcon(self.emptyIcon)
                         icon.setText(freq_band_value) 
                         icon.setFixedWidth(90)    

    def uiChangeModeHandle(self,sliders_to_hide,labels_to_hide):
         for slider, label in zip(sliders_to_hide, labels_to_hide):
                            slider.setValue(0)
                            slider.hide()
                            label.hide()
    def uiChangeModeHandleICons(self,all_icons,mode):
             for i in range(len(all_icons)):
                        if i<5 and mode == 2 or i<4 and mode == 1:
                            all_icons[i].show()
                            all_icons[i].setText("")
                        else:
                            all_icons[i].hide()
                        all_icons[i].setFixedWidth(100)                    
    def uiChangeModeSetText(self,icons_to_show,icons_to_show_text):
        for icon, text in zip(icons_to_show, icons_to_show_text):
            icon.setIcon(self.emptyIcon)
            icon.show()
            icon.setText(text)
            icon.setFixedWidth(100)
    def hideAllIcons(self,all_icons):
        for i in range(len(all_icons)):
                    all_icons[i].hide()
    def uiChangeModeHandleSetIcon(self,all_icons,iconObjectsPaths,mode):
           for i in range(5): 
                         icon = QtGui.QIcon()
                         if i==3 and mode == 2 :  pass
                         elif i<3 and mode ==2 or  mode == 1 and i<4:  icon.addPixmap(QtGui.QPixmap(iconObjectsPaths[i]), QtGui.QIcon.Normal, QtGui.QIcon.Off)
                         elif i>3 and mode == 2:  icon.addPixmap(QtGui.QPixmap(iconObjectsPaths[i-1]), QtGui.QIcon.Normal, QtGui.QIcon.Off)
                         all_icons[i].setIcon(icon) 
    
    def changeMode(self):
        modeIndex = self.equalizerModeMenu.currentIndex()
        self.sliders_to_hide = []
        self.labels_to_hide = []
        self.resetSliders()
        mode_config = self.modes.get(modeIndex, {})
        self.slidersGain = mode_config.get('slidersGain', [])
        self.sliders_to_hide = mode_config.get('sliders_to_hide', [])
        self.labels_to_hide = mode_config.get('labels_to_hide', [])
        all_icons = mode_config.get('icons', [])
        self.uiChangeModeHandleICons(all_icons, modeIndex)
        icon_objects_paths = mode_config.get('iconObjectsPaths', [])
        if modeIndex > 0:
            self.uiChangeModeHandleSetIcon(all_icons, icon_objects_paths, modeIndex)
        icon_to_hide = mode_config.get('iconToHide')
        if icon_to_hide:  icon_to_hide.hide()
        icons_to_show = mode_config.get('iconsToShow', [])
        icons_to_show_text = mode_config.get('iconsToShowText', [])
        self.uiChangeModeSetText(icons_to_show,icons_to_show_text)
        hideIconsBool= mode_config.get('hideAllIcons') 
        if hideIconsBool:
            self.hideAllIcons(all_icons)
        self.uiChangeModeHandle(self.sliders_to_hide, self.labels_to_hide)      

    def showHideSpectro(self,showHideBtn):
         if(self.hideSpectro==False):
                self.equalizedSpectro.hide()
                self.originalSpectro.hide()
                self.label_4.hide()
                self.label_3.hide()
                self.hideSpectro=True
                showHideBtn.setText("Show Spectrograms")
         else:
                self.equalizedSpectro.show()
                self.originalSpectro.show()
                self.label_4.show()
                self.label_3.show()
                self.hideSpectro=False
                showHideBtn.setText("Hide Spectrograms")

    def showEditWindow(self):
        edit_dialog = QDialog(self)
        edit_dialog.setWindowTitle("Edit Window")
        edit_dialog.setGeometry(1000, 800, 200, 50)
        edit_dialog.setStyleSheet("background-color: #040D12") #n7ot el color bta3na
        layout = QVBoxLayout()
        gaussian_label = QLabel("Gaussian Standard Deviation Factor:")
        gaussian_label.setStyleSheet("color: white")
        layout.addWidget(gaussian_label)
        gaussian_line_edit = QLineEdit()
        layout.addWidget(gaussian_line_edit)
        close_button = QPushButton("Save")
        close_button.clicked.connect(lambda: self.closePopUP(gaussian_line_edit.text(),edit_dialog))
        layout.addWidget(close_button)
        edit_dialog.setLayout(layout)
        # Show the dialog
        edit_dialog.exec_()

    def closePopUP(self,value,window):
        try:
            factor = float(value)
            self.stdDevGaussian= factor  # Save the value to the main window variable
            window.close()
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid number.")

def init_connectors(self):
     self.browseBtn.clicked.connect(lambda:self.browse())
     self.playPauseBtn.clicked.connect(lambda:self.playPauseLink(self.playPauseBtn))
     self.showHideSpectroBtn.clicked.connect(lambda:self.showHideSpectro(self.showHideSpectroBtn))
     self.originalPlayer.positionChanged.connect(self.updateXAxis) 
     self.originalPlayer.durationChanged.connect(self.updateTime)
     self.timeSlider.valueChanged.connect(self.originalPlayer.setPosition)
     self.editWindowBtn.clicked.connect(lambda: self.showEditWindow())
     ## Sliders
     self.equalizerModeMenu.currentIndexChanged.connect(self.changeMode)
     i=0
     for slider,label in zip(self.slidersArr,self.all_labels):
          slider.sliderReleased.connect(lambda i=i, label=label: self.updateSlider(i, label))
          i+=1

def main():
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
