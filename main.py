import sys
import asyncio
import os
from mistralai import Mistral, models
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QWidget, 
                             QPushButton, QComboBox, QTextEdit, QMessageBox, QSizePolicy)
from PyQt6.QtCore import Qt, QSettings, QStandardPaths, pyqtSlot
from PyQt6.QtGui import QAction, QKeySequence
from qasync import QEventLoop, asyncSlot

import dialogAPIkey
import dialog_about
import dialog_settings
import config


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DSA Siedlungsgenerator")
        self.resize(400, 300)
        self.menu = self.menuBar()
        self.menuApiKey = QAction("API-Key eingeben", self)
        self.menu_settings = QAction("Einstellungen", self)
        self.menu_settings.setShortcut(QKeySequence.StandardKey.Preferences)
        self.menu_about = QAction("Über die App")
        self.settings = QSettings("de.innobiz", "DSASettlementGenerator")
        self.client = None
        self.settlement = QTextEdit()
        self.tb_query = QTextEdit()
        self.tb_query_label = QLabel("Besonderheit der Siedlung:")
        self.cb_size = QComboBox()
        self.cb_size_label = QLabel("Größe der Siedlung:")
        self.cb_region = QComboBox()
        self.cb_region_label = QLabel("Region der Siedlung:")
        self.btn_generate = QPushButton("Siedlung generieren")
        self.cb_saved_settlements = QComboBox()
        self.btn_save_settlement = QPushButton("Siedlung speichern")

        self.initUI()
        self.load_settings()

    def initUI(self):
        # Menüleiste
        file_menu = self.menu.addMenu("Datei")
        file_menu.addAction(self.menu_about)
        self.menu_about.triggered.connect(self.open_dialog_about)
        settings_menu = self.menu.addMenu("Einstellungen")
        settings_menu.addAction(self.menuApiKey)
        self.menuApiKey.triggered.connect(self.open_api_key_dialog)
        settings_menu.addAction(self.menu_settings)
        self.menu_settings.triggered.connect(self.open_dialog_settings)

        # Setting up the central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        layout_generate = QHBoxLayout()
        layout_cbs = QVBoxLayout()
        layout_cbs.setSpacing(3)
        layout_cb_size = QHBoxLayout()
        layout_cb_size.addWidget(self.cb_size_label)
        layout_cb_size.addWidget(self.cb_size)
        self.cb_size.addItems(["-100", "-250", "-500", "-1000", "-2500", "-5000", "-10000"])
        layout_cbs.addLayout(layout_cb_size) 
        layout_cb_region = QHBoxLayout()
        layout_cb_region.addWidget(self.cb_region_label)
        layout_cb_region.addWidget(self.cb_region)
        self.cb_region.addItems(["Mittelreich", "Bornland", "Garetien", "Andergast", "Nostria", "Liebliches Feld", "Al'Anfa", "Mhanadistan", "Zorgan", "Weiden", "Orkland", "Thorwal"])
        layout_cbs.addLayout(layout_cb_region)
        layout_generate.addLayout(layout_cbs) 

        layout_query = QVBoxLayout()
        layout_query.addWidget(self.tb_query_label)
        layout_query.addWidget(self.tb_query)  
        self.tb_query.setPlaceholderText("Hier kann eine Besonderheit eingegeben werden.")
        self.tb_query.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred
        )
       
        layout_generate.addLayout(layout_query)
        layout_generate.addWidget(self.btn_generate)
        self.btn_generate.clicked.connect(self.on_generate_clicked)
        layout.addLayout(layout_generate)

        layout.addWidget(self.settlement)

        layout_save = QHBoxLayout()
        layout_save.addWidget(self.cb_saved_settlements)
        if self.get_settlement_list():
            self.cb_saved_settlements.setEnabled(True)
        else:
            self.cb_saved_settlements.setEnabled(False)

        self.cb_saved_settlements.currentTextChanged.connect(self.load_settlement)
        self.cb_saved_settlements.setPlaceholderText("Gespeicherte Siedlungen")
        layout_save.addStretch()
        layout_save.addWidget(self.btn_save_settlement)
        self.btn_save_settlement.setEnabled(False)
        self.btn_save_settlement.clicked.connect(self.save_settlement)
        layout.addLayout(layout_save)

    def load_settings(self):
        # Fenstergeometrie
        geometry = self.settings.value('window/geometry')
        if geometry:
            self.restoreGeometry(geometry)

        state = self.settings.value('window/state')
        if state:
            self.restoreState(state)   
        
        position = self.settings.value('window/position')
        if position:
            self.move(position)

        size = self.settings.value('window/size')
        if size:
            self.resize(size) 

        # Nutzerinformationen
        api_key = self.settings.value("api_key", "")
        if api_key:
            self.setup_chat(api_key)
        else:
            self.settlement.setText("""
                API-Key fehlt. Bitte in den Einstellungen eingeben. Diese App verwendet die API von mistral.ai, 
                um Siedlungen für das Rollenspiel Das Schwarze Auge zu generieren.
                
                Um Siedlungen zu speichern empfiehlt es sich in den Eintellungen einen Standardpfad für Siedlungen zu hinterlegen.
                """)

        config.modelSelected = self.settings.value('model/selected', config.modelSelected)
    
    def save_settings(self):
        self.settings.setValue('window/geometry', self.saveGeometry())
        self.settings.setValue('window/state', self.saveState())
        self.settings.setValue('window/position', self.pos())
        self.settings.setValue('window/size', self.size())
        self.settings.setValue('model/selected', config.modelSelected)

    @asyncSlot()
    async def on_generate_clicked(self):
        await self.generate_settlement()

    async def generate_settlement(self):
        self.settlement.clear()
        self.btn_save_settlement.setEnabled(False)
        extra = f" Besonderheit der Siedlung: {self.tb_query.toPlainText()}." if self.tb_query.toPlainText() else ""
        messages = [
            {"role": "system", "content": """
             Du bist ein Experte für die Erstellung von Siedlungen in der Welt von Das Schwarze Auge. 
             Erstelle eine Siedlung basierend auf den Parametern maximale Größe, Region und ggf. Besonderheit, die dir vom Benutzer vorgegeben werden.
             Es gibt folgende Größenkategorien für Siedlungen, die der Benutzer wählen kann: "-100", "-250", "-500", "-1000", "-2500", "-5000", "-10000"
             Orientiere dich an der Spielhilfe "Siedlungen und Städte" aus der 5. Edition von Das Schwarze Auge, um die Siedlung zu erstellen.
             Strukturiere die Antwort wie folgt:
                Name der Siedlung: <Name>
                Größe der Siedlung: <Anzahl der Einwohner und Rassen z.B. so (60% Menschen, 20% Zwerge, 10% Elfen, 10% andere Rassen)>
                Tavernen und Herbergen: <Namen und kurze Beschreibung in maximal fünf Stichpunkten (Herberge mit Bewirtung, gehobene Ausstattung, Abendunterhaltung, Wohlhabende Reisende und Bürger)>
                Handwerksbetriebe: <Namen und kurze Beschreibung in maximal fünf Stichpunkten>
                Händler und Märkte: <Namen und kurze Beschreibung>
                Tempel und Schreine: <Namen und kurze Beschreibung in maximal drei Stichpunkten>
                Besondere Bewohner: <Namen und kurze Beschreibung> (je nach Größe maximal 10 Bewohner)
                Besonderheit der Siedlung: 
                <Beschreibung der Besonderheit in maximal fünf Sätzen. Wenn eine Besonderheit vorgegeben wurde, kann diese in der Beschreibung der Besonderheit der Siedlung vorkommen. 
                 Sonst hat die Siedlung mit einer Wahrscheinlichkeit von 10% je Größenstufe eine Besonderheit, die in der Beschreibung der Besonderheit der Siedlung vorkommen kann. Andernsfalls seteht hier "Keine Besonderheit".>
                Nähere Umgebung: 
                <kurze Beschreibung der Umgebung in maxiaml drei Sätzen>
             
             Achte darauf, dass die Siedlung in sich stimmig ist und die Besonderheit der Siedlung gut in die Siedlung integriert ist. Es sollen nur Elemente aus DSA verwendet werden und keine anderen Systeme.
             Es ist möglich, dass nicht immer alle Kategorien vollständig gefüllt werden können, da die Siedlung je nach Größe und Besonderheit unterschiedlich aufgebaut sein kann. Fülle die Kategorien so gut wie möglich aus aber zwinge dich nicht dazu, alle Kategorien zu füllen, wenn es nicht sinnvoll ist.
             """
             },
            {"role": "user", "content": f"Größe der Siedlung bis {self.cb_size.currentText().replace('-', '')} Einwohner, in der Region {self.cb_region.currentText()}.{extra}"}
        ]

        try:
            response = await self.client.chat.stream_async(
                model=config.modelSelected,
                messages=messages,
                temperature=0.5
            )

            assert response
            async for chunk in response:
                if chunk.data.choices[0].delta.content is not None:
                    self.settlement.setText(self.settlement.toPlainText() + chunk.data.choices[0].delta.content)

        except models.MistralError as e:
            QMessageBox.warning(
                self,
                "Fehler",
                f"Die Siedlung konnte nicht generiert werden.\n\nMistral API-Fehler: {e}"
            )
            return
        
        if len(self.settlement.toPlainText()) > 0:
            self.btn_save_settlement.setEnabled(True)
            self.settlement.setMarkdown(self.settlement.toPlainText())
        else:
            QMessageBox.warning(self, "Fehler", "Die Siedlung konnte nicht generiert werden. Bitte überprüfen Sie Ihre Eingaben und versuchen Sie es erneut.")  
            

    def setup_chat(self, api_key):
        try:
            self.client = Mistral(api_key=api_key)
            # Falls der Login passt muss die App aktiv werden.

            mistral_models = self.client.models.list().data
            text_models = [m for m in mistral_models if hasattr(m.capabilities, 'completion_chat') and m.capabilities.completion_chat]
            for model in text_models:
                config.aiModels[model.id] = f"Name: {model.name}, Max. Kontext: {model.max_context_length}"

            return True
        except models.MistralError as e:
            # The base class for HTTP error responses
            print(e.message)
            print(e.status_code)
            print(e.body)
            print(e.headers)
            print(e.raw_response)

            # Depending on the method different errors may be thrown
            if isinstance(e, models.HTTPValidationError):
                print(e.data.detail)  # Optional[List[mistralai.client.ValidationError]]


    def open_dialog_about(self):
        dialog = dialog_about.dialog_about(self)
        dialog.move(self.geometry().center() - dialog.rect().center()) 
        dialog.exec()

    def open_api_key_dialog(self):
        dialog = dialogAPIkey.APIKeyDialog(self)
        dialog.api_key_entered.connect(self.set_api_key)
        dialog.move(self.geometry().center() - dialog.rect().center()) 
        dialog.exec()

    def open_dialog_settings(self):
        dialog = dialog_settings.dialog_settings(self)
        dialog.standard_path.connect(self.set_settings)
        dialog.move(self.geometry().center() - dialog.rect().center()) 
        dialog.exec()

    
    @pyqtSlot(str)
    def set_api_key(self, api_key):
        if self.setup_chat(api_key):
            self.settlement.setText("Modell erfolgreich geladen.")
            self.settings.setValue("api_key", api_key)

    @pyqtSlot(str)
    def set_settings(self, standard_path):
        self.settings.setValue('standard_path', standard_path)

    def closeEvent(self, event):
    # Automatisch beim Schließen speichern
        self.save_settings()
        event.accept()
    
    def save_settlement(self):
        settlement_name = self.settlement.toPlainText().splitlines()[0]
        settlement_name = settlement_name.replace("#", "").replace("*", "")
        settlement_name = settlement_name.replace("Name der Siedlung: ", "").strip()
        if settlement_name:
            if settlement_name in [self.cb_saved_settlements.itemText(i) for i in range(self.cb_saved_settlements.count())]:
                QMessageBox.warning(self, "Fehler", "Eine Siedlung mit diesem Namen existiert bereits.")
                return
            
            self.cb_saved_settlements.addItem(settlement_name)
            self.cb_saved_settlements.setEnabled(True)
            
            standard_path = self.settings.value('standard_path')
            if standard_path:
                file_path = standard_path + "/" + settlement_name + ".md"
            else:
                file_path = os.path.join(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation), settlement_name + ".md")
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(self.settlement.toMarkdown())
            QMessageBox.information(self, "Erfolg", f"Siedlung '{settlement_name}' wurde erfolgreich gespeichert.")
        else:
            QMessageBox.warning(self, "Fehler", "Die Siedlung konnte nicht gespeichert werden, da kein Name gefunden wurde.")

    def load_settlement(self, settlement_name):
        if settlement_name == 'Wähle eine Siedlung':
            return
        
        standard_path = self.settings.value('standard_path')
        if standard_path:
            documents_path = standard_path
        else:
            documents_path = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation)

        file = documents_path + "/" + settlement_name + ".md"
        
        if os.path.exists(file):
            with open(file, "r", encoding="utf-8") as f:
                content = f.read()
                self.settlement.setMarkdown(content)
                self.btn_save_settlement.setEnabled(True)
        else:
            QMessageBox.warning(self, "Fehler", f"Siedlung '{settlement_name}' konnte nicht gefunden werden.")
    
    def get_settlement_list(self):
        standard_path = self.settings.value('standard_path')
        if standard_path:
            documents_path = standard_path
        else:
            documents_path = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation)
        
        settlements = []
        for file in os.listdir(documents_path):
            if file.endswith(".md"):
                settlements.append(file[:-3])  # Entfernt die .md Endung
        
        if len(settlements) > 0:
            self.cb_saved_settlements.clear()
            self.cb_saved_settlements.addItem('Wähle eine Siedlung')
            self.cb_saved_settlements.addItems(settlements)
        return len(settlements) > 0

# Ende der MainWindow-Klasse

def main():
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    window = MainWindow()
    window.show()
    with loop:
        loop.run_forever()

if __name__ == "__main__":
    main()