from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.vkeyboard import VKeyboard
from kivy.clock import Clock
from kivy.properties import NumericProperty, StringProperty, BooleanProperty, ListProperty


class LoginScreen(Widget):
 pass
    
class TakePhoto(Widget):
 pass

 
class MyApp(App):
        def build(self):
            return LoginScreen()

    
if __name__ == '__main__':
    MyApp().run()
