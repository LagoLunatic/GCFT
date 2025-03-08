# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'dol_tab.ui'
##
## Created by: Qt User Interface Compiler version 6.8.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFormLayout, QHBoxLayout, QHeaderView,
    QLabel, QLineEdit, QPushButton, QSizePolicy,
    QTreeView, QVBoxLayout, QWidget)

class Ui_DOLTab(object):
    def setupUi(self, DOLTab):
        if not DOLTab.objectName():
            DOLTab.setObjectName(u"DOLTab")
        DOLTab.resize(776, 515)
        self.verticalLayout = QVBoxLayout(DOLTab)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.import_dol = QPushButton(DOLTab)
        self.import_dol.setObjectName(u"import_dol")

        self.horizontalLayout_9.addWidget(self.import_dol)

        self.export_dol = QPushButton(DOLTab)
        self.export_dol.setObjectName(u"export_dol")

        self.horizontalLayout_9.addWidget(self.export_dol)


        self.verticalLayout.addLayout(self.horizontalLayout_9)

        self.horizontalLayout_10 = QHBoxLayout()
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.formLayout_2 = QFormLayout()
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.formLayout_2.setHorizontalSpacing(0)
        self.label_13 = QLabel(DOLTab)
        self.label_13.setObjectName(u"label_13")

        self.formLayout_2.setWidget(0, QFormLayout.LabelRole, self.label_13)

        self.dol_address = QLineEdit(DOLTab)
        self.dol_address.setObjectName(u"dol_address")

        self.formLayout_2.setWidget(0, QFormLayout.FieldRole, self.dol_address)


        self.horizontalLayout_10.addLayout(self.formLayout_2)

        self.convert_from_dol_offset = QPushButton(DOLTab)
        self.convert_from_dol_offset.setObjectName(u"convert_from_dol_offset")

        self.horizontalLayout_10.addWidget(self.convert_from_dol_offset)

        self.convert_from_dol_address = QPushButton(DOLTab)
        self.convert_from_dol_address.setObjectName(u"convert_from_dol_address")

        self.horizontalLayout_10.addWidget(self.convert_from_dol_address)

        self.formLayout_3 = QFormLayout()
        self.formLayout_3.setObjectName(u"formLayout_3")
        self.formLayout_3.setHorizontalSpacing(0)
        self.label_14 = QLabel(DOLTab)
        self.label_14.setObjectName(u"label_14")

        self.formLayout_3.setWidget(0, QFormLayout.LabelRole, self.label_14)

        self.dol_offset = QLineEdit(DOLTab)
        self.dol_offset.setObjectName(u"dol_offset")

        self.formLayout_3.setWidget(0, QFormLayout.FieldRole, self.dol_offset)


        self.horizontalLayout_10.addLayout(self.formLayout_3)


        self.verticalLayout.addLayout(self.horizontalLayout_10)

        self.dol_sections_tree = QTreeView(DOLTab)
        self.dol_sections_tree.setObjectName(u"dol_sections_tree")

        self.verticalLayout.addWidget(self.dol_sections_tree)


        self.retranslateUi(DOLTab)

        QMetaObject.connectSlotsByName(DOLTab)
    # setupUi

    def retranslateUi(self, DOLTab):
        DOLTab.setWindowTitle(QCoreApplication.translate("DOLTab", u"Form", None))
        self.import_dol.setText(QCoreApplication.translate("DOLTab", u"Import DOL", None))
        self.export_dol.setText(QCoreApplication.translate("DOLTab", u"Export DOL", None))
        self.label_13.setText(QCoreApplication.translate("DOLTab", u"RAM Address: 0x", None))
        self.convert_from_dol_offset.setText(QCoreApplication.translate("DOLTab", u"<- Convert offset to address", None))
        self.convert_from_dol_address.setText(QCoreApplication.translate("DOLTab", u"Convert address to offset ->", None))
        self.label_14.setText(QCoreApplication.translate("DOLTab", u"Offset in DOL: 0x", None))
    # retranslateUi

