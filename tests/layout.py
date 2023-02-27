import sys
from PyQt6.QtWidgets import QApplication
# from FOGSE import application
from FoGSE.application import GSEMain, GSEFocus

app = QApplication([])
window = GSEMain()
# window = GSEFocus()
window.show()
sys.exit(app.exec())