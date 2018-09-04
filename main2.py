#!/usr/bin/env python3

# -*- coding: utf-8 -*-

# 
# A simple tool to rename and move images due to their "Create Date" exif property
#

import sys
import os
import glob
from mimetypes import MimeTypes
from pathlib import Path

from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import QPalette, QColor,QImageReader
from PyQt5.QtCore import Qt

import settings
from exiftools import ExifTools
from logger import log
from importwindow import ImportWindow
from datetimewindow import DateTimeWindow
from lenseaparturewindow import LenseApartureWindow
from gpswindow import GPSWindow


SourceDir       =   None
DestDir         =   None
Lensedata       =   [] 
FNumber         =   0
CreateDate      =   None

# Global argumentlist for exiftool
Filelist        =   []

# item_list contains imagedata:
#item_list[0]: checked=1/unchecked=0
#item_list[1]: inode (hidden)
#item_list[2]: image name
#item_list[3]: file datetime
#item_list[4]: CreateDate
#item_list[5]: lens model
#item_list[6]: aparture
item_list = []



# Class-handlers
exif            =   None
filemgr         =   None




Ui_MainWindow, QtBaseClass = uic.loadUiType(settings.qtCreatorFile)
 




#####################################################
#
#####################################################
class ImageWindow(QMainWindow):
    

#==============================
#
#==============================
    def __init__(self):
        super(ImageWindow,self).__init__()
        self.ui=Ui_MainWindow()
        self.ui.setupUi(self)
        self.arglist = []
            

			### Menues
        #           Arkiv
        self.ui.actionQuit.triggered.connect(self.actionQuit_trigger)
        self.ui.actionImportera.triggered.connect(self.actionImport_trigger)
        #           Edit
        self.ui.actionDateTime.triggered.connect(self.actionDateTime_trigger)
        self.ui.actionLenseAparture.triggered.connect(self.actionLenseAparture_trigger)
        self.ui.actionGPS.triggered.connect(self.actionGPS_trigger)
        
        ### Buttons
        self.ui.source_pushButton.clicked.connect(self.openSource)        
        self.ui.destdir_pushButton.clicked.connect(self.destDirButton)
        self.ui.execute_pushButton.clicked.connect(self.executeImages)
        self.ui.clear_pushButton.clicked.connect(self.clearButton)
        #self.ui.test_pushButton.setStyleSheet("background-color: red; color: white;")
        
        ### Checkboxes
        self.ui.togglenolens_checkBox.stateChanged.connect(self.toggleNoLenses)
        self.ui.togglenolens_checkBox.setCheckState(Qt.Checked)
        self.ui.toggleall_checkBox.stateChanged.connect(self.toggleAll)
        self.ui.toggleall_checkBox.setCheckState(Qt.Checked)

        ### Labels
        self.ui.dest_label.setText(DestDir)
        self.ui.sourcedir_label.setText(SourceDir)
		
        self.setStyleSheet(open("styles.css", "r").read())		

        self.col = QColor.colorNames()
        log.debug(self.col)
			
        self.ui.treeWidget.setHeaderLabels(['Välj','Inode','Filnamn','FileModifyDate','CreateDate', 'Lensmodel', 'FNumber', 'GPSLatitude', 'GPSLongitude' ])
    
    
#==============================
#
#==============================
    def actionImport_trigger(self):
        log.info("====== Import ======")
        self.iw=ImportWindow()
        self.iw.show()
        

#==============================
#
#==============================
    def actionQuit_trigger(self):
        log.info("====== Quit! ======")
        qApp.quit()


#==============================
#
#==============================
    def actionDateTime_trigger(self):
        global CreateDate
        global item_list

        log.info("====== DateTime ======")
        self.iw=DateTimeWindow("","","",0)
        self.iw.exec_()
        res = self.iw.result()
        log.debug("resultat=%d" % res)
        if res == 1:
            CreateDate, incSecond = self.iw.save()
            log.info("CreateDate is %s, incSeconds %s" % (CreateDate, incSecond))

            for i in range(self.ui.treeWidget.topLevelItemCount()):
                item = self.ui.treeWidget.topLevelItem(i)
                if item.checkState(0) == 2:
                    exif.initArglist()
                    exif.appendCreateDate(CreateDate)
                    exif.appendArglist(SourceDir + os.path.sep + item.text(2))
                    exif.executeExiftool()
                    CreateDate = self.iw.inctime(CreateDate)


            item_list.clear()
            item_list = filemgr.readFiles(Filelist, item_list)                                
            self.redrawTreeWidget(item_list)

    
    
