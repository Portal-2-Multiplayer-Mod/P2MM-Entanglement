from PyQt5 import QtCore, QtGui, QtWidgets
import modules.Configs as cfg


class ConfigFieldModel(QtWidgets.QWidget):

    Config: cfg.ConfigProperties
    Value: any

    def __init__(self, config: cfg.ConfigProperties) -> None:
        super(ConfigFieldModel, self).__init__()
        self.setObjectName("configFieldModel")

        self.Config = config

        layout = QtWidgets.QVBoxLayout()

        layout.addWidget(self.CreateNameLabel())
        layout.addWidget(self.CreateHintLabel())
        layout.addWidget(self.CreateValueField())

        spacerItem = QtWidgets.QSpacerItem(10, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        layout.addItem(spacerItem)

        self.setLayout(layout)

    def CreateNameLabel(self) -> QtWidgets.QLabel:
        name = cfg.GetLabelName(self.Config)
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

    def CreateHintLabel(self) -> QtWidgets.QLabel:
        hint = cfg.GetHint(self.Config)
        HintLabel = QtWidgets.QLabel(self)

        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(HintLabel.sizePolicy().hasHeightForWidth())

        HintLabel.setSizePolicy(sizePolicy)

        font = QtGui.QFont()
        font.setPointSize(8)
        font.setItalic(True)

        HintLabel.setFont(font)
        HintLabel.setObjectName("Hint")
        HintLabel.setText(hint)
        return HintLabel

    def CreateValueField(self) -> QtWidgets.QWidget:
        customType: type = cfg.GetType(self.Config)
        self.Value = cfg.GetValue(self.Config)

        ValueField: QtWidgets.QWidget

        if customType is int:
            ValueField = QtWidgets.QSpinBox(self)
            ValueField.setValue(self.Value)
            ValueField.valueChanged.connect(self.OnValueChanged)

        elif customType is bool:
            ValueField = QtWidgets.QCheckBox(self)
            ValueField.text = ""
            ValueField.setChecked(self.Value)
            ValueField.stateChanged.connect(self.OnValueChanged)

        else:
            ValueField = QtWidgets.QLineEdit(self)
            ValueField.setText(str(self.Value))
            ValueField.textChanged.connect(self.OnValueChanged)

        ValueField.setMinimumSize(QtCore.QSize(0, 30))
        ValueField.setObjectName("Value")

        return ValueField

    def OnValueChanged(self, event) -> None:
        self.Value = event

    def SaveValue(self) -> None:
        cfg.SetValue(self.Config, self.Value)
