from kivy.app import App
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
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
InputStreamReader = autoclass('java.io.InputStreamReader')
OutputStreamWriter = autoclass('java.io.OutputStreamWriter')

Window.softinput_mode = 'below_target'

currentActivity = PythonActivity.mActivity

REQUEST_OPEN = 1001
REQUEST_SAVE = 1002

# Палитра от заказчика
SALAD = (0.62, 0.83, 0.22, 1)        # салатовые кнопки
EGGPLANT = (0.55, 0.32, 0.62, 1)     # окантовка: баклажан, но светлее
SCARLET = (0.87, 0.14, 0.10, 1)      # алый шрифт на кнопках
TEXT_LIGHT = (0.98, 0.93, 0.85, 1)   # светлый текст на тёмных плашках
PANEL = (0.16, 0.10, 0.06, 0.92)     # тёмно-коричневая плашка результата
ACCENT = (0.98, 0.80, 0.45, 1)       # тёпло-медовый для заголовка и сдвига


class WoodButton(Button):
    # Округлая салатовая кнопка с баклажановой окантовкой
    def __init__(self, **kw):
        super().__init__(**kw)
        self.background_normal = ''
        self.background_down = ''
        self.bold = True
        self.color = SCARLET
        self._radius = dp(24)
        self.bind(pos=self._redraw, size=self._redraw)
        Clock.schedule_once(lambda dt: self._redraw(), 0)

    def _redraw(self, *args):
        if self.width <= 0:
            return
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*SALAD)
            RoundedRectangle(pos=self.pos, size=self.size,
                             radius=[self._radius])
            Color(*EGGPLANT)
            Line(rounded_rectangle=[self.x, self.y, self.width,
                                    self.height, self._radius],
                 width=dp(2.5))


def draw_wood(widget, *args):
    # Коричневые доски с сучками: рисуем программно
    if widget.width <= 0:
        return
    widget.canvas.before.clear()
    with widget.canvas.before:
        Color(0.30, 0.19, 0.10, 1)
        Rectangle(pos=widget.pos, size=widget.size)
        plank_h = dp(105)
        y = widget.y
        i = 0
        while y < widget.y + widget.height:
            h = min(plank_h, widget.y + widget.height - y)
            # Оттенок доски: детерминированный, зависит от номера доски
            r = 0.40 + 0.03 * ((i * 5) % 3)
            g = 0.25 + 0.02 * ((i * 3) % 4)
            b = 0.13 + 0.02 * ((i * 7) % 5)
            Color(r, g, b, 1)
            Rectangle(pos=(widget.x, y + dp(2)),
                      size=(widget.width, h - dp(3)))
            # Шов между досками
            Color(0.14, 0.09, 0.05, 1)
            Rectangle(pos=(widget.x, y), size=(widget.width, dp(2)))
            # Волокна дерева — тонкие тёмные линии
            for j in range(3):
                gy = y + dp(18) + j * dp(32) + ((i * 13 + j * 7) % 14)
                if gy < y + h - dp(6):
                    Color(0.22, 0.13, 0.07, 0.6)
                    Rectangle(pos=(widget.x, gy),
                              size=(widget.width, dp(1.5)))
            # Сучок: тёмный овал со светлым ядром
            kx = widget.x + (((i * 137) % 9) + 1) * widget.width / 10.0
            ky = y + min(h, plank_h) / 2
            Color(0.19, 0.11, 0.06, 1)
            Ellipse(pos=(kx - dp(14), ky - dp(10)), size=(dp(28), dp(20)))
            Color(0.33, 0.21, 0.12, 1)
            Ellipse(pos=(kx - dp(7), ky - dp(5)), size=(dp(14), dp(10)))
            y += plank_h
            i += 1


class ShifrApp(App):
    title = 'Shifr'

    def build(self):
        self.shift_value = 3

        root = BoxLayout(orientation='vertical',
                         padding=dp(14), spacing=dp(10))
        root.bind(pos=draw_wood, size=draw_wood)
        Clock.schedule_once(lambda dt: draw_wood(root), 0)

        # Заголовок
        title = Label(text='Shifr', font_size=dp(32), bold=True,
                      color=ACCENT, size_hint_y=None, height=dp(46))
        root.add_widget(title)

        # Поле текста — тёмная плашка на досках
        self.txt_input = TextInput(hint_text='Введите текст...',
                                   multiline=True, write_tab=False,
                                   font_size=dp(18),
                                   background_color=PANEL,
                                   foreground_color=TEXT_LIGHT,
                                   hint_text_color=(0.6, 0.5, 0.42, 1),
                                   cursor_color=ACCENT)
        root.add_widget(self.txt_input)

        # Блок сдвига
        shift_row = BoxLayout(orientation='horizontal', spacing=dp(10),
                              size_hint_y=None, height=dp(64))
        self.lbl_shift = Label(text='Сдвиг: 3', font_size=dp(26),
                               bold=True, color=ACCENT)
        self.btn_minus = WoodButton(text='−', font_size=dp(30))
        self.btn_minus.size_hint_x = None
        self.btn_minus.width = dp(70)
        self.btn_minus._radius = dp(30)
        self.btn_minus.bind(on_press=self.decrease)
        self.btn_plus = WoodButton(text='+', font_size=dp(30))
        self.btn_plus.size_hint_x = None
        self.btn_plus.width = dp(70)
        self.btn_plus._radius = dp(30)
        self.btn_plus.bind(on_press=self.increase)
