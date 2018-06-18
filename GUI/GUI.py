import kivy
from kivy.app import App
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.button import Button
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.spinner import Spinner
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scatterlayout import ScatterLayout


class TabbedLayout(TabbedPanel):
    def onRelease(self):
        self.ids.canvasLabel.text = self.ids.objectCreator.text


class GUI(App):
    def build(self):
        return TabbedLayout()


if __name__ == '__main__':
    gui = GUI()
    gui.run()
