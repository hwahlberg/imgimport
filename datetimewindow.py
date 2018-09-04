#!/usr/bin/env python3

import datetime

from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt

from logger import log

qtDateTimeUIFile="datetime.ui"

manual_createDate=None
#datetime_format = "%Y-%m-%d %H:%M:%S"
datetime_format = "%Y-%m-%d"
incSeconds = "10"


#>>> import datetime                                                                                                            
#>>> start = "2012-06-20 12:10:00"
#>>> dt = datetime.datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
#>>> dt = dt + datetime.timedelta(seconds=10)
#>> dt.strftime("%Y-%m-%d %H:%M:%S")


class DateTimeWindow(QDialog):

    def __init__(self,imagefile, exifCreateDate, fileModifyDate, ifnum):
        global manual_createDate
        
        log.info("DateTimeWindow.__init__")
               
        ui_datetimewindow, QtBaseClass = uic.loadUiType(qtDateTimeUIFile)
        super(DateTimeWindow,self).__init__()
        self.ui=ui_datetimewindow()
        self.ui.setupUi(self)
        
        now = datetime.datetime.today()        
        manual_createDate = now.strftime(datetime_format) + " 12:00:00"
        self.ui.datetime_lineEdit.setText(manual_createDate)
        self.ui.incsec_lineEdit.setText(incSeconds)
        
        self.setStyleSheet(open("styles.css", "r").read())		




    def inctime(self, createdate):
        global incSeconds
        
        log.debug("inctime!!")
        
        dt = datetime.datetime.strptime(createdate, "%Y-%m-%d %H:%M:%S")
        dt = dt + datetime.timedelta(seconds=int(incSeconds))
        
        return dt.strftime("%Y-%m-%d %H:%M:%S")


    def save(self):
        global incSeconds
            
        log.info("SAVE %s" % manual_createDate)
        
        incSeconds = self.ui.incsec_lineEdit.text()
        
        self.close()
        return self.ui.datetime_lineEdit.text(), self.ui.incsec_lineEdit.text()
    
        
        
    def cancel(self):
        log.info("Cancel %s" % self.Rejected)
        self.close()
        return self.Rejected


        
