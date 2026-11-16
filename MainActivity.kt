package org.vodolei.shifr

import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {

    // Коды запросов для файловых диалогов
    private val REQUEST_OPEN_FILE = 1001
    private val REQUEST_SAVE_FILE = 1002

    private lateinit var editTextText: EditText
    private lateinit var editTextShift: EditText
    private lateinit var editTextMode: EditText
    private lateinit var textViewResult: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        editTextText = findViewById(R.id.editTextText)
        editTextShift = findViewById(R.id.editTextShift)
        editTextMode = findViewById(R.id.editTextMode)
        textViewResult = findViewById(R.id.textViewResult)

        findViewById<Button>(R.id.buttonDone).setOnClickListener { processText() }
        findViewById<Button>(R.id.buttonShare).setOnClickListener { shareResult() }
        findViewById<Button>(R.id.buttonOpenFile).setOnClickListener { openFile() }
        findViewById<Button>(R.id.buttonSaveFile).setOnClickListener { saveFile() }
    }

    // Обработка текста: шифрование или расшифрование
    private fun processText() {
        val text = editTextText.text.toString()
        if (text.isEmpty()) {
            Toast.makeText(this, "Введите текст", Toast.LENGTH_SHORT).show()
            return
        }
        val shift = editTextShift.text.toString().toIntOrNull()
        if (shift == null) {
            Toast.makeText(this, "Введите число-сдвиг", Toast.LENGTH_SHORT).show()
            return
        }
        val mode = editTextMode.text.toString().trim().lowercase()
        val realShift = when (mode) {
            "ш" -> shift          // зашифровать: сдвиг вперёд
            "р" -> -shift         // расшифровать: сдвиг назад
            else -> {
                Toast.makeText(this, "Введите ш или р", Toast.LENGTH_SHORT).show()
                return
            }
        }
        textViewResult.text = caesar(text, realShift)
    }

    // Шифр Цезаря: русские и латинские буквы, регистр сохраняется,
    // остальные символы (пробелы, цифры, знаки) не трогаем
    private fun caesar(text: String, shift: Int): String {
        val rusLower = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
        val rusUpper = rusLower.uppercase()
        val rusSize = rusLower.length
        val latinLower = "abcdefghijklmnopqrstuvwxyz"
        val latinUpper = latinLower.uppercase()
        val latinSize = latinLower.length

        val sb = StringBuilder()
        for (ch in text) {
            when {
                rusLower.contains(ch) -> {
                    val idx = (rusLower.indexOf(ch) + shift % rusSize + rusSize) % rusSize
                    sb.append(rusLower[idx])
                }
                rusUpper.contains(ch) -> {
                    val idx = (rusUpper.indexOf(ch) + shift % rusSize + rusSize) % rusSize
                    sb.append(rusUpper[idx])
                }
                latinLower.contains(ch) -> {
                    val idx = (latinLower.indexOf(ch) + shift % latinSize + latinSize) % latinSize
                    sb.append(latinLower[idx])
                }
                latinUpper.contains(ch) -> {
                    val idx = (latinUpper.indexOf(ch) + shift % latinSize + latinSize) % latinSize
                    sb.append(latinUpper[idx])
                }
                else -> sb.append(ch)
            }
        }
        return sb.toString()
    }

    // Системное меню «Поделиться» с результатом
    private fun shareResult() {
        val text = textViewResult.text.toString()
        if (text.isEmpty() || text == "Результат появится здесь") {
            Toast.makeText(this, "Сначала получите результат", Toast.LENGTH_SHORT).show()
            return
        }
        val intent = Intent(Intent.ACTION_SEND).apply {
            type = "text/plain"
            putExtra(Intent.EXTRA_TEXT, text)
        }
        startActivity(Intent.createChooser(intent, "Отправка сообщения"))
    }

    // Открытие файла через системный выбор
    private fun openFile() {
        val intent = Intent(Intent.ACTION_OPEN_DOCUMENT).apply {
            addCategory(Intent.CATEGORY_OPENABLE)
            type = "*/*"  // любой файл; текст читается как UTF-8
        }
        startActivityForResult(intent, REQUEST_OPEN_FILE)
    }

    // Сохранение результата как .txt через системный диалог
    private fun saveFile() {
        val text = textViewResult.text.toString()
        if (text.isEmpty() || text == "Результат появится здесь") {
            Toast.makeText(this, "Сначала получите результат", Toast.LENGTH_SHORT).show()
            return
        }
        val intent = Intent(Intent.ACTION_CREATE_DOCUMENT).apply {
            addCategory(Intent.CATEGORY_OPENABLE)
            type = "text/plain"
            putExtra(Intent.EXTRA_TITLE, "shifr_result.txt")
        }
        startActivityForResult(intent, REQUEST_SAVE_FILE)
    }

    // Приём результата файловых диалогов
    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (resultCode != RESULT_OK || data == null) return
        val uri = data.data ?: return
        when (requestCode) {
            REQUEST_OPEN_FILE -> loadTextFromFile(uri)
            REQUEST_SAVE_FILE -> saveTextToFile(uri)
        }
    }

    // Чтение файла: кодировка UTF-8, чтобы русский текст не ломался
    private fun loadTextFromFile(uri: Uri) {
        try {
            contentResolver.openInputStream(uri)?.use { stream ->
                val text = stream.readBytes().toString(Charsets.UTF_8)
                editTextText.setText(text)
                Toast.makeText(this, "Файл загружен", Toast.LENGTH_SHORT).show()
            }
        } catch (e: Exception) {
            Toast.makeText(this, "Ошибка чтения файла: ${e.message}", Toast.LENGTH_LONG).show()
        }
    }

    // Запись результата в файл: тоже UTF-8
    private fun saveTextToFile(uri: Uri) {
        val text = textViewResult.text.toString()
        try {
            contentResolver.openOutputStream(uri)?.use { stream ->
                stream.write(text.toByteArray(Charsets.UTF_8))
                Toast.makeText(this, "Файл сохранён", Toast.LENGTH_SHORT).show()
            }
        } catch (e: Exception) {
            Toast.makeText(this, "Ошибка сохранения: ${e.message}", Toast.LENGTH_LONG).show()
        }
    }
}
