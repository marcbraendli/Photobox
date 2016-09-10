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
timestamp=0
daystamp=0

class LoginScreen(Screen):

    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)

    def next(self):
        self.manager.current = "capture"


class CaptureScreen(Screen):

    def __init__(self, **kwargs):
        super(CaptureScreen, self).__init__(**kwargs)
        global timestamp
        global daystamp
        self.start_button = Factory.StartButton()
        self.start_button.action = self.show_countdown
        self.countdown = Factory.Countdown()
        self.countdown.action = self.take_picture
        self.bind(on_pre_enter=self.show_start)
        cam = Camera(resolution=(640, 480), play=True)
        self.add_widget(cam)

        self.iteration = 0
        timestamp=time.strftime("%d%m%Y-%H%M%S")
        daystamp=time.strftime("%d%m%Y")

    def show_start(self, *kwargs):
        self.float_layout.add_widget(self.start_button)

    def show_countdown(self, *kwargs):
        self.float_layout.remove_widget(self.start_button)
        
        self.float_layout.add_widget(self.countdown)
        self.countdown.start()

    def take_picture(self, *kwargs):
        print "take_picture"
        path="~/workspace/capture_images/capture%s_%s.jpg" %(timestamp, self.iteration)
        path=os.path.expanduser(path)
        self.float_layout.remove_widget(self.countdown)
        os.system("gphoto2 --capture-image-and-download --filename ~/workspace/capture_images/capture%s_%s.jpg" %(timestamp, self.iteration))
        Clock.schedule_interval(self.check_for_picture, 0.5)

    def check_for_picture(self, *kwargs):
        path="~/workspace/capture_images/capture%s_%s.jpg" %(timestamp, self.iteration)
        path=os.path.expanduser(path)
        self.float_layout.remove_widget(self.countdown)
        if os.path.isfile(path):
            self.show_picture(path)
            Clock.unschedule(self.check_for_picture)

    def show_picture(self, path):
        print "show_picture"
        image = Image(source=path)
        self.float_layout.clear_widgets()
        self.float_layout.add_widget(image) #marc
        if self.iteration == 3:
            self.iteration = 0
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

"""class PendingScreen(Screen):
    def __init__(self, **kwargs):
        super(Pendingscreen, self).__init__(**kwargs) 
        self.assembly()
        print_picture()
        send_mail(mailadress)
        clean_up()
        
    def assembly(self, *kwargs):
       os.system("mogrify -resize 968x648 ~/photobooth/capture_images/*.jpg")
       os.system("montage ~/photobooth/capture_images/*.jpg -tile 2x2 -geometry +10+10 ~/photobooth/temp_montage.jpg")
       os.system("montage ~/photobooth/temp_montage.jpg ~/photobooth/footer.jpg -tile 2x1 -geometry +5+5 ~/photobooth/photobox_%s.jpg" %timestamp)
    
    def send_mail(self, mailadress, *kwargs):
       os.system("mail < ~/photobooth/mail_message %s -s "Photobox" -A "~/photobooth/photobox_%s.jpg" %(mailadress, timestamp)) 
       
    def print_picture(self, *kwargs):
       os.system("lp -d CP9810DW ~/photobooth/photobox_%s.jpg" %timestamp)
       
    def clean_up(self, *kwargs):
       path= "/media/usb0/photobooth_archive/photobox_%s" %daystamp
       assure_path_exists(path)
       os.system("cp ~/photobooth/photobox_%s.jpg /media/usb0/photobooth_archive/photobox_%s/" %(daystamp, daystamp))
       os.system("rm ~/photobooth/capture_images/*.jpg")
       os.system("rm ~/photobooth/photobox*.jpg")
       os.system("rm ~/photobooth/temp*.jpg")   
       
    def assure_path_exists(self, *kwargs):
        dirpath=("/media/usb0/photobooth_archive/photobox_%s" %daystamp)
        dir = os.path.dirname(dirpath)
        if not os.path.exists(dir):
                os.makedirs(dir)"""


class MainLayout(FloatLayout):

    def __init__(self, **kwargs):
        super(MainLayout, self).__init__(**kwargs)
        self.screen_manager.current = "capture"

 
class MyApp(App):
    def build(self):
        return MainLayout()

    
if __name__ == '__main__':
    MyApp().run()