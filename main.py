import traceback

from kivy.app import App
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle, Line, Ellipse, RoundedRectangle
from kivy.clock import Clock

from jnius import autoclass

try:
    from android import activity as android_activity
except ImportError:
    android_activity = None

Intent = autoclass('android.content.Intent')
String = autoclass('java.lang.String')
PythonActivity = autoclass('org.kivy.android.PythonActivity')
BufferedReader = autoclass('java.io.BufferedReader')
