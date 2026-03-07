import sys
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton, 
                             QFileDialog, QLineEdit, QMessageBox, QComboBox, QSizePolicy, QSpacerItem)
from PyQt6.QtCore import pyqtSignal, QSettings

import config

class dialog_settings(QDialog):
    standard_path = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Einstellungen")
        self.resize(500, 250)
        self.settings = QSettings("de.innobiz", "DSASettlementGenerator")
        self.label_folder = QLabel("Speicherort")
        self.le_folder = QLineEdit()
        self.btn_select_folder = QPushButton("Ordner wählen")
        self.label_model = QLabel("Model")
        self.cb_model = QComboBox()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        layout_form = QGridLayout()
        layout_form.addWidget(self.label_folder, 0, 0)
        layout_form.addWidget(self.le_folder, 0, 1)
        layout_form.addWidget(self.btn_select_folder, 0, 3)
        self.btn_select_folder.clicked.connect(self.select_folder)

        layout_form.addWidget(self.label_model, 1, 0)
        layout_form.addWidget(self.cb_model, 1, 1)

        for model in config.aiModels.keys():
            self.cb_model.addItem(model)
        
        self.cb_model.setCurrentText(config.modelSelected)
        self.cb_model.currentTextChanged.connect(self.model_updated)
        
        layout.addLayout(layout_form)

        button_layout = QHBoxLayout()
        button_layout.addSpacerItem(QSpacerItem(40, 20, 
                            QSizePolicy.Policy.Expanding, 
                            QSizePolicy.Policy.Minimum))
        submit_button = QPushButton("Speichern")
        submit_button.clicked.connect(self.submit_dialog)
        button_layout.addWidget(submit_button)
        cancel_button = QPushButton("Abbrechen")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)  

        layout.addLayout(button_layout)

        self.le_folder.setText(self.settings.value('standard_path'))

    def submit_dialog(self):
        path = Path(self.le_folder.text())
        if path.exists():
            self.standard_path.emit(str(path))

        self.accept()


    def select_folder(self):
        ordner_pfad = QFileDialog.getExistingDirectory(
            parent=None,
            caption="Ordner auswählen",
            directory="."  # Startverzeichnis
        )
        if ordner_pfad:
            self.le_folder.setText(ordner_pfad)
        else:
            QMessageBox.warning(self, "Fehler", "Der Pfad ist nicht korrekt bitte prüfen.")
    
    def model_updated(self):
        config.modelSelected = self.cb_model.currentText()

def main():
    app  = QApplication(sys.argv)
    dialog = dialog_settings()
    dialog.exec()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
    