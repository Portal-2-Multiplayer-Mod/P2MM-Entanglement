from PyQt5 import QtCore, QtGui, QtWidgets


class ConfigFieldModel(QtWidgets.QWidget):

    # def __init__(self, steps=5, *args, **kwargs):
    #     super(ConfigFieldModel, self).__init__(*args, **kwargs)
    def __init__(self, name: str, hint: str, value: any, customType: type):
        super(ConfigFieldModel, self).__init__()
        layout = QtWidgets.QVBoxLayout()
        # self.setObjectName("configFieldModel")
        self.Name = QtWidgets.QLabel(self)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.Name.sizePolicy().hasHeightForWidth())
        self.Name.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(20)
        font.setBold(True)
        font.setWeight(75)
        font.setKerning(True)
        self.Name.setFont(font)
        self.Name.setAlignment(QtCore.Qt.AlignLeading |
                               QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.Name.setObjectName("Name")
        layout.addWidget(self.Name)
        self.Hint = QtWidgets.QLabel(self)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.Hint.sizePolicy().hasHeightForWidth())
        self.Hint.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setItalic(True)
        self.Hint.setFont(font)
        self.Hint.setObjectName("Hint")
        layout.addWidget(self.Hint)


        layout.addWidget(self.CreateValueField(customType, value))

        # self.Value = QtWidgets.QLineEdit(self)
        # self.Value.setMinimumSize(QtCore.QSize(0, 30))
        # self.Value.setObjectName("Value")
        # layout.addWidget(self.Value)

        spacerItem = QtWidgets.QSpacerItem(
            10, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        layout.addItem(spacerItem)

        self.setLayout(layout)

        self.Name.setText(name)
        self.Hint.setText(hint)
        # self.Value.setText(str(value))


    def CreateValueField(self, customType: type, value: any) -> QtWidgets.QWidget:
        Value: QtWidgets.QWidget

        if customType is int:
            Value = QtWidgets.QSpinBox(self)
            Value.setValue(value)
        elif customType is bool:
            Value = QtWidgets.QCheckBox(self)
            Value.text = ""
        else:
            Value = QtWidgets.QLineEdit(self)
            Value.setText(value)

        Value.setMinimumSize(QtCore.QSize(0, 30))
        Value.setObjectName("Value")
        return Value

