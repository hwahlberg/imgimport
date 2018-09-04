

import os
from subprocess import Popen, PIPE, STDOUT, run
import glob
import json

from logger import log



class ExifTools:
    
    def __init__(self):
        log.info("init ExifTools")
        self.prog = "exiftool"
        self.exifCreateDate=None
        self.fileModifyDate=None
        self.FNumber=None
        self.LensModel=None
        self.jsonData=None
        self.FileType= None
        self.GPSLatitude = None
        self.GPSLongitude = None
        self.arglist = []



    def inode_inlist(self,lista, inode):
        for line in lista:
            if line[1] == inode:
                return True

        return False
   
        
    def about(self):
        log.info("ExifTools prog = " + self.prog)
  
  
  
    def readJson(self,image):
        
        #log.info("readJson %s" % image)
        proc = Popen(["exiftool", "-json","-g",image],
                                stdout=PIPE, 
                                stdin=PIPE,
                                stderr=PIPE)
        lines = proc.stdout

        json_lines=b''
        for line in proc.stdout:
            json_lines += line

        proc.wait()

        try:
            self.jsonData = json.loads(json_lines.decode('UTF-8'))
            self.FileType=self.jsonData[0]['File']['FileType']
            self.FNumber=self.jsonData[0]['EXIF']['FNumber']
            self.LensModel=self.jsonData[0]['EXIF']['LensModel']
            if 'GPSLatitude' in self.jsonData[0]['Composite']:
                log.debug("readjson %s " % self.jsonData[0]['Composite']['GPSLatitude'])
                self.GPSLatitude=self.jsonData[0]['Composite']['GPSLatitude']
                self.GPSLongitude=self.jsonData[0]['Composite']['GPSLongitude']            
            else:
                self.GPSLatitude = None
                self.GPSLongitude = None

            return True
        except:
            log.info("readJson False: %s" % image)
            return False




    def readJsonCreateDate(self):
        self.exifCreateDate=None
        self.fileModifyDate=None
        
        #log.info("readJsonCreateDate")

        # Get CreateDate per filetype
        if self.FileType == 'PNG':
        # get rid of any trailing "...+01:00"
            try:
                self.exifCreateDate=self.jsonData[0]['PNG']['CreateDate'].rsplit('+',1)[0]
            except:
                pass
            
        else:
            try:
                self.exifCreateDate=self.jsonData[0]['EXIF']['CreateDate'].rsplit('+',1)[0]
            except:
                pass
            
        #if FileModifyDate exists, it is always in File-section(?) 
        try:
            self.fileModifyDate=self.jsonData[0]['File']['FileModifyDate'].rsplit('+',1)[0]
        except:
            pass





    def NewCreateDate(self,newdate,  image, out,  err):
        log.info("NewCreateDate: " + image + ": set new date: " + newdate)
    
        proc = Popen([self.prog,  \
            "-CreateDate=\"" +newdate+ "\"", \
                "-P", \
                "-r", \
                "-overwrite_original_in_place",  \
                image], \
                stdout=out, \
                stderr=err)
                                                
     
        proc.wait()



    def RenameImage(self,image, FilenameFormat, filenum, out,  err):

        log.info("RenameImage: " + image)

        if filenum > 0:
            fnameFormat = FilenameFormat + "-%04d" % filenum + ".%%le"
        else:
            fnameFormat = FilenameFormat + "%%-c.%%le"

        proc = Popen([self.prog,  \
                                                "-FileName<CreateDate", \
                                                "-d", fnameFormat, \
                                                "-P", \
                                                "-r", \
                                                image], \
                                                stdout=out, \
                                                stderr=err)
                                                

        proc.wait()



    def MoveImages(self,sourcedir,  destdir,  inodes,  out,  err):
        #get the new name from inode
        lista = glob.glob(sourcedir + os.path.sep + "*")
        
        log.info("MoveImages: sourcedir=%s, destdir=%s" % (sourcedir,  destdir))
        
        for l in lista:
            st_ino = os.stat(l)[1]
            if st_ino in inodes:
                log.info("move image: " + l + ": inode: " + str(st_ino))
                proc = Popen([self.prog,  \
                                                        "-Directory<CreateDate", \
                                                        "-d", destdir + "/%Y/%m%d", \
                                                        "-P", \
                                                        "-r", \
                                                        l], \
                                                        stdout=out, \
                                                        stderr=err)
                proc.wait()





###############################
#
###############################
    def initArglist(self):
        log.debug("initArglist")
        
        self.arglist.clear()
        self.arglist.append("exiftool")
        self.arglist.append("-P")
        self.arglist.append("-overwrite_original_in_place")



###############################
#
###############################
    def appendArglist(self,item):
        log.debug("appendArglist %s" % item)
        self.arglist.append(item)



###############################
#
###############################
    def appendFnumber(self,fnum):
        self.arglist.append("-FNumber=" + fnum + "")



###############################
#
###############################
    def appendCreateDate(self, newdate):
        log.debug("set new date: " + newdate) 
        self.arglist.append("-CreateDate=\"" +newdate+ "\"")



###############################
#
###############################
    def appendRenameImage(self, filenameFormat):
        self.arglist.append("-FileName<CreateDate")
        self.arglist.append("-d")
        self.arglist.append(filenameFormat)
    
    
    
    
###############################
#
###############################
    def appendMoveImages(self,destdir):

        self.arglist.append("-Directory<CreateDate")
        self.arglist.append("-d")
        self.arglist.append(destdir + "/%Y/%m")
    
 

###############################
#
###############################
    def appendLatLng(self,lat, lng):
        self.arglist.append("-GPSLatitude=%s" % lat)
        self.arglist.append("-GPSLatitudeRef=0")
        self.arglist.append("-GPSLongitude=%s" % lng)
        self.arglist.append("-GPSLongitudeRef=0")




###############################
#
###############################
    def executeExiftool(self):
        log.debug("executeExiftool")
        
        fdnull = os.open(os.devnull, os.O_WRONLY)
        log.info("executeExiftool: %s" % str(self.arglist))
        proc = Popen(self.arglist, stdout=fdnull, stderr=fdnull)
        proc.wait()
        
        log.debug("executeExiftool")




