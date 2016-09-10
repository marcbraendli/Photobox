import os
import time

TIMESTAMP=time.strftime("%d%m%Y-%H%M%S")
print "1/3-auskommentiert"
os.system("mogrify -resize 856x570 ~/workspace/capture_images/*.jpg")
print "2/3"
os.system("montage ~/workspace/capture_images/*.jpg -tile 2x2 -geometry +10+10 ~/workspace/temp_montage.jpg")
os.system("montage ~/workspace/temp_montage.jpg -geometry +4+23 ~/workspace/temp_montage2.jpg")
print "3/3"
os.system("montage ~/workspace/temp_montage2.jpg ~/workspace/footer_3.jpg -tile 2x1 -geometry +2+0 ~/workspace/temp_montage3.jpg")
os.system("montage ~/workspace/temp_montage3.jpg -geometry +0+20 ~/workspace/photobox_%s.jpg" %TIMESTAMP)
print "finished"