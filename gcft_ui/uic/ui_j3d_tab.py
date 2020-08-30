# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'j3d_tab.ui'
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


class Ui_J3DTab(object):
    def setupUi(self, J3DTab):
        if not J3DTab.objectName():
            J3DTab.setObjectName(u"J3DTab")
        J3DTab.resize(776, 515)
        self.actionOpenJ3DImage = QAction(J3DTab)
        self.actionOpenJ3DImage.setObjectName(u"actionOpenJ3DImage")
        self.actionReplaceJ3DImage = QAction(J3DTab)
        self.actionReplaceJ3DImage.setObjectName(u"actionReplaceJ3DImage")
        self.verticalLayout = QVBoxLayout(J3DTab)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.import_j3d = QPushButton(J3DTab)
        self.import_j3d.setObjectName(u"import_j3d")

        self.horizontalLayout_6.addWidget(self.import_j3d)

        self.export_j3d = QPushButton(J3DTab)
        self.export_j3d.setObjectName(u"export_j3d")

        self.horizontalLayout_6.addWidget(self.export_j3d)


        self.verticalLayout.addLayout(self.horizontalLayout_6)

        self.j3d_chunks_tree = QTreeWidget(J3DTab)
        self.j3d_chunks_tree.setObjectName(u"j3d_chunks_tree")

        self.verticalLayout.addWidget(self.j3d_chunks_tree)


        self.retranslateUi(J3DTab)

        QMetaObject.connectSlotsByName(J3DTab)
    # setupUi

    def retranslateUi(self, J3DTab):
        J3DTab.setWindowTitle(QCoreApplication.translate("J3DTab", u"Form", None))
        self.actionOpenJ3DImage.setText(QCoreApplication.translate("J3DTab", u"Open Image", None))
        self.actionReplaceJ3DImage.setText(QCoreApplication.translate("J3DTab", u"Replace Image", None))
        self.import_j3d.setText(QCoreApplication.translate("J3DTab", u"Import J3D File", None))
        self.export_j3d.setText(QCoreApplication.translate("J3DTab", u"Export J3D File", None))
        ___qtreewidgetitem = self.j3d_chunks_tree.headerItem()
        ___qtreewidgetitem.setText(2, QCoreApplication.translate("J3DTab", u"Size", None));
        ___qtreewidgetitem.setText(1, QCoreApplication.translate("J3DTab", u"Texture Name", None));
        ___qtreewidgetitem.setText(0, QCoreApplication.translate("J3DTab", u"Chunk Type", None));
    # retranslateUi

