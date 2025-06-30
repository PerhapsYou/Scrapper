from PyQt5.QtWidgets import QApplication, QLabel

app = QApplication([])
label = QLabel("If you see this, PyQt5 works!")
label.show()
app.exec_()