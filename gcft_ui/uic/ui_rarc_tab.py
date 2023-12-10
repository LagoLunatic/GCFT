# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'rarc_tab.ui'
##
## Created by: Qt User Interface Compiler version 6.6.1
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QHBoxLayout, QHeaderView,
    QPushButton, QSizePolicy, QTreeWidget, QTreeWidgetItem,
    QVBoxLayout, QWidget)

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
        self.actionReplaceRARCJ3D = QAction(RARCTab)
        self.actionReplaceRARCJ3D.setObjectName(u"actionReplaceRARCJ3D")
        self.actionExtractAllFilesFromRARCFolder = QAction(RARCTab)
        self.actionExtractAllFilesFromRARCFolder.setObjectName(u"actionExtractAllFilesFromRARCFolder")
        self.actionReplaceAllFilesInRARCFolder = QAction(RARCTab)
        self.actionReplaceAllFilesInRARCFolder.setObjectName(u"actionReplaceAllFilesInRARCFolder")
        self.actionLoadJ3DAnim = QAction(RARCTab)
        self.actionLoadJ3DAnim.setObjectName(u"actionLoadJ3DAnim")
        self.actionLoadJ3DAnim.setMenuRole(QAction.NoRole)
        self.verticalLayout = QVBoxLayout(RARCTab)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.import_rarc = QPushButton(RARCTab)
        self.import_rarc.setObjectName(u"import_rarc")

        self.horizontalLayout.addWidget(self.import_rarc)

        self.replace_all_files_in_rarc = QPushButton(RARCTab)
        self.replace_all_files_in_rarc.setObjectName(u"replace_all_files_in_rarc")

        self.horizontalLayout.addWidget(self.replace_all_files_in_rarc)

        self.create_rarc = QPushButton(RARCTab)
        self.create_rarc.setObjectName(u"create_rarc")

        self.horizontalLayout.addWidget(self.create_rarc)

        self.create_rarc_from_folder = QPushButton(RARCTab)
        self.create_rarc_from_folder.setObjectName(u"create_rarc_from_folder")

        self.horizontalLayout.addWidget(self.create_rarc_from_folder)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.export_rarc = QPushButton(RARCTab)
        self.export_rarc.setObjectName(u"export_rarc")

        self.horizontalLayout_7.addWidget(self.export_rarc)

        self.extract_all_files_from_rarc = QPushButton(RARCTab)
        self.extract_all_files_from_rarc.setObjectName(u"extract_all_files_from_rarc")

        self.horizontalLayout_7.addWidget(self.extract_all_files_from_rarc)

        self.dump_all_rarc_textures = QPushButton(RARCTab)
        self.dump_all_rarc_textures.setObjectName(u"dump_all_rarc_textures")

        self.horizontalLayout_7.addWidget(self.dump_all_rarc_textures)

        self.export_rarc_to_c_header = QPushButton(RARCTab)
        self.export_rarc_to_c_header.setObjectName(u"export_rarc_to_c_header")

        self.horizontalLayout_7.addWidget(self.export_rarc_to_c_header)


        self.verticalLayout.addLayout(self.horizontalLayout_7)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.sync_file_ids_and_indexes = QCheckBox(RARCTab)
        self.sync_file_ids_and_indexes.setObjectName(u"sync_file_ids_and_indexes")
        self.sync_file_ids_and_indexes.setChecked(True)

        self.horizontalLayout_2.addWidget(self.sync_file_ids_and_indexes)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.rarc_files_tree = QTreeWidget(RARCTab)
        self.rarc_files_tree.setObjectName(u"rarc_files_tree")

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
        self.actionReplaceRARCJ3D.setText(QCoreApplication.translate("RARCTab", u"Replace J3D", None))
        self.actionExtractAllFilesFromRARCFolder.setText(QCoreApplication.translate("RARCTab", u"Extract All Files From Folder", None))
        self.actionReplaceAllFilesInRARCFolder.setText(QCoreApplication.translate("RARCTab", u"Replace All Files in Folder", None))
        self.actionLoadJ3DAnim.setText(QCoreApplication.translate("RARCTab", u"Load J3D Animation", None))
        self.import_rarc.setText(QCoreApplication.translate("RARCTab", u"Import RARC", None))
        self.replace_all_files_in_rarc.setText(QCoreApplication.translate("RARCTab", u"Replace All Files in RARC", None))
        self.create_rarc.setText(QCoreApplication.translate("RARCTab", u"Create New RARC", None))
        self.create_rarc_from_folder.setText(QCoreApplication.translate("RARCTab", u"Create New RARC From Folder", None))
        self.export_rarc.setText(QCoreApplication.translate("RARCTab", u"Export RARC", None))
        self.extract_all_files_from_rarc.setText(QCoreApplication.translate("RARCTab", u"Extract All Files From RARC", None))
        self.dump_all_rarc_textures.setText(QCoreApplication.translate("RARCTab", u"Dump All Textures", None))
        self.export_rarc_to_c_header.setText(QCoreApplication.translate("RARCTab", u"Export File List to C Header", None))
        self.sync_file_ids_and_indexes.setText(QCoreApplication.translate("RARCTab", u"Sync File IDs and Indexes", None))
        ___qtreewidgetitem = self.rarc_files_tree.headerItem()
        ___qtreewidgetitem.setText(5, QCoreApplication.translate("RARCTab", u"Yaz0 Compressed", None));
        ___qtreewidgetitem.setText(4, QCoreApplication.translate("RARCTab", u"File Size", None));
        ___qtreewidgetitem.setText(3, QCoreApplication.translate("RARCTab", u"File ID", None));
        ___qtreewidgetitem.setText(2, QCoreApplication.translate("RARCTab", u"File Index", None));
        ___qtreewidgetitem.setText(1, QCoreApplication.translate("RARCTab", u"Folder Type", None));
        ___qtreewidgetitem.setText(0, QCoreApplication.translate("RARCTab", u"File Name", None));
    # retranslateUi

