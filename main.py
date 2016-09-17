from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import Screen
from kivy.factory import Factory
from kivy.clock import Clock
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.camera import Camera
from kivy.uix.image import Image
from threading import Thread

import os
import time
import csv
import re


COUNTDOWN = 3


class LoginScreen(Screen):

    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        self.bind(on_pre_enter=self.prepare)

    def prepare(self, *args):
        self.manager.mail_address = ""

    def next(self, mail_input):
        if self.validateEmail(mail_input):
            print "Gueltige Adresse"
            self.manager.mail_address = mail_input
            a=open('/home/photobox/workspace/mailadressen.csv', 'ab')
            b = csv.writer(a)
            b.writerow(['%s' %mail_input, '%s' %self.manager.timestamp])
            a.close()
            self.manager.current = "capture"
        else:
            print "Ungueltige Adresse!!!"
            self.message_text = "Bitte gib eine gueltige Email-Adresse ein"
        
        

    def validateEmail(self, email):
        if len(email) > 7:
            if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,4}|[0-9]{1,3})(\\]?)$", email) != None:
                self.manager.timestamp = time.strftime("%d%m%Y-%H%M%S")
                self.manager.daystamp = time.strftime("%d%m%Y")
                return True
            return False


class CaptureScreen(Screen):

    def __init__(self, **kwargs):
        super(CaptureScreen, self).__init__(**kwargs)
        self.start_button = Factory.StartButton()
        self.start_button.action = self.show_countdown
        self.countdown = Factory.Countdown()
        self.countdown.action = self.take_picture
        self.bind(on_pre_enter=self.show_start)
        #self.cam = Camera(resolution=(640, 480), play=False)
        self.cam = Camera(resolution=(720, 540), play=True)
        self.add_widget(self.cam)
        
        self.image = Image(source="")

        self.iteration = 0

    def show_start(self, *kwargs):
        self.float_layout.add_widget(self.start_button)
        self.cam.play = True

    def show_countdown(self, *kwargs):
        self.float_layout.remove_widget(self.start_button)
        self.float_layout.remove_widget(self.image)
        self.float_layout.add_widget(self.countdown)
        self.countdown.start()

    def take_picture(self, *kwargs):
        print "take_picture", self.manager.timestamp
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
        print "show_picture"
        self.image = Image(source=path)
        self.float_layout.clear_widgets()
        # self.float_layout.remove_widget(self.countdown)
        self.float_layout.add_widget(self.image) #marc
        if self.iteration == 3:
            self.iteration = 0
            self.float_layout.clear_widgets()#marc
            self.cam.play = False
            print"switch to pending"
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
        print"assembly_and_print"
        Thread(target=self.assembly).start()
        self.shown_text = "Please wait..."
            
    def assembly(self, *kwargs):  
        print "assembly"
        os.system("mogrify -resize 856x570 ~/workspace/capture_images/*.jpg")
        os.system("montage ~/workspace/capture_images/*.jpg -tile 2x2 -geometry +10+10 ~/workspace/temp_montage.jpg")
        os.system("montage ~/workspace/temp_montage.jpg -geometry +4+23 ~/workspace/temp_montage2.jpg")
        os.system("montage ~/workspace/temp_montage2.jpg ~/workspace/Photobox/footer_3.jpg -tile 2x1 -geometry +2+0 ~/workspace/temp_montage3.jpg")
        os.system("montage ~/workspace/temp_montage3.jpg -geometry +0+20 ~/workspace/photobox_%s.jpg" % self.manager.timestamp)
        self.print_picture()
        self.send_mail()
        self.clean_up()
        Clock.schedule_once(self.show_take_picture)

    def send_mail(self, *kwargs):
        print "send_mail"
        os.system("mail < ~/workspace/Photobox/mail_message %s -s \"Photobox\" -A \"/home/photobox/workspace/photobox_%s.jpg\"" %
                  (self.manager.mail_address, self.manager.timestamp))
       
    def print_picture(self, *kwargs):
        print "print_picture"
        os.system("lp -d CP9810DW ~/workspace/photobox_%s.jpg" % self.manager.timestamp)
       
    def clean_up(self, *kwargs):
        print "clean_up"
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

    def show_take_picture(self, *kwargs):
        self.shown_text = "Bitte entnehmen Sie waht ever..."
        Clock.schedule_once(self.show_screen_saver, 15)

    def show_screen_saver(self, *kwargs):
        Clock.unschedule(self.show_screen_saver)
        self.manager.current = "screen_saver"


class ScreenSaver(Screen):
    def show_picture(self, *kwargs):
        print "show_picture_slideshow"
        #self.float_layout.clear_widgets()
        #self.image = Image(source=path)
        #self.float_layout.add_widget(self.image) #marc
        #Clock.schedule_once(self.show_picture, 5)"""

    def show_login(self):
        self.manager.current = "login"


class MainLayout(FloatLayout):

    def __init__(self, **kwargs):
        super(MainLayout, self).__init__(**kwargs)
        #self.screen_manager.current = "capture"

 
class MyApp(App):

    def build(self):
        return MainLayout()

    
if __name__ == '__main__':
    MyApp().run()