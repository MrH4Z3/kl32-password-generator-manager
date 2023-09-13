import string
import random
import sys
import sqlite3
import hashlib
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QLineEdit, QTabWidget, QComboBox, QListWidget, QInputDialog, QCheckBox

from PyQt5.QtCore import Qt

class PasswordGeneratorApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("K!32 Parola Yöneticisi")
        self.setGeometry(100, 100, 400, 300)

        self.init_main_app()

    def init_main_app(self):
        main_layout = QVBoxLayout()

        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(self.create_password_tab(), "Parola Oluştur")
        self.tab_widget.addTab(self.create_saved_passwords_tab(), "Kayıtlı Parolalar")

        main_layout.addWidget(self.tab_widget)

        self.setLayout(main_layout)

        self.init_database()
        self.load_saved_passwords()

    def init_database(self):
        # SQLite veritabanını başlatma
        self.conn = sqlite3.connect("passwords.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS passwords (id INTEGER PRIMARY KEY, type TEXT, identifier TEXT, password TEXT)")
        self.conn.commit()

    def load_saved_passwords(self):
        self.saved_passwords_list.clear()

        self.cursor.execute("SELECT * FROM passwords WHERE type = 'Kullanıcı Adı'")
        usernames = self.cursor.fetchall()
        self.saved_passwords_list.addItem("Kullanıcı Adları:")
        for username in usernames:
            self.saved_passwords_list.addItem(f"{username[2]} - Parola: {username[3]}")

        self.saved_passwords_list.addItem("")  # Boşluk eklemek için

        self.cursor.execute("SELECT * FROM passwords WHERE type = 'E-Posta'")
        emails = self.cursor.fetchall()
        self.saved_passwords_list.addItem("E-posta Adresleri:")
        for email in emails:
            self.saved_passwords_list.addItem(f"{email[2]} - Parola: {email[3]}")

    def create_password_tab(self):
        # Parola oluşturma sekmesini oluşturma
        tab_layout = QVBoxLayout()

        self.title_label = QLabel("Güçlü Parola Oluşturucu")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        tab_layout.addWidget(self.title_label)

        self.input_label = QLabel("Seçim yapın:")
        tab_layout.addWidget(self.input_label)

        self.input_combobox = QComboBox(self)
        self.input_combobox.addItem("Kullanıcı Adı")
        self.input_combobox.addItem("E-Posta")
        tab_layout.addWidget(self.input_combobox)

        self.username_entry = QLineEdit(self)
        tab_layout.addWidget(self.username_entry)

        options_layout = QVBoxLayout()

        self.use_letters_check = QCheckBox("Harf Kullan")
        options_layout.addWidget(self.use_letters_check)

        self.use_numbers_check = QCheckBox("Rakam Kullan")
        options_layout.addWidget(self.use_numbers_check)

        self.use_symbols_check = QCheckBox("Sembol Kullan")
        options_layout.addWidget(self.use_symbols_check)

        tab_layout.addLayout(options_layout)

        self.generate_button = QPushButton("Parola Oluştur", self)
        self.generate_button.clicked.connect(self.generate_password)
        tab_layout.addWidget(self.generate_button)

        self.result_label = QLabel("")
        self.result_label.setAlignment(Qt.AlignCenter)
        tab_layout.addWidget(self.result_label)

        password_tab = QWidget()
        password_tab.setLayout(tab_layout)
        return password_tab

    def create_saved_passwords_tab(self):
        tab_layout = QVBoxLayout()

        self.saved_passwords_label = QLabel("Kayıtlı Parolalar")
        self.saved_passwords_label.setAlignment(Qt.AlignCenter)
        self.saved_passwords_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        tab_layout.addWidget(self.saved_passwords_label)

        self.saved_passwords_list = QListWidget()
        tab_layout.addWidget(self.saved_passwords_list)

        self.saved_passwords_list.addItem("----- Kullanıcı Adları -----")
        self.saved_passwords_list.addItem("")  # Boşluk eklemek için

        self.saved_passwords_list.addItem("----- E-posta Adresleri -----")
        self.saved_passwords_list.addItem("")  # Boşluk eklemek için

        self.copy_password_button = QPushButton("Parolayı Kopyala", self)
        self.copy_password_button.clicked.connect(self.copy_selected_password)
        tab_layout.addWidget(self.copy_password_button)

        self.delete_password_button = QPushButton("Parolayı Sil", self)
        self.delete_password_button.clicked.connect(self.delete_selected_password)
        tab_layout.addWidget(self.delete_password_button)

        saved_passwords_tab = QWidget()
        saved_passwords_tab.setLayout(tab_layout)
        return saved_passwords_tab


    def copy_selected_password(self):
        # Seçilen parolayı kopyalama
        selected_item = self.saved_passwords_list.currentItem()
        if selected_item:
            password_text = selected_item.text().split(" - Parola: ")[1]
            clipboard = QApplication.clipboard()
            clipboard.setText(password_text)

    def delete_selected_password(self):
        selected_item = self.saved_passwords_list.currentItem()
        if selected_item:
            password_text = selected_item.text()
            username_or_email = password_text.split("- Parola:")[0].strip()

            try:
                self.cursor.execute("SELECT id FROM passwords WHERE identifier = ?", (username_or_email,))
                password_id = self.cursor.fetchone()
                if password_id:
                    password_id = password_id[0]  # İlk sütundaki ID'yi al
                    self.cursor.execute("DELETE FROM passwords WHERE id = ?", (password_id,))
                    self.conn.commit()
                    self.load_saved_passwords()
                else:
                    print("Kullanıcı adına uygun şifre bulunamadı")
            except Exception as e:
                print("Parola silinirken bir hata oluştu:", e)


    def generate_password(self):
        # Parola oluşturma işlemini gerçekleştirme
        use_letters = self.use_letters_check.isChecked()
        use_numbers = self.use_numbers_check.isChecked()
        use_symbols = self.use_symbols_check.isChecked()

        characters = ""
        if use_letters:
            characters += string.ascii_letters
        if use_numbers:
            characters += string.digits
        if use_symbols:
            characters += string.punctuation

        if not characters:
            self.result_label.setText("En az bir karakter türü seçmelisiniz.")
            return

        length = 16  # Belirlediğiniz uzunluk
        password = ''.join(random.choice(characters) for _ in range(length))

        selected_option = self.input_combobox.currentText()
        username_or_email = self.username_entry.text()

        if username_or_email and selected_option:
            self.cursor.execute("INSERT INTO passwords (type, identifier, password) VALUES (?, ?, ?)", (selected_option, username_or_email, password))
            self.conn.commit()
            self.load_saved_passwords()

        self.result_label.setText("Oluşturulan Parola: " + password)

class PasswordProtectedApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("K!32")
        self.setGeometry(100, 100, 400, 300)

        self.remaining_attempts = 3  # Toplam deneme hakkı
        self.init_hash_table()  # Hash tablosunu oluşturuyoruz ve veritabanını hazırlıyoruz
        self.password_protected()

    def init_hash_table(self):
        # Hash tablosunu ve veritabanını hazırlama
        self.conn = sqlite3.connect("passwords.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS hashes (id INTEGER PRIMARY KEY, hash_value TEXT)")
        self.conn.commit()

    def password_protected(self):
        # Giriş şifresini kontrol etme ve uygulamayı koruma
        while self.remaining_attempts > 0:
            password, ok = QInputDialog.getText(None, "Giriş Şifresi", f"Kalan deneme hakkı: {self.remaining_attempts}\nGiriş şifresini girin:", QLineEdit.Password)

            if ok and self.check_hash(password):
                self.init_main_app()
                return
            else:
                self.remaining_attempts -= 1

        sys.exit()

    def init_main_app(self):
        main_layout = QVBoxLayout()

        main_app = PasswordGeneratorApp()  # Parola yöneticisi uygulaması nesnesi
        main_layout.addWidget(main_app)  # Parola yöneticisi uygulamasını ana pencereye ekliyoruz

        main_container = QWidget()
        main_container.setLayout(main_layout)
        self.setCentralWidget(main_container)

    def check_hash(self, input_password):
        # Girilen şifrenin hash değerini kontrol etme
        hashed_input_password = calculate_hash(input_password)
        self.cursor.execute("SELECT * FROM hashes WHERE hash_value = ?", (hashed_input_password,))
        return self.cursor.fetchone() is not None

def calculate_hash(input_string):
    # Verilen metni SHA-256 algoritmasıyla hash'e çevirme
    hash_object = hashlib.sha256(input_string.encode())
    hash_value = hash_object.hexdigest()
    return hash_value

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PasswordProtectedApp()
    window.show()
    sys.exit(app.exec_())
