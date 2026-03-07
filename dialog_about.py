import sys
import re
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

class dialog_about(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Über DSA Siedlungsgenerator")
        self.resize(300, 250)
        self.text_label = QLabel()
        self.initUI()

    def initUI(self):
        version = self.get_version_from_spec()
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("DSA Siedlungsgenerator")
        title.setFont(QFont("Helvetica", 14, QFont.Weight.Bold))
        layout.addWidget(title)
        
        self.text_label.setText(
            """
            <p>Ein Tool zur Generierung von Siedlungen in der Welt von DSA.</p>
            <p>Dies ist ein Hobby Projekt. Bugs können auf <a href="https://github.com/Sikarjan/siedlungsgenerator">GitHub</a> gemeldet werden.</p>
            <p>Das Schwareze Auge ist eine Marke von Ulisses.</p>
            """
        )
        self.text_label.setOpenExternalLinks(True)
        self.text_label.setWordWrap(True)          # Textumbruch aktivieren
        self.text_label.setTextFormat(Qt.TextFormat.RichText)  # HTML-Formatierung
        self.text_label.setTextInteractionFlags(Qt.TextInteractionFlag.LinksAccessibleByMouse)

        layout.addWidget(QLabel(f"Version: {version}"))
        layout.addWidget(self.text_label)
        
        button = QPushButton("Schließen")
        button.clicked.connect(self.accept)
        layout.addWidget(button)

    @staticmethod
    def get_version_from_spec():
        """Liest die Version aus der .spec-Datei aus."""
        spec_path = Path(__file__).parent / "DSA_Siedlungsgenerator.spec"
        try:
            with open(spec_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Suche nach CFBundleVersion im info_plist-Dictionary
                match = re.search(r"'CFBundleVersion'\s*:\s*'([^']+)'", content)
                if match:
                    return match.group(1)
                # Fallback: Suche nach CFBundleShortVersionString im info_plist-Dictionary
                match = re.search(r"'CFBundleShortVersionString'\s*:\s*'([^']+)'", content)
                if match:
                    return match.group(1)
        except FileNotFoundError:
            pass
        return "Unbekannt"

def main():
    app  = QApplication(sys.argv)
    dialog = dialog_about()
    dialog.exec()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
    