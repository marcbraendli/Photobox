# -*- coding: UTF-8 -*-

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import Screen
from kivy.factory import Factory
from kivy.clock import Clock
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.camera import Camera
from kivy.uix.image import Image
from kivy.properties import StringProperty
from threading import Thread
from kivy.config import Config
from kivy.core.window import Window
from kivy.logger import Logger

import os
import time
import csv
import re
import random
import socket

#Enumerations, don't change
COLLECT_MAILADRESS = 1
ONLY_CAPTURING = 2


#Global variables
REMOTE_SERVER = "www.google.com"
COUNTDOWN = 3
WATCHDOG_TIME = 300 #5 Minuten



#Possible values for MODE are:
#   -COLLECT_MAILADRESS (save mailadress in .csv and capture photos)
#   -ONLY_CAPTURING (capture photo without any mailadress inputs)
#
MODE = COLLECT_MAILADRESS


class LoginScreen(Screen):

    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        self.startup_check()
        self.bind(on_pre_enter=self.prepare)

    def timeout (self, *args):
        Logger.info( 'Application: Login User Timeout')
        self.mail_input.focus =False
        self.manager.current = "screen_saver"
        
    def startup_check(self, *args):
        if MODE == COLLECT_MAILADRESS:
            Logger.info('Application: MODE = COLLECT_MAILADRESS')
        elif MODE == ONLY_CAPTURING:
            Logger.info('Application: MODE = ONLY_CAPTURING')
        else:
            Logger.info('Application: Wrong MODE value  = %s' %MODE)
            self.programmabbruch
        if self.is_connected():
            Logger.info('Application: Internet connectet')
        else:
            Logger.info('Application: No Internet!!!')
            self.programmabbruch
        if os.path.exists('/media/usb0/photobooth_archive'):
            Logger.info('Application: USB-Stick connected')
        else:
            Logger.info('Application: USB-Stick missed')
            self.programmabbruch
            
    def prepare(self, *args):
        self.manager.mail_address = ""
        Clock.schedule_once(self.timeout, WATCHDOG_TIME)
        #Watchdog timer, reset to screensaver after WATCHDOG_TIME minutes with no email input

    def next(self, mail_input):
        if self.validateEmail(mail_input):
            Clock.unschedule(self.timeout)
            #deactivate login watchdog
            Logger.info( 'Application: Gültige Adresse')
            self.manager.mail_address = mail_input
            self.manager.current = "agreement"
        else:
            Logger.info( 'Application: Ungültige Adresse!!!')
            self.message_text = "Bitte geben Sie eine gültige E-mail Adresse ein"

    def validateEmail(self, email):
        if len(email) > 7:
            if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,4}|[0-9]{1,3})(\\]?)$", email) != None:
                self.manager.timestamp = time.strftime("%d%m%Y-%H%M%S")
                self.manager.daystamp = time.strftime("%d%m%Y")
                Logger.info( 'Application: Timestamp: %s' %self.manager.timestamp)
                Logger.info( 'Application: Daystamp:  %s' %self.manager.daystamp)
                return True
            return False
            
    def is_connected(self, *args):
      try:
      # see if we can resolve the host name -- tells us if there is
      # a DNS listening
        host = socket.gethostbyname(REMOTE_SERVER)
        # connect to the host -- tells us if the host is actually
        # reachable
        s = socket.create_connection((host, 80), 2)
        return True
      except:
         pass
      return False
            
class AgreementScreen(Screen):
    def __init__(self, **kwargs):
        super(AgreementScreen, self).__init__(**kwargs)
        self.bind(on_enter=self.prepare)
        
        
    def prepare (self, *args):
        Clock.schedule_once(self.timeout, WATCHDOG_TIME)
        #Watchdog timer, reset to screensaver after WATCHDOG_TIME minutes with no email input
        
    def timeout (self, *args):
        Logger.info( 'Application: Agreement User Timeout')
        self.manager.current = "screen_saver"
    
    def if_agree (self, *args):
        Logger.info( 'Application: Agreet')
        Clock.unschedule(self.timeout)
        #deactivate agreement watchdog
        a = open('/media/usb0/mailadressen.csv', 'ab')
        b = csv.writer(a)
        b.writerow(['%s' % self.manager.timestamp, '%s' %self.manager.mail_address])
        a.close()
        self.manager.current = "capture"


