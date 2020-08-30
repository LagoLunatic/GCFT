# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main.ui'
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

from gcft_ui.gcm_tab import GCMTab
from gcft_ui.rarc_tab import RARCTab
from gcft_ui.bti_tab import BTITab
from gcft_ui.j3d_tab import J3DTab
from gcft_ui.jpc_tab import JPCTab
from gcft_ui.dol_tab import DOLTab
from gcft_ui.yaz0_tab import Yaz0Tab


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.gcm_tab = GCMTab()
        self.gcm_tab.setObjectName(u"gcm_tab")
        self.tabWidget.addTab(self.gcm_tab, "")
        self.rarc_tab = RARCTab()
        self.rarc_tab.setObjectName(u"rarc_tab")
        self.tabWidget.addTab(self.rarc_tab, "")
        self.bti_tab = BTITab()
        self.bti_tab.setObjectName(u"bti_tab")
        self.tabWidget.addTab(self.bti_tab, "")
        self.j3d_tab = J3DTab()
        self.j3d_tab.setObjectName(u"j3d_tab")
        self.tabWidget.addTab(self.j3d_tab, "")
        self.jpc_tab = JPCTab()
        self.jpc_tab.setObjectName(u"jpc_tab")
        self.tabWidget.addTab(self.jpc_tab, "")
        self.dol_tab = DOLTab()
        self.dol_tab.setObjectName(u"dol_tab")
        self.tabWidget.addTab(self.dol_tab, "")
        self.yaz0_tab = Yaz0Tab()
        self.yaz0_tab.setObjectName(u"yaz0_tab")
        self.tabWidget.addTab(self.yaz0_tab, "")

        self.verticalLayout.addWidget(self.tabWidget)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 21))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"GameCube File Tools", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.gcm_tab), QCoreApplication.translate("MainWindow", u"GCM ISOs", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.rarc_tab), QCoreApplication.translate("MainWindow", u"RARC Archives", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.bti_tab), QCoreApplication.translate("MainWindow", u"BTI Images", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.j3d_tab), QCoreApplication.translate("MainWindow", u"J3D Files", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.jpc_tab), QCoreApplication.translate("MainWindow", u"JPC Particle Archives", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.dol_tab), QCoreApplication.translate("MainWindow", u"DOL Executables", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.yaz0_tab), QCoreApplication.translate("MainWindow", u"Yaz0 Compression", None))
    # retranslateUi

