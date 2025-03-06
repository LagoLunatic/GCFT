# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'gcm_tab.ui'
##
## Created by: Qt User Interface Compiler version 6.8.2
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QHBoxLayout, QHeaderView,
    QLineEdit, QPushButton, QSizePolicy, QTreeView,
    QVBoxLayout, QWidget)

class Ui_GCMTab(object):
    def setupUi(self, GCMTab):
        if not GCMTab.objectName():
            GCMTab.setObjectName(u"GCMTab")
        GCMTab.resize(776, 515)
        self.actionReplaceGCMFile = QAction(GCMTab)
        self.actionReplaceGCMFile.setObjectName(u"actionReplaceGCMFile")
        self.actionExtractGCMFile = QAction(GCMTab)
        self.actionExtractGCMFile.setObjectName(u"actionExtractGCMFile")
        self.actionAddGCMFile = QAction(GCMTab)
        self.actionAddGCMFile.setObjectName(u"actionAddGCMFile")
        self.actionDeleteGCMFile = QAction(GCMTab)
        self.actionDeleteGCMFile.setObjectName(u"actionDeleteGCMFile")
        self.actionOpenGCMImage = QAction(GCMTab)
        self.actionOpenGCMImage.setObjectName(u"actionOpenGCMImage")
        self.actionReplaceGCMImage = QAction(GCMTab)
        self.actionReplaceGCMImage.setObjectName(u"actionReplaceGCMImage")
        self.actionReplaceGCMDOL = QAction(GCMTab)
        self.actionReplaceGCMDOL.setObjectName(u"actionReplaceGCMDOL")
        self.actionOpenGCMDOL = QAction(GCMTab)
        self.actionOpenGCMDOL.setObjectName(u"actionOpenGCMDOL")
        self.actionReplaceGCMJPC = QAction(GCMTab)
        self.actionReplaceGCMJPC.setObjectName(u"actionReplaceGCMJPC")
        self.actionOpenGCMJPC = QAction(GCMTab)
        self.actionOpenGCMJPC.setObjectName(u"actionOpenGCMJPC")
        self.actionReplaceGCMRARC = QAction(GCMTab)
        self.actionReplaceGCMRARC.setObjectName(u"actionReplaceGCMRARC")
        self.actionOpenGCMRARC = QAction(GCMTab)
        self.actionOpenGCMRARC.setObjectName(u"actionOpenGCMRARC")
        self.actionAddGCMFolder = QAction(GCMTab)
        self.actionAddGCMFolder.setObjectName(u"actionAddGCMFolder")
        self.actionDeleteGCMFolder = QAction(GCMTab)
        self.actionDeleteGCMFolder.setObjectName(u"actionDeleteGCMFolder")
        self.actionExtractAllFilesFromGCMFolder = QAction(GCMTab)
        self.actionExtractAllFilesFromGCMFolder.setObjectName(u"actionExtractAllFilesFromGCMFolder")
        self.actionExtractAllFilesFromGCMFolder.setMenuRole(QAction.NoRole)
        self.actionReplaceAllFilesInGCMFolder = QAction(GCMTab)
        self.actionReplaceAllFilesInGCMFolder.setObjectName(u"actionReplaceAllFilesInGCMFolder")
        self.actionReplaceAllFilesInGCMFolder.setMenuRole(QAction.NoRole)
        self.actionAddReplaceFilesForFolder = QAction(GCMTab)
        self.actionAddReplaceFilesForFolder.setObjectName(u"actionAddReplaceFilesForFolder")
        self.actionAddReplaceFilesForFolder.setMenuRole(QAction.NoRole)
        self.actionOpenGCMJ3D = QAction(GCMTab)
        self.actionOpenGCMJ3D.setObjectName(u"actionOpenGCMJ3D")
        self.actionReplaceGCMJ3D = QAction(GCMTab)
        self.actionReplaceGCMJ3D.setObjectName(u"actionReplaceGCMJ3D")
        self.actionLoadJ3DAnim = QAction(GCMTab)
        self.actionLoadJ3DAnim.setObjectName(u"actionLoadJ3DAnim")
        self.verticalLayout = QVBoxLayout(GCMTab)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.import_gcm = QPushButton(GCMTab)
        self.import_gcm.setObjectName(u"import_gcm")

        self.horizontalLayout_3.addWidget(self.import_gcm)

        self.replace_all_files_in_gcm = QPushButton(GCMTab)
        self.replace_all_files_in_gcm.setObjectName(u"replace_all_files_in_gcm")

        self.horizontalLayout_3.addWidget(self.replace_all_files_in_gcm)

        self.add_replace_files_from_folder = QPushButton(GCMTab)
        self.add_replace_files_from_folder.setObjectName(u"add_replace_files_from_folder")

        self.horizontalLayout_3.addWidget(self.add_replace_files_from_folder)


        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.export_gcm = QPushButton(GCMTab)
        self.export_gcm.setObjectName(u"export_gcm")

        self.horizontalLayout.addWidget(self.export_gcm)

        self.extract_all_files_from_gcm = QPushButton(GCMTab)
        self.extract_all_files_from_gcm.setObjectName(u"extract_all_files_from_gcm")

        self.horizontalLayout.addWidget(self.extract_all_files_from_gcm)

        self.dump_all_gcm_textures = QPushButton(GCMTab)
        self.dump_all_gcm_textures.setObjectName(u"dump_all_gcm_textures")

        self.horizontalLayout.addWidget(self.dump_all_gcm_textures)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.filter = QLineEdit(GCMTab)
        self.filter.setObjectName(u"filter")

        self.verticalLayout.addWidget(self.filter)

        self.gcm_files_tree = QTreeView(GCMTab)
        self.gcm_files_tree.setObjectName(u"gcm_files_tree")
        self.gcm_files_tree.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.verticalLayout.addWidget(self.gcm_files_tree)


        self.retranslateUi(GCMTab)

        QMetaObject.connectSlotsByName(GCMTab)
    # setupUi

    def retranslateUi(self, GCMTab):
        GCMTab.setWindowTitle(QCoreApplication.translate("GCMTab", u"Form", None))
        self.actionReplaceGCMFile.setText(QCoreApplication.translate("GCMTab", u"Replace File", None))
        self.actionExtractGCMFile.setText(QCoreApplication.translate("GCMTab", u"Extract File", None))
        self.actionAddGCMFile.setText(QCoreApplication.translate("GCMTab", u"Add File", None))
        self.actionDeleteGCMFile.setText(QCoreApplication.translate("GCMTab", u"Delete File", None))
        self.actionOpenGCMImage.setText(QCoreApplication.translate("GCMTab", u"Open Image", None))
        self.actionReplaceGCMImage.setText(QCoreApplication.translate("GCMTab", u"Replace Image", None))
        self.actionReplaceGCMDOL.setText(QCoreApplication.translate("GCMTab", u"Replace DOL", None))
        self.actionOpenGCMDOL.setText(QCoreApplication.translate("GCMTab", u"Open DOL", None))
        self.actionReplaceGCMJPC.setText(QCoreApplication.translate("GCMTab", u"Replace JPC", None))
        self.actionOpenGCMJPC.setText(QCoreApplication.translate("GCMTab", u"Open JPC", None))
        self.actionReplaceGCMRARC.setText(QCoreApplication.translate("GCMTab", u"Replace RARC", None))
        self.actionOpenGCMRARC.setText(QCoreApplication.translate("GCMTab", u"Open RARC", None))
        self.actionAddGCMFolder.setText(QCoreApplication.translate("GCMTab", u"Add Folder", None))
        self.actionDeleteGCMFolder.setText(QCoreApplication.translate("GCMTab", u"Delete Folder", None))
        self.actionExtractAllFilesFromGCMFolder.setText(QCoreApplication.translate("GCMTab", u"Extract All Files From Folder", None))
        self.actionReplaceAllFilesInGCMFolder.setText(QCoreApplication.translate("GCMTab", u"Replace All Files in Folder", None))
        self.actionAddReplaceFilesForFolder.setText(QCoreApplication.translate("GCMTab", u"Add/Replace Files For Folder", None))
        self.actionOpenGCMJ3D.setText(QCoreApplication.translate("GCMTab", u"Open J3D", None))
        self.actionReplaceGCMJ3D.setText(QCoreApplication.translate("GCMTab", u"Replace J3D", None))
        self.actionLoadJ3DAnim.setText(QCoreApplication.translate("GCMTab", u"Load J3D Animation", None))
        self.import_gcm.setText(QCoreApplication.translate("GCMTab", u"Import GCM", None))
        self.replace_all_files_in_gcm.setText(QCoreApplication.translate("GCMTab", u"Replace All Files in GCM", None))
        self.add_replace_files_from_folder.setText(QCoreApplication.translate("GCMTab", u"Add/Replace Files From Folder", None))
        self.export_gcm.setText(QCoreApplication.translate("GCMTab", u"Export GCM", None))
        self.extract_all_files_from_gcm.setText(QCoreApplication.translate("GCMTab", u"Extract All Files From GCM", None))
        self.dump_all_gcm_textures.setText(QCoreApplication.translate("GCMTab", u"Dump All Textures", None))
        self.filter.setPlaceholderText(QCoreApplication.translate("GCMTab", u"Filter", None))
    # retranslateUi

