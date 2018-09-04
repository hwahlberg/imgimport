#!/usr/bin/env python3


from PyQt5.QtWidgets import *
from PyQt5 import uic
from logger import log

qtImportWindowFile="import.ui"


class ImportWindow(QDialog):

    def __init__(self):
        log.info("ImportWindow.__init__")
        
        ui_importwindow, QtBaseClass = uic.loadUiType(qtImportWindowFile)
        super(ImportWindow,self).__init__()
        self.ui=ui_importwindow()
        self.ui.setupUi(self)
        self.ui.buttonBox.accepted.connect(self.ok)
        self.ui.buttonBox.rejected.connect(self.cancel)


    def ok(self):
        log.info("OK")
        self.close()
        
        
    def cancel(self):
        log.info("Cancel")
        self.close()


        
