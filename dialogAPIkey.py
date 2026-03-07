import sys
from PyQt6.QtWidgets import QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt6.QtCore import pyqtSignal

class APIKeyDialog(QDialog):
    api_key_entered = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("API-Key Eingabe")
        self.resize(300, 150)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        label = QLabel("Bitte geben Sie Ihren API-Key ein:")
        layout.addWidget(label)

        self.api_key_input = QLineEdit()
        layout.addWidget(self.api_key_input)

        button_layout = QHBoxLayout()

        submit_button = QPushButton("OK")
        submit_button.clicked.connect(self.submit_api_key)
        button_layout.addWidget(submit_button)
        cancel_button = QPushButton("Abbrechen")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)  

        layout.addLayout(button_layout)

    def submit_api_key(self):
        api_key = self.api_key_input.text().strip()
        if api_key:
            self.api_key_entered.emit(api_key)
            self.accept()
        else:
            QMessageBox.warning(self, "Fehler", "API-Key darf nicht leer sein.")

def main():
    app = QApplication(sys.argv)
    dialog = APIKeyDialog()
    dialog.exec()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()