#==============================
#
#==============================
    def actionLenseAparture_trigger(self):
        global Lensedata
        global FNumber
        global item_list
        
        log.info("====== LenseAparture ======")
        self.iw=LenseApartureWindow()
        self.iw.exec_()
        res = self.iw.result()
        log.debug("resultat=%d" % res)
        if res == 1:
            Lensedata, FNumber = self.iw.save()
            log.info("FNumber is %s, Lensedata %s" % (FNumber, Lensedata))
            if len(Lensedata) > 0 or int(FNumber) > 0:
                exif.initArglist()
                
                log.debug("len(Lensedata): %d" % len(Lensedata))
                for l in Lensedata:
                    log.debug("Lensedata: %s" % l)
                    exif.appendArglist(l)
                
                if float(FNumber) > 0:
                    exif.appendFnumber(FNumber)
                upd = False
                for i in range(self.ui.treeWidget.topLevelItemCount()):
                    item = self.ui.treeWidget.topLevelItem(i)
                    if item.checkState(0) == 2:
                        exif.appendArglist(SourceDir + os.path.sep + item.text(2))
                        upd = True
                        
                if upd:
                    exif.executeExiftool()
                
                item_list.clear()
                item_list = filemgr.readFiles(Filelist, item_list)                                
                self.redrawTreeWidget(item_list)

                
                    


    
#==============================
#
#==============================
    def executeImages(self):
        global Filelist
        global item_list
        
        exif.initArglist()
        exif.appendRenameImage(settings.FilenameFormat)
                
        upd = False
        for i in range(self.ui.treeWidget.topLevelItemCount()):
            item = self.ui.treeWidget.topLevelItem(i)
            if item.checkState(0) == 2:
                upd = True
                exif.appendArglist(SourceDir + os.path.sep + item.text(2))

        if upd:
            exif.executeExiftool()
            
        Filelist.clear()
        lista = glob.glob(SourceDir + os.path.sep + "*")
        for l in lista:
            st_ino = os.stat(l)[1]
            log.debug("executeImages: %s %d" % (l,st_ino))
            if exif.inode_inlist(item_list, st_ino) == True:
                Filelist.append(l)
            
        # reread and update widget  
        log.info("update widget after rename")
        item_list.clear()
        item_list = filemgr.readFiles(Filelist, item_list)                                
        self.redrawTreeWidget(item_list)
        
        
        if DestDir != None:
            log.info("move images %s" % DestDir)
            exif.initArglist()
            log.debug("move images 1")
            exif.appendMoveImages(DestDir)
            log.debug("move images 2")

            for i in range(self.ui.treeWidget.topLevelItemCount()):
                item = self.ui.treeWidget.topLevelItem(i)
                if item.checkState(0) == 2:
                    upd = True
                    exif.appendArglist(SourceDir + os.path.sep + item.text(2))
        
            log.debug("move images 3")
            if upd:
                exif.executeExiftool()
                
            log.debug("move images 3")
            lista = glob.glob(SourceDir + os.path.sep + "*")
            
            # reread and update widget    
            item_list.clear()
            item_list = filemgr.readFiles(lista, item_list)                                
            self.redrawTreeWidget(item_list)
   
            # Update Filelist
            Filelist.clear()
            for i in item_list:
                Filelist.append(i[2])



    
#==============================
#
#==============================
    def actionGPS_trigger(self):
        global Lensedata
        global FNumber
        global item_list
        
        log.info("====== actionGPS ======")
        self.iw=GPSWindow()
        self.iw.exec_()
        res = self.iw.result()
        log.info("resultat=%d" % res)
        if res == 1:
            lat, lng = self.iw.save()
            if len(lat) > 0:
                exif.initArglist()
                exif.appendLatLng(lat,lng)
                
                upd = False
                for i in range(self.ui.treeWidget.topLevelItemCount()):
                    item = self.ui.treeWidget.topLevelItem(i)
                    if item.checkState(0) == 2:
                        exif.appendArglist(SourceDir + os.path.sep + item.text(2))
                        upd = True
                        
                if upd:
                    exif.executeExiftool()

                item_list.clear()
                item_list = filemgr.readFiles(Filelist, item_list)                                
                self.redrawTreeWidget(item_list)

    


#==============================
#
#==============================
    def toggleAll(self):
        #log.info("toggleAll")
        
        for i in range(self.ui.treeWidget.topLevelItemCount()):
            item = self.ui.treeWidget.topLevelItem(i)
            if self.ui.toggleall_checkBox.checkState() == Qt.Checked:
                item.setCheckState(0,Qt.Checked)
            else:
                item.setCheckState(0,Qt.Unchecked)       

        if self.ui.toggleall_checkBox.checkState() == Qt.Checked:
            self.ui.togglenolens_checkBox.setCheckState(Qt.Checked)
        else:
            self.ui.togglenolens_checkBox.setCheckState(Qt.Unchecked)



