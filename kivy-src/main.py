from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import Screen
from kivy.factory import Factory
from kivy.clock import Clock
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.camera import Camera
from kivy.uix.image import Image

import os
import time


COUNTDOWN = 3
TIMESTAMP=0
DAYSTAMP=0
MAILADRESS=0


class LoginScreen(Screen):

    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        global MAILADRESS
        MAILADRESS="marc_braendli@hotmail.com"

    def next(self):
        self.manager.current = "capture"


class CaptureScreen(Screen):

    def __init__(self, **kwargs):
        super(CaptureScreen, self).__init__(**kwargs)
        global TIMESTAMP
        global DAYSTAMP
        self.start_button = Factory.StartButton()
        self.start_button.action = self.show_countdown
        self.countdown = Factory.Countdown()
        self.countdown.action = self.take_picture
        self.bind(on_pre_enter=self.show_start)
        cam = Camera(resolution=(640, 480), play=True)
        self.add_widget(cam)
        
        self.image = Image(source="")

        self.iteration = 0
        TIMESTAMP=time.strftime("%d%m%Y-%H%M%S")
        DAYSTAMP=time.strftime("%d%m%Y")

    def show_start(self, *kwargs):
        self.float_layout.add_widget(self.start_button)

    def show_countdown(self, *kwargs):
        self.float_layout.remove_widget(self.start_button)
        self.float_layout.remove_widget(self.image)
        self.float_layout.add_widget(self.countdown)
        self.countdown.start()

    def take_picture(self, *kwargs):
        print "take_picture"
        #path="~/workspace/capture_images/capture%s_%s.jpg" %(TIMESTAMP, self.iteration)
        #path=os.path.expanduser(path)
        self.float_layout.remove_widget(self.countdown)
        os.system("gphoto2 --capture-image-and-download --filename ~/workspace/capture_images/capture%s_%s.jpg" %(TIMESTAMP, self.iteration))
        Clock.schedule_interval(self.check_for_picture, 0.5)
        #self.show_picture(path)

    def check_for_picture(self, *kwargs):
        path="~/workspace/capture_images/capture%s_%s.jpg" %(TIMESTAMP, self.iteration)
        path=os.path.expanduser(path)
        self.float_layout.remove_widget(self.countdown)
        if os.path.isfile(path):
            self.show_picture(path)
            Clock.unschedule(self.check_for_picture)

    def show_picture(self, path):
        print "show_picture"
        self.image = Image(source=path)
        #self.float_layout.clear_widgets()
        self.float_layout.remove_widget(self.countdown)
        self.float_layout.add_widget(self.image) #marc
        if self.iteration == 3:
            self.iteration = 0
            self.float_layout.clear_widgets()#marc
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
        
        
        
    def assembly_and_print(self, *kwargs):
        print"assembly_and_print"
        self.assembly()
        #self.print_picture()
        #self.send_mail()
        self.clean_up()   
        
        
    def assembly(self, *kwargs):  
        print "assembly"
        os.system("mogrify -resize 856x570 ~/workspace/capture_images/*.jpg")
        os.system("montage ~/workspace/capture_images/*.jpg -tile 2x2 -geometry +10+10 ~/workspace/temp_montage.jpg")
        os.system("montage ~/workspace/temp_montage.jpg -geometry +4+23 ~/workspace/temp_montage2.jpg")
        os.system("montage ~/workspace/temp_montage2.jpg ~/workspace/footer_3.jpg -tile 2x1 -geometry +2+0 ~/workspace/temp_montage3.jpg")
        os.system("montage ~/workspace/temp_montage3.jpg -geometry +0+20 ~/workspace/photobox_%s.jpg" %TIMESTAMP)
    
    def send_mail(self, *kwargs):
        print "send_mail"
        os.system("mail < ~/workspace/Photobox/mail_message %s -s \"Photobox2\" -A \"/home/photobox/workspace/photobox_%s.jpg\"" %(MAILADRESS, TIMESTAMP)) 
       
    def print_picture(self, *kwargs):
        print "print_picture"
        os.system("lp -d CP9810DW ~/workspace/photobox_%s.jpg" %TIMESTAMP)
       
    def clean_up(self, *kwargs):
        print "clean_up"
        path ="/media/usb0/photobooth_archive/photobox_%s" %DAYSTAMP
        self.assure_path_exists(path)
        os.system("cp ~/workspace/photobox_%s.jpg /media/usb0/photobooth_archive/photobox_%s/" %(TIMESTAMP, DAYSTAMP))
        os.system("rm ~/workspace/capture_images/*.jpg")
        os.system("rm ~/workspace/photobox*.jpg")
        os.system("rm ~/workspace/temp*.jpg")
       
    def assure_path_exists(self, *kwargs):
        dirpath="/media/usb0/photobooth_archive/photobox_%s" %DAYSTAMP
        if not os.path.exists(dirpath):
           os.makedirs(dirpath)

class ScreenSaver(Screen):
    def show_picture(self, *kwargs):
        print "show_picture_slideshow"
        #self.float_layout.clear_widgets()
        #self.image = Image(source=path)
        #self.float_layout.add_widget(self.image) #marc
        #Clock.schedule_once(self.show_picture, 5)"""
    
class MainLayout(FloatLayout):

    def __init__(self, **kwargs):
        super(MainLayout, self).__init__(**kwargs)
        self.screen_manager.current = "capture"

 
class MyApp(App):
    def build(self):
        return MainLayout()

    
if __name__ == '__main__':
    MyApp().run()