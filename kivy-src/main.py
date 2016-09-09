from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import Screen
from kivy.factory import Factory
from kivy.clock import Clock
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.camera import Camera
from kivy.uix.image import Image

import os
COUNTDOWN = 3


class LoginScreen(Screen):

    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)

    def next(self):
        self.manager.current = "capture"


class CaptureScreen(Screen):

    def __init__(self, **kwargs):
        super(CaptureScreen, self).__init__(**kwargs)
        self.start_button = Factory.StartButton()
        self.start_button.action = self.show_countdown
        self.countdown = Factory.Countdown()
        self.countdown.action = self.take_picture
        self.bind(on_pre_enter=self.show_start)
        cam = Camera(resolution=(640, 480), play=True)
        self.add_widget(cam)

        self.iteration = 0

    def show_start(self, *kwargs):
        self.float_layout.add_widget(self.start_button)

    def show_countdown(self):
        self.float_layout.remove_widget(self.start_button)
        self.float_layout.add_widget(self.countdown)
        self.countdown.start()

    def take_picture(self):
        self.float_layout.remove_widget(self.countdown)
        os.system("gfoto2 ")
        Clock.schedule_interval(self.check_for_picture)

    def check_for_picture(self, *kwargs):
        if os.path.isfile("bild%s.jpg" % self.iteration):
            self.show_picture(self.iteration)
            Clock.unschedule(self.check_for_picture)

    def show_picture(self):
        image = Image(souce="bild%s.jpg" % self.iteration)
        self.float_layout.clear_widgets()
        self.float_layout.add_widget(image)
        if self.iteration == 3:
            self.manager.current = "pending"
            self.iteration = 0
        else:
            self.iteration += 1
            Clock.schedule_once(self.take_picture, 2)


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


class MainLayout(FloatLayout):

    def __init__(self, **kwargs):
        super(MainLayout, self).__init__(**kwargs)
        self.screen_manager.current = "capture"

 
class MyApp(App):
    def build(self):
        return MainLayout()

    
if __name__ == '__main__':
    MyApp().run()