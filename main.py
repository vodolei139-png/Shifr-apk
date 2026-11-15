from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label

def sdvig(text, k, napravlenie):
    alfavit = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
    resultat = ""
    for bukva in text:
        if bukva.isalpha() and bukva.lower() in alfavit:
            nomer = alfavit.index(bukva.lower())
            noviy = alfavit[(nomer + k) % 33] if napravlenie == "ш" else alfavit[(nomer - k) % 33]
            resultat += noviy.upper() if bukva.isupper() else noviy
        else:
            resultat += bukva
    return resultat

class ShifrApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.txt_input = TextInput(hint_text="Текст", multiline=True)
        self.txt_shift = TextInput(hint_text="Сдвиг (число)", input_filter='int')
        self.txt_mode = TextInput(hint_text="ш — зашифровать, р — расшифровать")
        self.btn = Button(text="Готово", on_press=self.process)
        self.lbl_out = Label(text="Результат появится здесь", font_size=32)
        for widget in (self.txt_input, self.txt_shift, self.txt_mode, self.btn, self.lbl_out):
            layout.add_widget(widget)
        return layout

    def process(self, instance):
        try:
            k = int(self.txt_shift.text)
            import os

class ShifrApp(App):
    def build(self):
        # ... существующие виджеты ...
        row = BoxLayout()
        self.btn_save = Button(text="Сохранить", on_press=self.save)
        self.btn_load = Button(text="Загрузить", on_press=self.load)
        row.add_widget(self.btn_load)
        row.add_widget(self.btn_save)
        layout.add_widget(row)   # добавить до lbl_out

    def get_path(self, name):
        # собственная папка приложения на Android (или на компьютере)
        return os.path.join(self.user_data_dir, name)

    def save(self, instance):
        if not self.txt_input.text.strip():
            self.lbl_out.text = "Нечего сохранять"
            return
        with open(self.get_path("shifr_save.txt"), "w", encoding="utf-8") as f:
            f.write(self.txt_input.text + "\n---\n" + self.lbl_out.text)
        self.lbl_out.text = "Сохранено в shifr_save.txt"

    def load(self, instance):
        try:
            with open(self.get_path("shifr_save.txt"), "r", encoding="utf-8") as f:
                text, result = f.read().split("\n---\n", 1)
        except FileNotFoundError:
            self.lbl_out.text = "Сохранений пока нет"
            return
        except ValueError:
            text, result = f.read(), ""
        self.txt_input.text = text
        self.lbl_out.text = result or "Загружено"

            self.lbl_out.text = sdvig(self.txt_input.text, k, self.txt_mode.text.strip())
        except ValueError:
            self.lbl_out.text = "Ошибка: сдвиг должен быть числом"

ShifrApp().run()
