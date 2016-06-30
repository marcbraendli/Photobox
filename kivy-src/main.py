from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget


class LoginScreen(BoxLayout):
    pass


class TakePhoto(Widget):
    pass

 
class MyApp(App):
    def build(self):
        return LoginScreen()

    
if __name__ == '__main__':
    MyApp().run()
