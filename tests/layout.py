import sys
from PyQt6.QtWidgets import QApplication
# from FOGSE import application
from FoGSE.application import GSEMain, GSEFocus, GSECommand

app = QApplication([])
# window = GSEMain()
# window = GSEFocus()
window = GSECommand()
window.show()
sys.exit(app.exec())