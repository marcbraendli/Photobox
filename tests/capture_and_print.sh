#!/bin/bash

timestemp=$(date +"%d%m%Y_%H%M")
echo Zeitstempel=${timestemp}

#FOTO AUSLOESEN UND DOWNLOADEN via gPhoto2
echo FOTO AUSLOESEN-auskommentiert
#gphoto2 -I 5 -F 4 --capture-image-and-download --filename ~/photobooth/capture_images/capture_${timestemp}-%n.jpg
#echo COPY FILES to /media/usb0/photobooth_archive/rohfotos_$(date +"%d%m%Y")
#cp ~/photobooth/capture_images/* /media/usb0/photobooth_archive/rohfotos_$(date +"%d%m%Y")/

#BEARBEITEN UND SPEICHERN via imageMagick und usbmount
echo BEARBEITEN 1/3
#mogrify -resize 968x648 ~/photobooth/capture_images/*.jpg
mogrify -resize 815x648 ~/photobooth/capture_images/*.jpg
echo BEARBEITEN 2/3
montage ~/photobooth/capture_images/*.jpg -tile 2x2 -geometry +10+10 ~/photobooth/temp_montage.jpg
echo BEARBEITEN 3/3
montage ~/photobooth/temp_montage.jpg ~/photobooth/footer.jpg -tile 2x1 -geometry +5+5 ~/photobooth/photobox_${timestemp}.jpg

#DRUCKEN via CUPS
echo DRUCKEN-auskommentiert
#lp -d CP9810DW ~/photobooth/photobox_${timestemp}.jpg

#VERSENDEN via ssmpt/mailutils/mpack
echo VERSENDEN-auskommentiert
#mail < ~/photobooth/mail_message marc@braendli.ch -s "Photobox" -A "/home/photobox/photobooth/photobox_${timestemp}.jpg" 

#AUFRAEUMEN
echo AUFRAEUMEN

mkdir -p /media/usb0/photobooth_archive/photobox_$(date +"%d%m%Y")
cp ~/photobooth/photobox_${timestemp}.jpg /media/usb0/photobooth_archive/photobox_$(date +"%d%m%Y")/

#rm ~/photobooth/capture_images/*.jpg
#rm ~/photobooth/photobox*.jpg
rm ~/photobooth/temp*.jpg

#HOW TO USE SHELL COMMANDS IN PYTHON
#import os
#def getch():
#    os.system("bash -c \"read -n 1\"") 
#getch()