from kivy.app import App
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle

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

# Тёмный фон всего окна
Window.clearcolor = (0.09, 0.10, 0.13, 1)
Window.softinput_mode = 'below_target'

currentActivity = PythonActivity.mActivity

REQUEST_OPEN = 1001
REQUEST_SAVE = 1002

# Палитра
BG_CARD = (0.14, 0.16, 0.20, 1)
GREEN = (0.22, 0.62, 0.35, 1)
BLUE = (0.23, 0.47, 0.82, 1)
GRAY = (0.30, 0.33, 0.38, 1)
TEXT_LIGHT = (0.92, 0.94, 0.96, 1)
ACCENT = (0.98, 0.72, 0.25, 1)


class ShifrApp(App):
    title = 'Shifr'

    def build(self):
        self.shift_value = 3

        root = BoxLayout(orientation='vertical',
                         padding=dp(14), spacing=dp(10))

        # Заголовок приложения
        title = Label(text='🔐 Shifr', font_size=dp(30),
                      color=ACCENT, size_hint_y=None, height=dp(44))
        root.add_widget(title)

        # Поле текста
        self.txt_input = TextInput(hint_text='Введите текст...',
                                   multiline=True, write_tab=False,
                                   font_size=dp(18),
                                   background_color=BG_CARD,
                                   foreground_color=TEXT_LIGHT,
                                   hint_text_color=(0.55, 0.58, 0.62, 1),
                                   cursor_color=ACCENT)
        root.add_widget(self.txt_input)

        # Блок сдвига: подпись и кнопки в один ряд
        shift_row = BoxLayout(orientation='horizontal',
                              spacing=dp(10),
                              size_hint_y=None, height=dp(60))
        self.lbl_shift = Label(text='Сдвиг: 3', font_size=dp(24),
                               color=ACCENT)
        self.btn_minus = RoundButton(text='−', font_size=dp(30),
                                     color=GRAY, on_press=self.decrease)
        self.btn_plus = RoundButton(text='+', font_size=dp(30),
                                    color=GRAY, on_press=self.increase)
        shift_row.add_widget(self.lbl_shift)
        shift_row.add_widget(self.btn_minus)
        shift_row.add_widget(self.btn_plus)
        root.add_widget(shift_row)

        # Главные действия — цветные и на всю ширину
        self.btn_enc = BigButton(text='Зашифровать', color=GREEN,
                                 on_press=lambda x: self.process('ш'))
        self.btn_dec = BigButton(text='Расшифровать', color=BLUE,
                                 on_press=lambda x: self.process('р'))
        root.add_widget(self.btn_enc)
        root.add_widget(self.btn_dec)

        # Файловые действия — два в ряд
        file_row = BoxLayout(orientation='horizontal', spacing=dp(10),
                             size_hint_y=None, height=dp(52))
        self.btn_open = BigButton(text='📂 Открыть', color=GRAY,
                                  on_press=self.open_file)
        self.btn_save = BigButton(text='💾 Сохранить', color=GRAY,
                                  on_press=self.save_file)
        file_row.add_widget(self.btn_open)
        file_row.add_widget(self.btn_save)
        root.add_widget(file_row)

        self.btn_share = BigButton(text='Поделиться', color=GRAY,
                                   size_hint_y=None, height=dp(52),
                                   on_press=self.share)
        root.add_widget(self.btn_share)

        # Результат — на «карточке», заметно крупнее
        result_box = BoxLayout(size_hint_y=1, padding=dp(6))
        with result_box.canvas.before:
            Color(*BG_CARD)
            self.result_bg = Rectangle(pos=result_box.pos,
                                       size=result_box.size)
        self.lbl_out = Label(text='Результат появится здесь',
                             font_size=dp(22), color=TEXT_LIGHT)
        result_box.add_widget(self.lbl_out)
        result_box.bind(pos=self._update_bg, size=self._update_bg)
        root.add_widget(result_box)

        return root

    def _update_bg(self, instance, value):
        self.result_bg.pos = instance.pos
        self.result_bg.size = instance.size

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
        if request_code == REQUEST_OPEN and result_code == -1:
            self.load_text_from_uri(data.getData())
        elif request_code == REQUEST_SAVE and result_code == -1:
            self.save_text_to_uri(data.getData())

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


# Кнопка с закруглениями и мягким нажатием
class RoundButton(Button):
    pass


class BigButton(Button):
    pass


def style_buttons():
    for cls in (RoundButton, BigButton):
        cls.background_normal = ''
        cls.background_down = ''
        cls.background_color = GRAY
        cls.color = TEXT_LIGHT
        cls.bold = True


style_buttons()


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
