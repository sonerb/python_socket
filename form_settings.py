# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'form_settings.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Settings(object):
    def setupUi(self, Settings):
        Settings.setObjectName("Settings")
        Settings.resize(285, 250)
        self.verticalLayout = QtWidgets.QVBoxLayout(Settings)
        self.verticalLayout.setObjectName("verticalLayout")
        self.grpbox_server = QtWidgets.QGroupBox(Settings)
        self.grpbox_server.setObjectName("grpbox_server")
        self.formLayout = QtWidgets.QFormLayout(self.grpbox_server)
        self.formLayout.setObjectName("formLayout")
        self.lbl_server_address = QtWidgets.QLabel(self.grpbox_server)
        self.lbl_server_address.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lbl_server_address.setObjectName("lbl_server_address")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.lbl_server_address)
        self.txt_server_address = QtWidgets.QLineEdit(self.grpbox_server)
        self.txt_server_address.setObjectName("txt_server_address")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.txt_server_address)
        self.lbl_server_port = QtWidgets.QLabel(self.grpbox_server)
        self.lbl_server_port.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.lbl_server_port.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lbl_server_port.setObjectName("lbl_server_port")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.lbl_server_port)
        self.txt_server_port = QtWidgets.QLineEdit(self.grpbox_server)
        self.txt_server_port.setObjectName("txt_server_port")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.txt_server_port)
        self.verticalLayout.addWidget(self.grpbox_server)
        self.grpbox_encryption = QtWidgets.QGroupBox(Settings)
        self.grpbox_encryption.setObjectName("grpbox_encryption")
        self.formLayout_2 = QtWidgets.QFormLayout(self.grpbox_encryption)
        self.formLayout_2.setObjectName("formLayout_2")
        self.lbl_enc_password = QtWidgets.QLabel(self.grpbox_encryption)
        self.lbl_enc_password.setObjectName("lbl_enc_password")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.lbl_enc_password)
        self.txt_enc_password = QtWidgets.QLineEdit(self.grpbox_encryption)
        self.txt_enc_password.setObjectName("txt_enc_password")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.txt_enc_password)
        self.verticalLayout.addWidget(self.grpbox_encryption)
        self.grpbox_misc = QtWidgets.QGroupBox(Settings)
        self.grpbox_misc.setObjectName("grpbox_misc")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.grpbox_misc)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.chb_minimize = QtWidgets.QCheckBox(self.grpbox_misc)
        self.chb_minimize.setObjectName("chb_minimize")
        self.verticalLayout_2.addWidget(self.chb_minimize)
        self.verticalLayout.addWidget(self.grpbox_misc)
        self.buttonBox = QtWidgets.QDialogButtonBox(Settings)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Settings)
        self.buttonBox.accepted.connect(Settings.accept)
        self.buttonBox.rejected.connect(Settings.reject)
        QtCore.QMetaObject.connectSlotsByName(Settings)

    def retranslateUi(self, Settings):
        _translate = QtCore.QCoreApplication.translate
        Settings.setWindowTitle(_translate("Settings", "Settings"))
        self.grpbox_server.setTitle(_translate("Settings", "Server"))
        self.lbl_server_address.setText(_translate("Settings", "Address :"))
        self.lbl_server_port.setText(_translate("Settings", "Port :"))
        self.grpbox_encryption.setTitle(_translate("Settings", "Encryption"))
        self.lbl_enc_password.setText(_translate("Settings", "Password :"))
        self.grpbox_misc.setTitle(_translate("Settings", "Miscellaneous"))
        self.chb_minimize.setText(_translate("Settings", "Minimize when close"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Settings = QtWidgets.QDialog()
    ui = Ui_Settings()
    ui.setupUi(Settings)
    Settings.show()
    sys.exit(app.exec_())

