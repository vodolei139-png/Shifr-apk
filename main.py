import traceback

from kivy.app import App
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle, Line, Ellipse, RoundedRectangle
from kivy.clock import Clock
from kivy.core.window import Window
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
Window.clearcolor = (0.30, 0.19, 0.10, 1)

currentActivity = PythonActivity.mActivity

REQUEST_OPEN = 1001
REQUEST_SAVE = 1002

# Палитра от заказчика
SALAD = (0.62, 0.83, 0.22, 1)
EGGPLANT = (0.55, 0.32, 0.62, 1)
SCARLET = (0.87, 0.14, 0.10, 1)
TEXT_LIGHT = (0.98, 0.93, 0.85, 1)
PANEL = (0.16, 0.10, 0.06, 0.92)
ACCENT = (0.98, 0.80, 0.45, 1)


class WoodButton(Button):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.background_normal = ''
        self.background_down = ''
        self.background_color = (0, 0, 0, 0)
        self.bold = True
        self.color = SCARLET
        self._radius = dp(24)
        self.bind(pos=self._redraw, size=self._redraw)
        Clock.schedule_once(lambda dt: self._redraw(), 0)

    def _redraw(self, *args):
        try:
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
        except Exception:
            # Если рисунок не получился — хотя бы цветная кнопка
            self.canvas.before.clear()
            with self.canvas.before:
                Color(*SALAD)
                Rectangle(pos=self.pos, size=self.size)


def draw_wood(widget, *args):
    try:
        _draw_wood_body(widget)
    except Exception:
        # Если доски не нарисовались — просто коричневый фон
        widget.canvas.before.clear()
        with widget.canvas.before:
            Color(0.30, 0.19, 0.10, 1)
            Rectangle(pos=widget.pos, size=widget.size)


