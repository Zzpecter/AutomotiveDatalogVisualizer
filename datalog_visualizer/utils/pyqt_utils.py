from PyQt5.QtWidgets import QLabel, QComboBox


def create_combo_box(label_text, items, layout, width=80):
    lbl = QLabel(label_text)
    lbl.setStyleSheet("font-weight: bold; margin-left: 10px;")
    box = QComboBox()
    box.addItems(items)
    box.setFixedWidth(width)
    layout.addWidget(lbl)
    layout.addWidget(box)
    return box
