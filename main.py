from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label

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

# Клавиатура не должна перекрывать поле, по которому тапнули
Window.softinput_mode = 'below_target'

currentActivity = PythonActivity.mActivity

REQUEST_OPEN = 1001
REQUEST_SAVE = 1002


# Шифр Цезаря: русские и латинские буквы, регистр сохраняется,
# пробелы, цифры и знаки не трогаем
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


# Поделиться через системное меню
def podelitsya(text):
    intent = Intent()
    intent.setAction(Intent.ACTION_SEND)
    intent.setType('text/plain')
    intent.putExtra(Intent.EXTRA_TEXT, String(text))
    currentActivity.startActivity(
        Intent.createChooser(intent, String('Куда отправить')))


class ShifrApp(App):
    def build(self):
        self.shift_value = 3  # стартовый сдвиг

        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.txt_input = TextInput(hint_text='Текст', multiline=True,
                                   write_tab=False)
        self.lbl_shift = Label(text='Сдвиг: 3', font_size=24)
        row = BoxLayout(orientation='horizontal', spacing=10)
        self.btn_minus = Button(text='−', font_size=32,
                                on_press=self.decrease)
        self.btn_plus = Button(text='+', font_size=32,
                               on_press=self.increase)
        row.add_widget(self.btn_minus)
        row.add_widget(self.btn_plus)
        self.btn_enc = Button(text='Зашифровать (ш)',
                              on_press=lambda instance: self.process('ш'))
        self.btn_dec = Button(text='Расшифровать (р)',
                              on_press=lambda instance: self.process('р'))
        self.btn_share = Button(text='Поделиться', on_press=self.share)
        self.btn_open = Button(text='Открыть файл', on_press=self.open_file)
        self.btn_save = Button(text='Сохранить файл', on_press=self.save_file)
        self.lbl_out = Label(text='Результат появится здесь', font_size=28)

        for widget in (self.txt_input, self.lbl_shift, row,
                       self.btn_enc, self.btn_dec,
                       self.btn_share, self.btn_open,
                       self.btn_save, self.lbl_out):
            layout.add_widget(widget)
        return layout

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

    # Пересчёт на лету, если текст уже введён
    def recount(self):
        if self.txt_input.text:
            self.lbl_out.text = sdvig(self.txt_input.text, self.shift_value)

    # Обработка текста: шифрование или расшифрование
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

    # Открытие файла через системный выбор
    def open_file(self, instance):
        if android_activity is None:
            self.lbl_out.text = 'Файлы работают только на Android'
            return
        intent = Intent()
        intent.setAction(Intent.ACTION_OPEN_DOCUMENT)
        intent.addCategory(Intent.CATEGORY_OPENABLE)
        intent.setType('*/*')
        currentActivity.startActivityForResult(intent, REQUEST_OPEN)

    # Сохранение результата через системный диалог
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

    # Приём результата системных диалогов
    def on_activity_result(self, request_code, result_code, data):
        if data is None:
            return
        if request_code == REQUEST_OPEN and result_code == -1:
            self.load_text_from_uri(data.getData())
        elif request_code == REQUEST_SAVE and result_code == -1:
            self.save_text_to_uri(data.getData())

    # Чтение файла: UTF-8, чтобы русский текст не ломался
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

    # Запись результата в файл: тоже UTF-8
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


if __name__ == '__main__':
    ShifrApp().run()
