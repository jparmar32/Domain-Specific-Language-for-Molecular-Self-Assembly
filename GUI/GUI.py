import kivy
from kivy.app import App
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.button import Button
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.spinner import Spinner
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scatterlayout import ScatterLayout
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.behaviors import DragBehavior


class tile_template(DragBehavior, Label):
    pass


class tile_set_template():
    def __init__(self, name):
        self.name = name


class root_module():
    def __init__(self, name):
        self.name = name


class module(DragBehavior, Label):
    pass


class port(DragBehavior, Label):
    pass


class initiator_port(DragBehavior, Label):
    pass


class TabbedLayout(TabbedPanel):

    widget_list = []

    def createObject(self):

        if self.ids.objectCreator.text == 'Tile Template':
            box = BoxLayout(orientation='vertical')
            txt = TextInput(multiline=False, text='Name')
            box.add_widget(txt)
            bttn = Button(text="Create Tile Template")
            box.add_widget(bttn)
            popup = Popup(title='Create Tile Template', content=box, size_hint=(.2, .3), auto_dismiss=False)
            new_tile = tile_template()
            new_tile.text = 'tile template'

            def popupFunc(self):
                popup.dismiss()
                new_tile.text = txt.text

            bttn.bind(on_press=popupFunc)

            popup.open()
            self.ids.scatterID.add_widget(new_tile)

            self.widget_list.append(new_tile)

            #self.ids.canvasLabel.text = 'Tile Template'

        if self.ids.objectCreator.text == 'Tile Set Template':

            box = BoxLayout(orientation='vertical')
            txt = TextInput(multiline=False, text='Name')
            box.add_widget(txt)
            bttn = Button(text="Create Tile Set Template")
            box.add_widget(bttn)
            popup = Popup(title='Create Tile Set Template', content=box, size_hint=(.2, .3), auto_dismiss=False)
            new_tile_set_template = tile_set_template("")

            def popupFunc(self):
                popup.dismiss()
                new_tile_set_template.name = txt.text

            bttn.bind(on_press=popupFunc)

            popup.open()

        if self.ids.objectCreator.text == 'Root Module':

            new_root_module = root_module("rootMod")

        if self.ids.objectCreator.text == 'Module':

            box = BoxLayout(orientation='vertical')
            txt = TextInput(multiline=False, text='Name')
            box.add_widget(txt)
            bttn = Button(text="Create Module")
            box.add_widget(bttn)
            popup = Popup(title='Create Module', content=box, size_hint=(.2, .3))
            new_module = module()
            new_module.text = 'module'

            def popupFunc(self):
                popup.dismiss()
                new_module.text = txt.text

            bttn.bind(on_press=popupFunc)
            popup.open()
            self.ids.scatterID.add_widget(new_module)

            self.widget_list.append(new_module)

        if self.ids.objectCreator.text == 'Port':

            box = BoxLayout(orientation='vertical')
            txt = TextInput(multiline=False, text='Name')
            box.add_widget(txt)
            box.add_widget(TextInput(multiline=False, text='Direction'))
            bttn = Button(text="Create Port")
            box.add_widget(bttn)
            popup = Popup(title='Create Port', content=box, size_hint=(.2, .3), auto_dismiss=False)
            new_port = port()
            new_port.text = 'port'

            def popupFunc(self):
                popup.dismiss()
                new_port.text = txt.text

            bttn.bind(on_press=popupFunc)
            popup.open()
            self.ids.scatterID.add_widget(new_port)

            self.widget_list.append(new_port)

        if self.ids.objectCreator.text == 'Initiator Port':

            box = BoxLayout(orientation='vertical')
            txt = TextInput(multiline=False, text='Name')
            box.add_widget(txt)
            box.add_widget(TextInput(multiline=False, text='Direction'))
            box.add_widget(TextInput(multiline=False, text='Strength'))
            bttn = Button(text="Create Initiator Port")
            box.add_widget(bttn)
            popup = Popup(title='Create Initiator Port', content=box, size_hint=(.25, .35), auto_dismiss=False)
            new_initiator_port = initiator_port()
            new_initiator_port.text = 'initiator_port'

            def popupFunc(self):
                popup.dismiss()
                new_initiator_port.text = txt.text

            bttn.bind(on_press=popupFunc)
            popup.open()
            self.ids.scatterID.add_widget(new_initiator_port)

            self.widget_list.append(new_initiator_port)

    def deleteObject(self):
        last_element = len(self.widget_list) - 1
        self.ids.scatterID.remove_widget(self.widget_list[last_element])
        self.widget_list.pop()

    def executeFunction(self):
        if self.ids.objectCreator.text == 'Create Join':
            pass


class GUI(App):
    StringProperty Select1 = ""

    def build(self):
        return TabbedLayout()


if __name__ == '__main__':
    gui = GUI()
    gui.run()
