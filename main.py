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
            self.lbl_out.text = sdvig(self.txt_input.text, k, self.txt_mode.text.strip())
        except ValueError:
            self.lbl_out.text = "Ошибка: сдвиг должен быть числом"

ShifrApp().run()
