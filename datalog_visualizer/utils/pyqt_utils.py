from PyQt5.QtWidgets import QMessageBox, QLabel, QComboBox


def show_message(parent, title, message, icon=QMessageBox.Information):
    msg = QMessageBox(parent)
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.setIcon(icon)
    msg.exec_()


def create_combo_box(label_text, items, layout, width=80):
    lbl = QLabel(label_text)
    lbl.setStyleSheet("font-weight: bold; margin-left: 10px;")
    box = QComboBox()
    box.addItems(items)
    box.setFixedWidth(width)
    layout.addWidget(lbl)
    layout.addWidget(box)
    return box
