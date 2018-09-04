#!/usr/bin/env python3

import math

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic

from PyQt5.QtWebKit import *
from PyQt5.QtWebKitWidgets import QWebView , QWebPage

from logger import log

qtGPSUIFile="gps.ui"


maphtml = '''
<!DOCTYPE html>
<html>
    <head>
    <meta name="viewport" content="initial-scale=1.0, user-scalable=no"/>
    <meta http-equiv="content-type" content="text/html; charset=UTF-8"/>
    <title>Google Maps JavaScript API v3 Example: Geocoding Simple</title>
    <link href="http://code.google.com/apis/maps/documentation/javascript/examples/default.css" rel="stylesheet" type="text/css" />
    <script src="http://maps.google.com/maps/api/js?v=3.5&amp;sensor=false"></script>

    <script type="text/javascript">
    var geocoder;
    var map;
    var marker;
    function initialize() {
    
        geocoder = new google.maps.Geocoder();
        var latlng = new google.maps.LatLng(64.750244, 20.950917);
        var myOptions = {
            zoom: 12,
            center: latlng,
            mapTypeId: google.maps.MapTypeId.ROADMAP
        }
        map = new google.maps.Map(document.getElementById("map"), myOptions);
    

        marker = new google.maps.Marker({
            map: map,
            position: latlng,
            draggable: true,
            title: 'Drag me!'
        });

        
    
        marker.addListener('click', function() {
            latlng = marker.getPosition()
            
            self.click(latlng.lat(),latlng.lng())
        });
        
        
        map.addListener('click', function(e) {
            marker.setPosition(e.latLng)
            self.click(e.latLng.lat(),e.latLng.lng())
        });

    }
    
    
    function codeAddress() {
        var address = document.getElementById("address").value;
        geocoder.geocode( { 'address': address}, function(results, status) {            
            if (status == google.maps.GeocoderStatus.OK) {
                map.setCenter(results[0].geometry.location);
                marker.setPosition(results[0].geometry.location);
                self.click(results[0].geometry.location.lat(), results[0].geometry.location.lng());

            } else {
                alert("Geocode was not successful for the following reason: " + status);
            }
        });
    }
    </script>

    <style type="text/css">
        #controls {
            position: absolute;
            bottom: 1em;
            left: 100px;
            width: 400px;
            z-index: 20000;
            padding: 0 0.5em 0.5em 0.5em;
        }
        html, body, #map {
            margin: 0;
            width: 100%;
            height: 100%;
        }
    </style>
    </head>

<body onload="initialize()">
<div id="controls">

<input type="button" value="Geocode" onclick="codeAddress()">
<input id="address" type="textbox" value="Skellefteå">

</div>
<div id="map"></div>
</body>
</html>
'''


class GPSWindow(QDialog):
    latitude = ""
    longitude = ""
    
    def __init__(self):
        
        log.info("GPSWindow.__init__")
               
        ui_gpswindow, QtBaseClass = uic.loadUiType(qtGPSUIFile)
        super(GPSWindow,self).__init__()
        self.ui=ui_gpswindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Google Google Maps Maps")
        
        self.web = QWebView()
        self.web.setMinimumSize(800,800)
        self.web.page().mainFrame().addToJavaScriptWindowObject('self', self)
        self.web.setHtml(maphtml)
        
        self.ui.frame.setLayout(self.ui.gridLayout)
        self.ui.gridLayout.addWidget(self.web, 0,0,1,1)
        
        self.ui.dd_latitude.setText(self.latitude)
        self.ui.dd_longitude.setText(self.longitude)
        self.ui.dms_latitude.setText(self.latitude)
        self.ui.dms_longitude.setText(self.longitude)
        
        self.setStyleSheet(open("styles.css", "r").read())		






    @pyqtSlot(float, float)
    def click(self, lat, lng):
        log.debug("click")
        self.latitude = str("%.4f" % lat)
        self.longitude = str("%.4f" % lng)
        self.ui.dd_latitude.setText(self.latitude)
        self.ui.dd_longitude.setText(self.longitude)
        
        degrees     = math.floor(lat)
        minutes     = math.floor(60*(lat-degrees))
        seconds     = 3600*(lat-degrees) - 60*minutes
        log.debug("lat=%f, minutes=%f, seconds=%f" % (lat,minutes,seconds))
        self.ui.dms_latitude.setText("N %.0f %.0f' %.2f\"" % (degrees, minutes, seconds))
        
        degrees     = math.floor(lng)
        minutes     = math.floor(60*(lng-degrees))
        seconds     = 3600*(lng-degrees) - 60*minutes
        self.ui.dms_longitude.setText("E %.0f %.0f' %.2f\"" % (degrees, minutes, seconds))        


    def save(self):
            
        log.info("GPSWindow SAVE")
        
        
        self.close()
        return self.latitude, self.longitude
    
        
        
    def cancel(self):
        log.info("GPSWindow Cancel")
        self.close()
        return self.Rejected


        