class CaptureScreen(Screen):

    def __init__(self, **kwargs):
        super(CaptureScreen, self).__init__(**kwargs)
        self.start_button = Factory.StartButton()
        self.start_button.action = self.show_countdown
        self.countdown = Factory.Countdown()
        self.countdown.action = self.take_picture
        self.bind(on_pre_enter=self.show_start)
        self.cam = Camera(resolution=(720, 540), play=True)
        self.add_widget(self.cam)

        # We need to stop the camera, because it introduces lag.
        # But we can not stop the camera at init as this results in a bug
        # (camera not updating the picture at all) when we try to play the
        # camera later.

        def stop_camera(*kwargs):
            self.cam.play = False
        Clock.schedule_once(stop_camera, 2)

        self.image = Image(source="")

        self.iteration = 0

    def timeout (self, *args):
        self.manager.current = "screen_saver"

    def show_start(self, *kwargs):
        self.float_layout.add_widget(self.start_button)
        Clock.schedule_once(self.timeout, WATCHDOG_TIME)
        #activate watchdog timer, reset to screensaver after WATCHDOG_TIME minutes with no start
        self.cam.play = True
        Window.release_all_keyboards()

    def show_countdown(self, *kwargs):
        Clock.unschedule(self.timeout)
        #deactivate capture watchdog
        self.float_layout.remove_widget(self.start_button)
        self.float_layout.remove_widget(self.image)
        self.float_layout.add_widget(self.countdown)
        self.countdown.start()

    def take_picture(self, *kwargs):
        Logger.info( 'Application: take_picture')
        self.float_layout.remove_widget(self.countdown)
        Thread(target=self._take_picture_aync).start()

    def _take_picture_aync(self, *kwargs):
        os.system("gphoto2 --capture-image-and-download --filename ~/workspace/capture_images/capture%s_%s.jpg" %
                  (self.manager.timestamp, self.iteration))
        path = "~/workspace/capture_images/capture%s_%s.jpg" % \
               (self.manager.timestamp, self.iteration)
        path = os.path.expanduser(path)
        Clock.schedule_once(lambda x: self.show_picture(path))

    def show_picture(self, path):
        Logger.info( 'Application: show_picture')
        self.image = Image(source=path)
        self.float_layout.clear_widgets()
        self.float_layout.add_widget(self.image)
        if self.iteration == 3:
            self.iteration = 0
            self.float_layout.clear_widgets()
            self.cam.play = False
            self.manager.current = "pending"  
        else:
            self.iteration += 1
            Clock.schedule_once(self.show_countdown, 2)


class Countdown(AnchorLayout):

    def __init__(self, **kwargs):
        super(Countdown, self).__init__(**kwargs)
        self.count = COUNTDOWN

    def start(self):
        Clock.schedule_interval(self.count_down, 1)

    def count_down(self, *kwargs):
        self.count -= 1
        if not self.count:
            Clock.unschedule(self.count_down)
            self.action()
            self.count = COUNTDOWN


