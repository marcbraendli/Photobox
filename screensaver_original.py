import kivy
kivy.require('1.4.1')

import random, os
from kivy.app import App
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.config import Config


class PhotoScreensaver(App):

    def __init__(self):
        App.__init__(self)
        self.photos = []
        find_all_photos(self)

    def build(self):
        keyb = Window.request_keyboard(self.stop, self)
        keyb.bind(on_key_down = self.key_pressed)
        self.image = Image()
        self.change_image()
        Clock.schedule_interval(self.change_image, 10)
        return self.image

    def key_pressed(self, keyboard, keycode, text, modifiers):
        self.stop()

    def change_image(self, whatever = None):
        self.image.source = random.choice(self.photos)

    def add_photos(self, nothing, dirname, files):
        for file in files:
            if file.endswith('.jpg') or file.endswith('.JPG'):
                self.photos.append(os.path.join(dirname, file))

def find_all_photos(app):
    os.path.walk('/media/usb0/photobooth_archive/photobox_11092016/', app.add_photos, None)

if __name__ == '__main__':
    Config.set('graphics', 'fullscreen', '1')
    Config.set('graphics', 'size', '0x0')
    PhotoScreensaver().run()