# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'jpc_tab.ui'
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


class Ui_JPCTab(object):
    def setupUi(self, JPCTab):
        if not JPCTab.objectName():
            JPCTab.setObjectName(u"JPCTab")
        JPCTab.resize(776, 515)
        self.actionOpenJPCImage = QAction(JPCTab)
        self.actionOpenJPCImage.setObjectName(u"actionOpenJPCImage")
        self.actionReplaceJPCImage = QAction(JPCTab)
        self.actionReplaceJPCImage.setObjectName(u"actionReplaceJPCImage")
        self.verticalLayout = QVBoxLayout(JPCTab)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.import_jpc = QPushButton(JPCTab)
        self.import_jpc.setObjectName(u"import_jpc")

        self.horizontalLayout_4.addWidget(self.import_jpc)

        self.export_jpc = QPushButton(JPCTab)
        self.export_jpc.setObjectName(u"export_jpc")

        self.horizontalLayout_4.addWidget(self.export_jpc)

        self.add_particles_from_folder = QPushButton(JPCTab)
        self.add_particles_from_folder.setObjectName(u"add_particles_from_folder")

        self.horizontalLayout_4.addWidget(self.add_particles_from_folder)

        self.export_jpc_folder = QPushButton(JPCTab)
        self.export_jpc_folder.setObjectName(u"export_jpc_folder")

        self.horizontalLayout_4.addWidget(self.export_jpc_folder)


        self.verticalLayout.addLayout(self.horizontalLayout_4)

        self.jpc_particles_tree = QTreeWidget(JPCTab)
        self.jpc_particles_tree.setObjectName(u"jpc_particles_tree")

        self.verticalLayout.addWidget(self.jpc_particles_tree)


        self.retranslateUi(JPCTab)

        QMetaObject.connectSlotsByName(JPCTab)
    # setupUi

    def retranslateUi(self, JPCTab):
        JPCTab.setWindowTitle(QCoreApplication.translate("JPCTab", u"Form", None))
        self.actionOpenJPCImage.setText(QCoreApplication.translate("JPCTab", u"Open Image", None))
        self.actionReplaceJPCImage.setText(QCoreApplication.translate("JPCTab", u"Replace Image", None))
        self.import_jpc.setText(QCoreApplication.translate("JPCTab", u"Import JPC", None))
        self.export_jpc.setText(QCoreApplication.translate("JPCTab", u"Export JPC", None))
        self.add_particles_from_folder.setText(QCoreApplication.translate("JPCTab", u"Add Particles From Folder", None))
        self.export_jpc_folder.setText(QCoreApplication.translate("JPCTab", u"Export Folder", None))
        ___qtreewidgetitem = self.jpc_particles_tree.headerItem()
        ___qtreewidgetitem.setText(1, QCoreApplication.translate("JPCTab", u"Texture Name", None));
        ___qtreewidgetitem.setText(0, QCoreApplication.translate("JPCTab", u"Particle ID", None));
    # retranslateUi

