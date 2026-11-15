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


def podelitjsya(text):
    """Открывает системное меню «Поделиться» (только на Android)."""
    from jnius import autoclass
    Intent = autoclass("android.content.Intent")
    PythonActivity = autoclass("org.kivy.android.PythonActivity")
    String = autoclass("java.lang.String")

    intent = Intent()
    intent.setAction(Intent.ACTION_SEND)
    intent.setType("text/plain")
    intent.putExtra(Intent.EXTRA_TEXT, String(text))
    currentActivity = PythonActivity.mActivity
    currentActivity.startActivity(
        Intent.createChooser(intent, String("Куда отправить"))
    )


class ShifrApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.txt_input = TextInput(hint_text="Текст", multiline=True)
        self.txt_shift = TextInput(hint_text="Сдвиг (число)", input_filter='int')
        self.txt_mode = TextInput(hint_text="ш — зашифровать, р — расшифровать")
        self.btn = Button(text="Готово", on_press=self.process)
        self.btn_share = Button(text="Поделиться", on_press=self.share)
        self.lbl_out = Label(text="Результат появится здесь", font_size=28)
        for widget in (self.txt_input, self.txt_shift, self.txt_mode,
                       self.btn, self.btn_share, self.lbl_out):
            layout.add_widget(widget)
        return layout

    def process(self, instance):
        try:
            k = int(self.txt_shift.text)
            self.lbl_out.text = sdvig(self.txt_input.text, k, self.txt_mode.text.strip())
        except ValueError:
            self.lbl_out.text = "Ошибка: сдвиг должен быть числом"

    def share(self, instance):
        # Берём то, что есть: результат шифрования или просто исходный текст
        result = self.lbl_out.text
        text = self.txt_input.text
        if result == "Результат появится здесь":
            payload = text if text.strip() else ""
        elif result.startswith("Ошибка"):
            self.lbl_out.text = "Сначала зашифруйте текст"
            return
        else:
            payload = "Текст: " + text + "\nРезультат: " + result

        if not payload:
            self.lbl_out.text = "Нечего отправлять"
            return

        try:
            podelitjsya(payload)
        except ImportError:
            # На компьютере jnius нет — покажем текст как заглушку
            self.lbl_out.text = "Поделиться работает только на Android"


ShifrApp().run()
