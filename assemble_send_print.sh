#!/bin/bash

#BEARBEITEN und Speichern via imageMagick und usbmount
mogrify -resize 968x648 ~/photobooth/photobooth_images/*.jpg
montage ~/photobooth/photobooth_images/*.jpg -tile 2x2 -geometry +10+10 ~/photobooth/temp_montage.jpg
datum=$(date +%d%m%Y_%H%M)
mailadresse=$(marc@braendli.ch)
montage ~/photobooth/temp_montage.jpg ~/photobooth/footer.jpg -tile 2x1 -geometry +5+5 /media/usb0/photobooth_archive/photobox_${datum}.jpg

#VERSENDEN via ssmpt/mailutils/mpack
mail < ~/photobooth/mail_message ${mailadresse} -s "Photobox" -A "/media/usb0/photobooth_archive/photobox_${suffix}.jpg" 

#DRUCKEN via CUPS
#lp -d NPD DS_RX1 /media/usb0/photobooth_archive/photobox_${datum}.jpg

#AUFRAEUMEN
#rm /home/pi/photobooth_images/*.jpg
rm ~/photobooth/temp*

#HOW TO USE SHELL COMMANDS IN PYTHON
#import os
#def getch():
#    os.system("bash -c \"read -n 1\"") 
#getch()