def _draw_wood_body(widget):
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
            r = 0.40 + 0.03 * ((i * 5) % 3)
            g = 0.25 + 0.02 * ((i * 3) % 4)
            b = 0.13 + 0.02 * ((i * 7) % 5)
            Color(r, g, b, 1)
            Rectangle(pos=(widget.x, y + dp(2)),
                      size=(widget.width, h - dp(3)))
            Color(0.14, 0.09, 0.05, 1)
            Rectangle(pos=(widget.x, y), size=(widget.width, dp(2)))
            for j in range(3):
                gy = y + dp(18) + j * dp(32) + ((i * 13 + j * 7) % 14)
                if gy < y + h - dp(6):
                    Color(0.22, 0.13, 0.07, 0.6)
                    Rectangle(pos=(widget.x, gy),
                              size=(widget.width, dp(1.5)))
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
        try:
            return self.build_main()
        except Exception:
            return self.error_screen()

    # Экран ошибки вместо молчаливого вылета
    def error_screen(self):
        err = traceback.format_exc()
        layout = BoxLayout(orientation='vertical', padding=dp(10))
        scroll = ScrollView()
        lbl = Label(text='Ошибка запуска — сфотографируйте этот текст:\n\n' + err,
                    font_size=dp(13), color=(1, 0.55, 0.35, 1),
                    halign='left', valign='top',
                    size_hint=(1, None))
        def _fit(*args):
            lbl.text_size = (lbl.width, None)
            lbl.height = lbl.texture_size[1]
        lbl.bind(width=_fit, texture_size=_fit)
        scroll.add_widget(lbl)
        layout.add_widget(scroll)
        return layout

    def build_main(self):
        self.shift_value = 3

        root = BoxLayout(orientation='vertical',
                         padding=dp(14), spacing=dp(10))
        root.bind(pos=draw_wood, size=draw_wood)
        Clock.schedule_once(lambda dt: draw_wood(root), 0)

        title = Label(text='Shifr', font_size=dp(32), bold=True,
                      color=ACCENT, size_hint_y=None, height=dp(46))
        root.add_widget(title)

        self.txt_input = TextInput(hint_text='Введите текст...',
                                   multiline=True, write_tab=False,
                                   font_size=dp(18),
                                   background_color=PANEL,
                                   foreground_color=TEXT_LIGHT,
                                   hint_text_color=(0.6, 0.5, 0.42, 1),
                                   cursor_color=ACCENT)
        root.add_widget(self.txt_input)

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
        shift_row.add_widget(self.lbl_shift)
        shift_row.add_widget(self.btn_minus)
        shift_row.add_widget(self.btn_plus)
        root.add_widget(shift_row)

        self.btn_enc = WoodButton(text='Зашифровать', font_size=dp(22),
                                  on_press=lambda x: self.process('ш'))
        self.btn_dec = WoodButton(text='Расшифровать', font_size=dp(22),
                                  on_press=lambda x: self.process('р'))
        root.add_widget(self.btn_enc)
        root.add_widget(self.btn_dec)

        file_row = BoxLayout(orientation='horizontal', spacing=dp(10),
                             size_hint_y=None, height=dp(54))
        self.btn_open = WoodButton(text='Открыть файл', font_size=dp(17),
                                   on_press=self.open_file)
        self.btn_save = WoodButton(text='Сохранить файл', font_size=dp(17),
                                   on_press=self.save_file)
        file_row.add_widget(self.btn_open)
        file_row.add_widget(self.btn_save)
        root.add_widget(file_row)

        self.btn_share = WoodButton(text='Поделиться', font_size=dp(20),
                                    size_hint_y=None, height=dp(54),
                                    on_press=self.share)
        root.add_widget(self.btn_share)

        result_box = BoxLayout(size_hint_y=1, padding=dp(8))
        self.lbl_out = Label(text='Результат появится здесь',
                             font_size=dp(22), color=TEXT_LIGHT)
        result_box.add_widget(self.lbl_out)

        def redraw_panel(instance, *a):
            try:
                instance.canvas.before.clear()
                with instance.canvas.before:
                    Color(*PANEL)
                    RoundedRectangle(pos=instance.pos, size=instance.size,
                                     radius=[dp(16)])
            except Exception:
                pass
        result_box.bind(pos=redraw_panel, size=redraw_panel)
        Clock.schedule_once(lambda dt: redraw_panel(result_box), 0)
        root.add_widget(result_box)

        return root

    def on_start(self):
        if android_activity is not None:
            android_activity.bind(on_activity_result=self.on_activity_result)

    def decrease(self, instance):
        if self.shift_value > 1:
            self.shift_value -= 1
        self.lbl_shift.text = 'Сдвиг: ' + str(self.shift_value)
        self.recount()

    def increase(self, instance):
        if self.shift_value < 33:
            self.shift_value += 1
        self.lbl_shift.text = 'Сдвиг: ' + str(self.shift_value)
        self.recount()

    def recount(self):
        if self.txt_input.text:
            self.lbl_out.text = sdvig(self.txt_input.text, self.shift_value)

    def process(self, mode):
        text = self.txt_input.text
        if not text:
            self.lbl_out.text = 'Введите текст'
            return
        shift = self.shift_value if mode == 'ш' else -self.shift_value
        self.lbl_out.text = sdvig(text, shift)

    def share(self, instance):
        text = self.lbl_out.text
        if text == 'Результат появится здесь':
            self.lbl_out.text = 'Сначала получите результат'
            return
        podelitsya(text)

    def open_file(self, instance):
        if android_activity is None:
            self.lbl_out.text = 'Файлы работают только на Android'
            return
        intent = Intent()
        intent.setAction(Intent.ACTION_OPEN_DOCUMENT)
        intent.addCategory(Intent.CATEGORY_OPENABLE)
        intent.setType('*/*')
        currentActivity.startActivityForResult(intent, REQUEST_OPEN)

    def on_resume(self):
        Clock.schedule_once(lambda dt: Window.canvas.ask_update(), 0.3)

    def save_file(self, instance):
        if android_activity is None:
            self.lbl_out.text = 'Файлы работают только на Android'
            return
        text = self.lbl_out.text
        if text == 'Результат появится здесь':
            self.lbl_out.text = 'Сначала получите результат'
            return
        intent = Intent()
        intent.setAction(Intent.ACTION_CREATE_DOCUMENT)
        intent.addCategory(Intent.CATEGORY_OPENABLE)
        intent.setType('text/plain')
        intent.putExtra(Intent.EXTRA_TITLE, String('shifr_result.txt'))
        currentActivity.startActivityForResult(intent, REQUEST_SAVE)

        def on_activity_result(self, request_code, result_code, data):
        if data is None:
            return
        uri = data.getData()
        if request_code == REQUEST_OPEN and result_code == -1:
            Clock.schedule_once(lambda dt: self.load_text_from_uri(uri), 0)
        elif request_code == REQUEST_SAVE and result_code == -1:
            Clock.schedule_once(lambda dt: self.save_text_to_uri(uri), 0)

    def load_text_from_uri(self, uri):
        try:
            stream = currentActivity.getContentResolver().openInputStream(uri)
            reader = BufferedReader(InputStreamReader(stream, 'UTF-8'))
            lines = []
            while True:
                line = reader.readLine()
                if line is None:
                    break
                lines.append(line)
            reader.close()
            self.txt_input.text = '\n'.join(lines)
            self.lbl_out.text = 'Файл загружен'
        except Exception as e:
            self.lbl_out.text = 'Ошибка чтения: ' + str(e)

    def save_text_to_uri(self, uri):
        try:
            stream = currentActivity.getContentResolver().openOutputStream(uri)
            writer = OutputStreamWriter(stream, 'UTF-8')
            writer.write(self.lbl_out.text)
            writer.flush()
            writer.close()
            self.lbl_out.text = 'Файл сохранён'
        except Exception as e:
            self.lbl_out.text = 'Ошибка сохранения: ' + str(e)
            
def sdvig(text, shift):
    rus_lower = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
    rus_upper = rus_lower.upper()
    latin_lower = 'abcdefghijklmnopqrstuvwxyz'
    latin_upper = latin_lower.upper()

    result = []
    for ch in text:
        for alphabet in (rus_lower, rus_upper, latin_lower, latin_upper):
            if ch in alphabet:
                size = len(rus_lower) if alphabet in (rus_lower, rus_upper) else len(latin_lower)
                idx = (alphabet.index(ch) + shift) % size
                result.append(alphabet[idx])
                break
        else:
            result.append(ch)
    return ''.join(result)


def podelitsya(text):
    intent = Intent()
    intent.setAction(Intent.ACTION_SEND)
    intent.setType('text/plain')
    intent.putExtra(Intent.EXTRA_TEXT, String(text))
    currentActivity.startActivity(
        Intent.createChooser(intent, String('Куда отправить')))

if __name__ == '__main__':
    ShifrApp().run()
