# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main.ui',
# licensing of 'main.ui' applies.
#
# Created: Wed Jan  8 09:46:12 2020
#      by: pyside2-uic  running on PySide2 5.11.2
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.tab)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.import_rarc = QtWidgets.QPushButton(self.tab)
        self.import_rarc.setObjectName("import_rarc")
        self.horizontalLayout.addWidget(self.import_rarc)
        self.export_rarc = QtWidgets.QPushButton(self.tab)
        self.export_rarc.setObjectName("export_rarc")
        self.horizontalLayout.addWidget(self.export_rarc)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.rarc_files_tree = QtWidgets.QTreeWidget(self.tab)
        self.rarc_files_tree.setObjectName("rarc_files_tree")
        self.verticalLayout_2.addWidget(self.rarc_files_tree)
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.tab_2)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.decompress_yaz0 = QtWidgets.QPushButton(self.tab_2)
        self.decompress_yaz0.setObjectName("decompress_yaz0")
        self.horizontalLayout_2.addWidget(self.decompress_yaz0)
        self.compress_yaz0 = QtWidgets.QPushButton(self.tab_2)
        self.compress_yaz0.setObjectName("compress_yaz0")
        self.horizontalLayout_2.addWidget(self.compress_yaz0)
        self.verticalLayout_3.addLayout(self.horizontalLayout_2)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem)
        self.tabWidget.addTab(self.tab_2, "")
        self.tab_3 = QtWidgets.QWidget()
        self.tab_3.setObjectName("tab_3")
        self.tabWidget.addTab(self.tab_3, "")
        self.verticalLayout.addWidget(self.tabWidget)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionReplaceRARCFile = QtWidgets.QAction(MainWindow)
        self.actionReplaceRARCFile.setObjectName("actionReplaceRARCFile")
        self.actionExtractRARCFile = QtWidgets.QAction(MainWindow)
        self.actionExtractRARCFile.setObjectName("actionExtractRARCFile")

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtWidgets.QApplication.translate("MainWindow", "GameCube File Tools", None, -1))
        self.import_rarc.setText(QtWidgets.QApplication.translate("MainWindow", "Import RARC", None, -1))
        self.export_rarc.setText(QtWidgets.QApplication.translate("MainWindow", "Export RARC", None, -1))
        self.rarc_files_tree.headerItem().setText(0, QtWidgets.QApplication.translate("MainWindow", "File Name", None, -1))
        self.rarc_files_tree.headerItem().setText(1, QtWidgets.QApplication.translate("MainWindow", "File ID", None, -1))
        self.rarc_files_tree.headerItem().setText(2, QtWidgets.QApplication.translate("MainWindow", "File Size", None, -1))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QtWidgets.QApplication.translate("MainWindow", "RARC Archives", None, -1))
        self.decompress_yaz0.setText(QtWidgets.QApplication.translate("MainWindow", "Decompress File", None, -1))
        self.compress_yaz0.setText(QtWidgets.QApplication.translate("MainWindow", "Compress File", None, -1))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QtWidgets.QApplication.translate("MainWindow", "Yaz0 Compression", None, -1))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), QtWidgets.QApplication.translate("MainWindow", "GCM ISOs", None, -1))
        self.actionReplaceRARCFile.setText(QtWidgets.QApplication.translate("MainWindow", "Replace File", None, -1))
        self.actionExtractRARCFile.setText(QtWidgets.QApplication.translate("MainWindow", "Extract File", None, -1))

