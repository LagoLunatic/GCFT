# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'rarc_tab.ui'
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


class Ui_RARCTab(object):
    def setupUi(self, RARCTab):
        if not RARCTab.objectName():
            RARCTab.setObjectName(u"RARCTab")
        RARCTab.resize(776, 515)
        self.actionReplaceRARCFile = QAction(RARCTab)
        self.actionReplaceRARCFile.setObjectName(u"actionReplaceRARCFile")
        self.actionExtractRARCFile = QAction(RARCTab)
        self.actionExtractRARCFile.setObjectName(u"actionExtractRARCFile")
        self.actionAddRARCFile = QAction(RARCTab)
        self.actionAddRARCFile.setObjectName(u"actionAddRARCFile")
        self.actionDeleteRARCFile = QAction(RARCTab)
        self.actionDeleteRARCFile.setObjectName(u"actionDeleteRARCFile")
        self.actionOpenRARCImage = QAction(RARCTab)
        self.actionOpenRARCImage.setObjectName(u"actionOpenRARCImage")
        self.actionOpenRARCJ3D = QAction(RARCTab)
        self.actionOpenRARCJ3D.setObjectName(u"actionOpenRARCJ3D")
        self.actionReplaceRARCImage = QAction(RARCTab)
        self.actionReplaceRARCImage.setObjectName(u"actionReplaceRARCImage")
        self.actionAddRARCFolder = QAction(RARCTab)
        self.actionAddRARCFolder.setObjectName(u"actionAddRARCFolder")
        self.actionDeleteRARCFolder = QAction(RARCTab)
        self.actionDeleteRARCFolder.setObjectName(u"actionDeleteRARCFolder")
        self.verticalLayout = QVBoxLayout(RARCTab)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.import_rarc = QPushButton(RARCTab)
        self.import_rarc.setObjectName(u"import_rarc")

        self.horizontalLayout.addWidget(self.import_rarc)

        self.create_rarc = QPushButton(RARCTab)
        self.create_rarc.setObjectName(u"create_rarc")

        self.horizontalLayout.addWidget(self.create_rarc)

        self.create_rarc_from_folder = QPushButton(RARCTab)
        self.create_rarc_from_folder.setObjectName(u"create_rarc_from_folder")

        self.horizontalLayout.addWidget(self.create_rarc_from_folder)

        self.import_folder_over_rarc = QPushButton(RARCTab)
        self.import_folder_over_rarc.setObjectName(u"import_folder_over_rarc")

        self.horizontalLayout.addWidget(self.import_folder_over_rarc)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.export_rarc = QPushButton(RARCTab)
        self.export_rarc.setObjectName(u"export_rarc")

        self.horizontalLayout_7.addWidget(self.export_rarc)

        self.export_rarc_folder = QPushButton(RARCTab)
        self.export_rarc_folder.setObjectName(u"export_rarc_folder")

        self.horizontalLayout_7.addWidget(self.export_rarc_folder)

        self.dump_all_rarc_textures = QPushButton(RARCTab)
        self.dump_all_rarc_textures.setObjectName(u"dump_all_rarc_textures")

        self.horizontalLayout_7.addWidget(self.dump_all_rarc_textures)

        self.export_rarc_to_c_header = QPushButton(RARCTab)
        self.export_rarc_to_c_header.setObjectName(u"export_rarc_to_c_header")

        self.horizontalLayout_7.addWidget(self.export_rarc_to_c_header)


        self.verticalLayout.addLayout(self.horizontalLayout_7)

        self.rarc_files_tree = QTreeWidget(RARCTab)
        self.rarc_files_tree.setObjectName(u"rarc_files_tree")
        self.rarc_files_tree.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.verticalLayout.addWidget(self.rarc_files_tree)


        self.retranslateUi(RARCTab)

        QMetaObject.connectSlotsByName(RARCTab)
    # setupUi

    def retranslateUi(self, RARCTab):
        RARCTab.setWindowTitle(QCoreApplication.translate("RARCTab", u"Form", None))
        self.actionReplaceRARCFile.setText(QCoreApplication.translate("RARCTab", u"Replace File", None))
        self.actionExtractRARCFile.setText(QCoreApplication.translate("RARCTab", u"Extract File", None))
        self.actionAddRARCFile.setText(QCoreApplication.translate("RARCTab", u"Add File", None))
        self.actionDeleteRARCFile.setText(QCoreApplication.translate("RARCTab", u"Delete File", None))
        self.actionOpenRARCImage.setText(QCoreApplication.translate("RARCTab", u"Open Image", None))
        self.actionOpenRARCJ3D.setText(QCoreApplication.translate("RARCTab", u"Open J3D", None))
        self.actionReplaceRARCImage.setText(QCoreApplication.translate("RARCTab", u"Replace Image", None))
        self.actionAddRARCFolder.setText(QCoreApplication.translate("RARCTab", u"Add Folder", None))
        self.actionDeleteRARCFolder.setText(QCoreApplication.translate("RARCTab", u"Delete Folder", None))
        self.import_rarc.setText(QCoreApplication.translate("RARCTab", u"Import RARC", None))
        self.create_rarc.setText(QCoreApplication.translate("RARCTab", u"Create New RARC", None))
        self.create_rarc_from_folder.setText(QCoreApplication.translate("RARCTab", u"Create New RARC From Folder", None))
        self.import_folder_over_rarc.setText(QCoreApplication.translate("RARCTab", u"Import Folder Over RARC", None))
        self.export_rarc.setText(QCoreApplication.translate("RARCTab", u"Export RARC", None))
        self.export_rarc_folder.setText(QCoreApplication.translate("RARCTab", u"Export Folder", None))
        self.dump_all_rarc_textures.setText(QCoreApplication.translate("RARCTab", u"Dump All Textures", None))
        self.export_rarc_to_c_header.setText(QCoreApplication.translate("RARCTab", u"Export File List to C Header", None))
        ___qtreewidgetitem = self.rarc_files_tree.headerItem()
        ___qtreewidgetitem.setText(4, QCoreApplication.translate("RARCTab", u"File Size", None));
        ___qtreewidgetitem.setText(3, QCoreApplication.translate("RARCTab", u"File ID", None));
        ___qtreewidgetitem.setText(2, QCoreApplication.translate("RARCTab", u"File Index", None));
        ___qtreewidgetitem.setText(1, QCoreApplication.translate("RARCTab", u"Folder Type", None));
        ___qtreewidgetitem.setText(0, QCoreApplication.translate("RARCTab", u"File Name", None));
    # retranslateUi

