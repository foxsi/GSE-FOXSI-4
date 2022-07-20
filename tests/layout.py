import sys
from PyQt6.QtWidgets import QApplication
# from FoGSE import application
from FoGSE.application import GSEMain

app = QApplication([])
window = GSEMain()
window.show()
sys.exit(app.exec())