# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'jpc_tab.ui'
##
## Created by: Qt User Interface Compiler version 6.5.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QHeaderView, QLabel,
    QLineEdit, QPushButton, QScrollArea, QSizePolicy,
    QTreeView, QVBoxLayout, QWidget)

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

        self.filter = QLineEdit(JPCTab)
        self.filter.setObjectName(u"filter")

        self.verticalLayout.addWidget(self.filter)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.jpc_particles_tree = QTreeView(JPCTab)
        self.jpc_particles_tree.setObjectName(u"jpc_particles_tree")

        self.horizontalLayout.addWidget(self.jpc_particles_tree)

        self.jpc_sidebar = QWidget(JPCTab)
        self.jpc_sidebar.setObjectName(u"jpc_sidebar")
        self.jpc_sidebar.setMaximumSize(QSize(300, 16777215))
        self.verticalLayout_3 = QVBoxLayout(self.jpc_sidebar)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.jpc_sidebar_label = QLabel(self.jpc_sidebar)
        self.jpc_sidebar_label.setObjectName(u"jpc_sidebar_label")

        self.verticalLayout_3.addWidget(self.jpc_sidebar_label)

        self.scrollArea = QScrollArea(self.jpc_sidebar)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 298, 411))
        self.verticalLayout_2 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout_3.addWidget(self.scrollArea)


        self.horizontalLayout.addWidget(self.jpc_sidebar)


        self.verticalLayout.addLayout(self.horizontalLayout)


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
        self.filter.setPlaceholderText(QCoreApplication.translate("JPCTab", u"Filter", None))
        self.jpc_sidebar_label.setText(QCoreApplication.translate("JPCTab", u"Extra information will be displayed here as necessary.", None))
    # retranslateUi