class PendingScreen(Screen):

    def __init__(self, **kwargs):
        super(PendingScreen, self).__init__(**kwargs)
        self.bind(on_enter=self.assembly_and_print)
                   
    def assembly_and_print(self, *kwargs):
        Thread(target=self.assembly).start()
            
    def assembly(self, *kwargs):  
        Logger.info( 'Application: assembly')
        os.system("mogrify -resize 856x570 ~/workspace/capture_images/*.jpg")
        os.system("montage ~/workspace/capture_images/*.jpg -tile 2x2 -geometry +10+10 ~/workspace/temp_montage.jpg")
        os.system("montage ~/workspace/temp_montage.jpg -geometry +4+23 ~/workspace/temp_montage2.jpg")
        os.system("montage ~/workspace/temp_montage2.jpg ~/workspace/Photobox/footer_3.jpg -tile 2x1 -geometry +2+0 ~/workspace/temp_montage3.jpg")
        os.system("montage ~/workspace/temp_montage3.jpg -geometry +0+20 ~/workspace/photobox_%s.jpg" % self.manager.timestamp)
        self.print_picture()
        if MODE == COLLECT_MAILADRESS:
            self.send_mail()       
        self.clean_up()
        Logger.info( 'Application: assembly_end')
        Clock.schedule_once(self.show_take_out_picture, 70)

    def send_mail(self, *kwargs):
        Logger.info( 'Application: send_mail')
        os.system("mail < ~/workspace/Photobox/mail_message %s -s \"Ihr Bild von der Photobox\" -A \"/home/photobox/workspace/photobox_%s.jpg\"" %
                  (self.manager.mail_address, self.manager.timestamp))
       
    def print_picture(self, *kwargs):
        Logger.info( 'Application: print_picture')
        #os.system("lp -d CP9810DW ~/workspace/photobox_%s.jpg" % self.manager.timestamp)
       
    def clean_up(self, *kwargs):
        Logger.info( 'Application: clean_up')
        path ="/media/usb0/photobooth_archive/photobox_%s" % self.manager.timestamp
        self.assure_path_exists(path)
        os.system("cp ~/workspace/photobox_%s.jpg /media/usb0/photobooth_archive/photobox_%s/" %
                  (self.manager.timestamp, self.manager.daystamp))
        os.system("rm ~/workspace/capture_images/*.jpg")
        os.system("rm ~/workspace/photobox*.jpg")
        os.system("rm ~/workspace/temp*.jpg")
       
    def assure_path_exists(self, *kwargs):
        dir_path = "/media/usb0/photobooth_archive/photobox_%s" % \
                   self.manager.daystamp
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

    def show_take_out_picture(self, *kwargs):
        Clock.unschedule(self.show_take_out_picture)
        self.manager.current = "takeout"

    def show_screen_saver(self, *kwargs):
        self.manager.current = "screen_saver"

class TakeOutScreen(Screen):

    def __init__(self, **kwargs):
        super(TakeOutScreen, self).__init__(**kwargs)
        self.bind(on_enter=self.take_out_timer)
       
    def take_out_timer(self, *kwargs):
        Clock.schedule_once(self.show_screen_saver, 30)
        
    def show_screen_saver(self, *kwargs):
        Logger.info( 'Application: Start Screen Saver')
        Clock.unschedule(self.show_screen_saver)
        self.manager.current = "screen_saver"

class ScreenSaver(Screen):

    image_source = StringProperty("")

    def __init__(self, **kwargs):
        super(ScreenSaver, self).__init__(**kwargs)
        self.photos = []
        self.find_all_photos(self)
        self.bind(on_pre_enter=self.find_all_photos)

    def show_login(self, *kwargs):
    
        if MODE == COLLECT_MAILADRESS:
            self.manager.current = "login"
        elif MODE == ONLY_CAPTURING:
            self.manager.current = "capture"
        
        Clock.unschedule(self.change_image)

    def change_image(self, *kwargs):
        old_image = new_image = self.image_source
        while new_image == old_image and len(self.photos) > 1:
            new_image = random.choice(self.photos)
        self.image_source = new_image

    def add_photos(self, nothing, dirname, files):
        self.photos = []
        for f in files:
            if f.endswith('.jpg') or f.endswith('.JPG'):
                self.photos.append(os.path.join(dirname, f))
    
    def find_all_photos(self, *kwargs):
        Clock.unschedule(self.change_image)
        Clock.schedule_interval(self.change_image, 5)
        os.path.walk("/home/photobox/workspace/screensaver_images/", self.add_photos, None)
        self.change_image()

    def on_touch_down(self, touch):
        super(ScreenSaver, self).on_touch_down(touch)
        if self.collide_point(*touch.pos):
            self.show_login()


class MainLayout(FloatLayout):

    def __init__(self, **kwargs):
        super(MainLayout, self).__init__(**kwargs)
        
        if MODE == COLLECT_MAILADRESS:
            self.screen_manager.current = "login"
        elif MODE == ONLY_CAPTURING:
            self.screen_manager.current = "capture"
 
class MyApp(App):

    def build(self):
        return MainLayout()

    
if __name__ == '__main__':
    MyApp().run()
