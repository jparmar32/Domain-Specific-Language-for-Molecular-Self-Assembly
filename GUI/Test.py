from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.scatterlayout import ScatterLayout
from kivy.uix.floatlayout import FloatLayout


class ListScreen(Screen):
    def __init__(self, **kwargs):
        super(ListScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        self.add_widget(layout)
        top_buttons = BoxLayout(orientation='horizontal')
        layout.add_widget(top_buttons)
        bottom_buttons = ScatterLayout()
        layout.add_widget(bottom_buttons)

        top_buttons.add_widget(Button(text='Save'))
        top_buttons.add_widget(Button(text='Dave Doty'))


class ExampleApp(App):
    def build(self):
        root = ListScreen()
        root.add_widget(ListScreen(name='list'))
        return root


ExampleApp().run()
