
import os

# Global definitions

qtCreatorFile   =   "main.ui" # Enter file here.

SourceDir       =   "/home/hwa/tmp/exiftest/org"
DestDir         =   os.environ["HOME"] + os.path.sep + "tmp" + os.path.sep + "kamera"
acceptedImages  =   ["image/jpeg", "image/png","image/tiff","image/gif"]
FilenameFormat  =   "%Y%m%d_%H%M%S%%-c.%%le"

Logdir          =   os.environ["HOME"] + os.path.sep + "tmp"




