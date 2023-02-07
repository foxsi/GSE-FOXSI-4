import sys
from PyQt6.QtWidgets import QApplication
# from FoGSE import application
from FoGSE.application import GSEFocus, GSEMain

app = QApplication([])
# window = GSEFocus()
window = GSEMain()
window.show()
sys.exit(app.exec())