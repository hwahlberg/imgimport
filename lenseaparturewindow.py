#!/usr/bin/env python3


from PyQt5.QtWidgets import *
from PyQt5 import uic
from logger import log

qtLenseApartureUIFile="lenseaparture.ui"


lensedata = []

# lists of Samyang lenses EXIF data
samyang14mm = ["-LensModel=Samyang MF 14mm F2.8 ED AS IF UMC", \
            "-FocalLength=14.0mm", \
            "-LensInfo=14mm f/2.8", \
            "-LensID=Samyang MF 14mm F2.8 ED AS IF UMC"]

samyang85mm = ["-LensModel=Samyang MF 85mm F1.4 AS IF UMC", \
            "-FocalLength=85.0mm", \
            "-LensInfo=85mm f/1.4", \
            "-LensID=Samyang MF 85mm F1.4 AS IF UMC"]




class LenseApartureWindow(QDialog):

    def __init__(self):
        log.info("LenseApartureWindow.__init__")
        self.fnumber = 0
        self.lensedata = []
        
        ui_lenseapartururewindow, QtBaseClass = uic.loadUiType(qtLenseApartureUIFile)
        super(LenseApartureWindow,self).__init__()
        self.ui=ui_lenseapartururewindow()
        self.ui.setupUi(self)
        self.ui.buttonBox.accepted.connect(self.save)
        self.ui.buttonBox.rejected.connect(self.cancel)
        self.ui.lenses_comboBox.addItem("-")
        self.ui.lenses_comboBox.addItem("Samyang 14mm")
        self.ui.lenses_comboBox.addItem("Samyang 85mm")
        self.ui.lenses_comboBox.currentIndexChanged.connect(self.selectionchange)

        self.setStyleSheet(open("styles.css", "r").read())		


    def selectionchange(self,i):
        log.info("Items in the list are %d:" %i)
		
        for count in range(self.ui.lenses_comboBox.count()):
            log.debug(self.ui.lenses_comboBox.itemText(count))
        
        log.debug("Current index %d: selection changed %s" % (i,self.ui.lenses_comboBox.currentText()))



    def save(self):
        global lensedata
        
        log.info("Save")

        self.fnumber = self.ui.fnumber_lineEdit.text()
        if self.fnumber == None or len(self.fnumber) == 0:
            self.fnumber="0"

        log.debug("fnumber=%s" % self.fnumber)
        lense = self.ui.lenses_comboBox.currentText()
        log.debug("lense=%s" % lense)

        lensedata =  []
        if lense != "-":
            if lense == "Samyang 14mm":
               lensedata =  samyang14mm
            if lense == "Samyang 85mm":
               lensedata =  samyang85mm
                
        self.close()
        return lensedata, self.fnumber
    
        
        
    def cancel(self):
        log.info("Cancel")
        self.close()
        return self.Rejected



        
