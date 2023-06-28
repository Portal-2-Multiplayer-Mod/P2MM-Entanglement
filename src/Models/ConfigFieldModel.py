from PyQt5 import QtCore, QtGui, QtWidgets


class ConfigFieldModel(QtWidgets.QWidget):

    def __init__(self, name: str, hint: str, value: any, customType: type) -> None:
        super(ConfigFieldModel, self).__init__()

        self.setObjectName("configFieldModel")

        layout = QtWidgets.QVBoxLayout()

        layout.addWidget(self.CreateNameLabel(name))
        layout.addWidget(self.CreateHintLabel(hint))
        layout.addWidget(self.CreateValueField(customType, value))

        spacerItem = QtWidgets.QSpacerItem(10, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        layout.addItem(spacerItem)

        self.setLayout(layout)

    def CreateNameLabel(self, name: str) -> QtWidgets.QLabel:
        Label = QtWidgets.QLabel(self)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Label.sizePolicy().hasHeightForWidth())

        Label.setSizePolicy(sizePolicy)

        font = QtGui.QFont()
        font.setPointSize(20)
        font.setBold(True)
        font.setWeight(75)
        font.setKerning(True)

        Label.setFont(font)
        Label.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        Label.setObjectName("Label")
        Label.setText(name)
        return Label

    def CreateHintLabel(self, hint: str) -> QtWidgets.QLabel:
        Hint = QtWidgets.QLabel(self)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Hint.sizePolicy().hasHeightForWidth())

        Hint.setSizePolicy(sizePolicy)

        font = QtGui.QFont()
        font.setPointSize(8)
        font.setItalic(True)

        Hint.setFont(font)
        Hint.setObjectName("Hint")
        Hint.setText(hint)
        return Hint

    def CreateValueField(self, customType: type, value: any) -> QtWidgets.QWidget:
        Value: QtWidgets.QWidget

        if customType is int:
            Value = QtWidgets.QSpinBox(self)
            Value.setValue(value)
        elif customType is bool:
            Value = QtWidgets.QCheckBox(self)
            Value.text = ""
            Value.setChecked(value)
        else:
            Value = QtWidgets.QLineEdit(self)
            Value.setText(str(value))

        Value.setMinimumSize(QtCore.QSize(0, 30))
        Value.setObjectName("Value")
        return Value
