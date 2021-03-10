# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'gcm_tab.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


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
        self.verticalLayout = QVBoxLayout(GCMTab)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.import_gcm = QPushButton(GCMTab)
        self.import_gcm.setObjectName(u"import_gcm")

        self.horizontalLayout_3.addWidget(self.import_gcm)

        self.export_gcm = QPushButton(GCMTab)
        self.export_gcm.setObjectName(u"export_gcm")

        self.horizontalLayout_3.addWidget(self.export_gcm)

        self.import_folder_over_gcm = QPushButton(GCMTab)
        self.import_folder_over_gcm.setObjectName(u"import_folder_over_gcm")

        self.horizontalLayout_3.addWidget(self.import_folder_over_gcm)

        self.export_gcm_folder = QPushButton(GCMTab)
        self.export_gcm_folder.setObjectName(u"export_gcm_folder")

        self.horizontalLayout_3.addWidget(self.export_gcm_folder)

        self.dump_all_gcm_textures = QPushButton(GCMTab)
        self.dump_all_gcm_textures.setObjectName(u"dump_all_gcm_textures")

        self.horizontalLayout_3.addWidget(self.dump_all_gcm_textures)


        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.gcm_files_tree = QTreeWidget(GCMTab)
        self.gcm_files_tree.setObjectName(u"gcm_files_tree")
        self.gcm_files_tree.setEditTriggers(QAbstractItemView.NoEditTriggers)

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
        self.import_gcm.setText(QCoreApplication.translate("GCMTab", u"Import GCM", None))
        self.export_gcm.setText(QCoreApplication.translate("GCMTab", u"Export GCM", None))
        self.import_folder_over_gcm.setText(QCoreApplication.translate("GCMTab", u"Import Folder Over GCM", None))
        self.export_gcm_folder.setText(QCoreApplication.translate("GCMTab", u"Export Folder", None))
        self.dump_all_gcm_textures.setText(QCoreApplication.translate("GCMTab", u"Dump All Textures", None))
        ___qtreewidgetitem = self.gcm_files_tree.headerItem()
        ___qtreewidgetitem.setText(1, QCoreApplication.translate("GCMTab", u"File Size", None));
        ___qtreewidgetitem.setText(0, QCoreApplication.translate("GCMTab", u"File Name", None));
    # retranslateUi

