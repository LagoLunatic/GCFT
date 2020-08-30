# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'yaz0_tab.ui'
##
## Created by: Qt User Interface Compiler version 5.14.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import (QCoreApplication, QDate, QDateTime, QMetaObject,
    QObject, QPoint, QRect, QSize, QTime, QUrl, Qt)
from PySide2.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont,
    QFontDatabase, QIcon, QKeySequence, QLinearGradient, QPalette, QPainter,
    QPixmap, QRadialGradient)
from PySide2.QtWidgets import *


class Ui_Yaz0Tab(object):
    def setupUi(self, Yaz0Tab):
        if not Yaz0Tab.objectName():
            Yaz0Tab.setObjectName(u"Yaz0Tab")
        Yaz0Tab.resize(776, 515)
        self.verticalLayout = QVBoxLayout(Yaz0Tab)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.decompress_yaz0 = QPushButton(Yaz0Tab)
        self.decompress_yaz0.setObjectName(u"decompress_yaz0")

        self.horizontalLayout_2.addWidget(self.decompress_yaz0)

        self.compress_yaz0 = QPushButton(Yaz0Tab)
        self.compress_yaz0.setObjectName(u"compress_yaz0")

        self.horizontalLayout_2.addWidget(self.compress_yaz0)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.verticalSpacer = QSpacerItem(20, 463, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)


        self.retranslateUi(Yaz0Tab)

        QMetaObject.connectSlotsByName(Yaz0Tab)
    # setupUi

    def retranslateUi(self, Yaz0Tab):
        Yaz0Tab.setWindowTitle(QCoreApplication.translate("Yaz0Tab", u"Form", None))
        self.decompress_yaz0.setText(QCoreApplication.translate("Yaz0Tab", u"Decompress File", None))
        self.compress_yaz0.setText(QCoreApplication.translate("Yaz0Tab", u"Compress File", None))
    # retranslateUi