#==============================
#
#==============================
    def toggleNoLenses(self):
        #log.info("toggleNoLenses")
        
        for i in range(self.ui.treeWidget.topLevelItemCount()):
            item = self.ui.treeWidget.topLevelItem(i)
            if item.text(5) == "----":
                if self.ui.togglenolens_checkBox.checkState() == Qt.Checked:
                    item.setCheckState(0,Qt.Checked)
                else:
                    item.setCheckState(0,Qt.Unchecked)
        

#==============================
#
#==============================
    def clearButton(self):
        log.info("clearButton")
        for i in range(self.ui.treeWidget.topLevelItemCount()):
            item = self.ui.treeWidget.topLevelItem(i)
            log.debug(item.checkState(0))
         
        Filelist.clear()
        item_list.clear()
        self.ui.treeWidget.clear()



    

#==============================
# 
#==============================
    def openSource(self):
        global SourceDir
        global mime
        global Filelist
        global item_list
        
        
        options = QFileDialog.Options()
        file_path, file_type = QFileDialog.getOpenFileNames(self, 
                                                            "Get images...", 
                                                            settings.SourceDir , 
                                                            "Images (*.arw *.jpg *.png *.tif)",
                                                            options=options)        
        if file_path:
            Filelist = file_path
            # Change SourceDir to current directory from first file in list
            SourceDir = os.path.dirname(file_path[0])
            self.ui.sourcedir_label.setText(SourceDir)
            log.info("directory is %s" % SourceDir)
            
            self.ui.toggleall_checkBox.setCheckState(Qt.Checked)
            self.ui.togglenolens_checkBox.setCheckState(Qt.Checked)

            item_list = filemgr.readFiles(file_path, item_list)
            
            self.redrawTreeWidget(item_list)



#==============================
#
#==============================
    def redrawTreeWidget(self, item_list):
        log.debug("item_list is %d" % len(item_list))
        self.ui.treeWidget.clear()
        for line in item_list:
            item = QTreeWidgetItem()
            item.setCheckState(0,Qt.Checked)
            item.setText(1, str(line[1]))
            item.setText(2, line[2])
            item.setText(3, line[3])
            item.setText(4, line[4])
            item.setText(5, line[5])
            item.setText(6, line[6])
            item.setText(7, line[7])
            item.setText(8, line[8])

            self.ui.treeWidget.addTopLevelItem(item)
            
#            self.ui.treeWidget.setColumnHidden(1,True)



#==============================
#
#==============================
    def destDirButton(self):
        global DestDir
        
        if DestDir == None:
            DestDir = settings.DestDir
            
        dir = QFileDialog.getExistingDirectory(self, 'Select a folder:', DestDir, QFileDialog.ShowDirsOnly)
        if dir:
            DestDir = dir
        else:
            DestDir = None
            
        self.ui.dest_label.setText(DestDir)
            
    
 


    
    

    
    





  
#####################################################
#
#####################################################
class Filemanager():
     

#==============================
#
#==============================
    def __init__(self):
        log.info("Filemanager init")
 
 
 
#==============================
#
#==============================
    def readFiles(self,files, item_list):

        log.info("Filemanager.readFiles")
        log.debug("Filemanager.readFiles: %s" % files)
        
        completed = 0
        self.ui.progressBar.setValue(completed)
        self.ui.progressBar.setMaximum(len(files))
        for file in files:
            completed += 1
            self.ui.progressBar.setValue(completed)
            
            st_ino = os.stat(file)[1]
            if exif.inode_inlist(item_list, st_ino) == False:
                if exif.readJson(file) == True:
                    exif.readJsonCreateDate()
                    item_list.append([1,st_ino,
                                        Path(file).name,
                                        exif.fileModifyDate,
                                        exif.exifCreateDate,
                                        str(exif.LensModel),
                                        str(exif.FNumber),
                                        exif.GPSLatitude,
                                        exif.GPSLongitude])
        
        return item_list
        
        
        
#==============================
#
#==============================
if __name__ == "__main__":


    #log.setLevel(logging.WARNING)

    log.debug("------ start imgimport-------")

    app = QApplication(sys.argv)
    mime = MimeTypes()
    mime.add_type('image/tiff','.arw')
    
    # get global settings
    SourceDir = settings.SourceDir
    #DestDir=settings.DestDir


    exif = ExifTools()
    exif.initArglist()
    
    filemgr = Filemanager()
    filemgr.readFiles(Filelist, item_list)

    window = ImageWindow()
    window.show()
    sys.exit(app.exec_())
