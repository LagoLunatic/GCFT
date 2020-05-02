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


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 600)
        self.actionReplaceRARCFile = QAction(MainWindow)
        self.actionReplaceRARCFile.setObjectName(u"actionReplaceRARCFile")
        self.actionExtractRARCFile = QAction(MainWindow)
        self.actionExtractRARCFile.setObjectName(u"actionExtractRARCFile")
        self.actionReplaceGCMFile = QAction(MainWindow)
        self.actionReplaceGCMFile.setObjectName(u"actionReplaceGCMFile")
        self.actionExtractGCMFile = QAction(MainWindow)
        self.actionExtractGCMFile.setObjectName(u"actionExtractGCMFile")
        self.actionAddGCMFile = QAction(MainWindow)
        self.actionAddGCMFile.setObjectName(u"actionAddGCMFile")
        self.actionAddRARCFile = QAction(MainWindow)
        self.actionAddRARCFile.setObjectName(u"actionAddRARCFile")
        self.actionDeleteRARCFile = QAction(MainWindow)
        self.actionDeleteRARCFile.setObjectName(u"actionDeleteRARCFile")
        self.actionDeleteGCMFile = QAction(MainWindow)
        self.actionDeleteGCMFile.setObjectName(u"actionDeleteGCMFile")
        self.actionOpenRARCImage = QAction(MainWindow)
        self.actionOpenRARCImage.setObjectName(u"actionOpenRARCImage")
        self.actionOpenJPCImage = QAction(MainWindow)
        self.actionOpenJPCImage.setObjectName(u"actionOpenJPCImage")
        self.actionOpenGCMImage = QAction(MainWindow)
        self.actionOpenGCMImage.setObjectName(u"actionOpenGCMImage")
        self.actionOpenJ3DImage = QAction(MainWindow)
        self.actionOpenJ3DImage.setObjectName(u"actionOpenJ3DImage")
        self.actionOpenRARCJ3D = QAction(MainWindow)
        self.actionOpenRARCJ3D.setObjectName(u"actionOpenRARCJ3D")
        self.actionReplaceJ3DImage = QAction(MainWindow)
        self.actionReplaceJ3DImage.setObjectName(u"actionReplaceJ3DImage")
        self.actionReplaceJPCImage = QAction(MainWindow)
        self.actionReplaceJPCImage.setObjectName(u"actionReplaceJPCImage")
        self.actionReplaceGCMImage = QAction(MainWindow)
        self.actionReplaceGCMImage.setObjectName(u"actionReplaceGCMImage")
        self.actionReplaceRARCImage = QAction(MainWindow)
        self.actionReplaceRARCImage.setObjectName(u"actionReplaceRARCImage")
        self.actionAddRARCFolder = QAction(MainWindow)
        self.actionAddRARCFolder.setObjectName(u"actionAddRARCFolder")
        self.actionDeleteRARCFolder = QAction(MainWindow)
        self.actionDeleteRARCFolder.setObjectName(u"actionDeleteRARCFolder")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tab_3 = QWidget()
        self.tab_3.setObjectName(u"tab_3")
        self.verticalLayout_4 = QVBoxLayout(self.tab_3)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.import_gcm = QPushButton(self.tab_3)
        self.import_gcm.setObjectName(u"import_gcm")

        self.horizontalLayout_3.addWidget(self.import_gcm)

        self.export_gcm = QPushButton(self.tab_3)
        self.export_gcm.setObjectName(u"export_gcm")

        self.horizontalLayout_3.addWidget(self.export_gcm)

        self.import_folder_over_gcm = QPushButton(self.tab_3)
        self.import_folder_over_gcm.setObjectName(u"import_folder_over_gcm")

        self.horizontalLayout_3.addWidget(self.import_folder_over_gcm)

        self.export_gcm_folder = QPushButton(self.tab_3)
        self.export_gcm_folder.setObjectName(u"export_gcm_folder")

        self.horizontalLayout_3.addWidget(self.export_gcm_folder)

        self.dump_all_gcm_textures = QPushButton(self.tab_3)
        self.dump_all_gcm_textures.setObjectName(u"dump_all_gcm_textures")

        self.horizontalLayout_3.addWidget(self.dump_all_gcm_textures)


        self.verticalLayout_4.addLayout(self.horizontalLayout_3)

        self.gcm_files_tree = QTreeWidget(self.tab_3)
        self.gcm_files_tree.setObjectName(u"gcm_files_tree")

        self.verticalLayout_4.addWidget(self.gcm_files_tree)

        self.tabWidget.addTab(self.tab_3, "")
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.verticalLayout_2 = QVBoxLayout(self.tab)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.import_rarc = QPushButton(self.tab)
        self.import_rarc.setObjectName(u"import_rarc")

        self.horizontalLayout.addWidget(self.import_rarc)

        self.create_rarc = QPushButton(self.tab)
        self.create_rarc.setObjectName(u"create_rarc")

        self.horizontalLayout.addWidget(self.create_rarc)

        self.create_rarc_from_folder = QPushButton(self.tab)
        self.create_rarc_from_folder.setObjectName(u"create_rarc_from_folder")

        self.horizontalLayout.addWidget(self.create_rarc_from_folder)

        self.widget = QWidget(self.tab)
        self.widget.setObjectName(u"widget")

        self.horizontalLayout.addWidget(self.widget)


        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.export_rarc = QPushButton(self.tab)
        self.export_rarc.setObjectName(u"export_rarc")

        self.horizontalLayout_7.addWidget(self.export_rarc)

        self.import_folder_over_rarc = QPushButton(self.tab)
        self.import_folder_over_rarc.setObjectName(u"import_folder_over_rarc")

        self.horizontalLayout_7.addWidget(self.import_folder_over_rarc)

        self.export_rarc_folder = QPushButton(self.tab)
        self.export_rarc_folder.setObjectName(u"export_rarc_folder")

        self.horizontalLayout_7.addWidget(self.export_rarc_folder)

        self.dump_all_rarc_textures = QPushButton(self.tab)
        self.dump_all_rarc_textures.setObjectName(u"dump_all_rarc_textures")

        self.horizontalLayout_7.addWidget(self.dump_all_rarc_textures)


        self.verticalLayout_2.addLayout(self.horizontalLayout_7)

        self.rarc_files_tree = QTreeWidget(self.tab)
        self.rarc_files_tree.setObjectName(u"rarc_files_tree")
        self.rarc_files_tree.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.verticalLayout_2.addWidget(self.rarc_files_tree)

        self.tabWidget.addTab(self.tab, "")
        self.tab_5 = QWidget()
        self.tab_5.setObjectName(u"tab_5")
        self.verticalLayout_6 = QVBoxLayout(self.tab_5)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.import_bti = QPushButton(self.tab_5)
        self.import_bti.setObjectName(u"import_bti")

        self.horizontalLayout_5.addWidget(self.import_bti)

        self.export_bti = QPushButton(self.tab_5)
        self.export_bti.setObjectName(u"export_bti")

        self.horizontalLayout_5.addWidget(self.export_bti)

        self.import_bti_image = QPushButton(self.tab_5)
        self.import_bti_image.setObjectName(u"import_bti_image")

        self.horizontalLayout_5.addWidget(self.import_bti_image)

        self.export_bti_image = QPushButton(self.tab_5)
        self.export_bti_image.setObjectName(u"export_bti_image")

        self.horizontalLayout_5.addWidget(self.export_bti_image)


        self.verticalLayout_6.addLayout(self.horizontalLayout_5)

        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.bti_image_container = QWidget(self.tab_5)
        self.bti_image_container.setObjectName(u"bti_image_container")
        self.verticalLayout_12 = QVBoxLayout(self.bti_image_container)
        self.verticalLayout_12.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_12.setObjectName(u"verticalLayout_12")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.bti_image_label = QLabel(self.bti_image_container)
        self.bti_image_label.setObjectName(u"bti_image_label")
        sizePolicy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.bti_image_label.sizePolicy().hasHeightForWidth())
        self.bti_image_label.setSizePolicy(sizePolicy)
        self.bti_image_label.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.bti_image_label, 2, 0, 1, 1)


        self.verticalLayout_12.addLayout(self.gridLayout)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.verticalLayout_12.addItem(self.horizontalSpacer)


        self.horizontalLayout_8.addWidget(self.bti_image_container)

        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setFieldGrowthPolicy(QFormLayout.FieldsStayAtSizeHint)
        self.label_11 = QLabel(self.tab_5)
        self.label_11.setObjectName(u"label_11")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label_11)

        self.label = QLabel(self.tab_5)
        self.label.setObjectName(u"label")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.label)

        self.bti_image_format = QComboBox(self.tab_5)
        self.bti_image_format.setObjectName(u"bti_image_format")
        self.bti_image_format.setMinimumSize(QSize(80, 0))

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.bti_image_format)

        self.label_2 = QLabel(self.tab_5)
        self.label_2.setObjectName(u"label_2")

        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.label_2)

        self.bti_palette_format = QComboBox(self.tab_5)
        self.bti_palette_format.setObjectName(u"bti_palette_format")

        self.formLayout.setWidget(3, QFormLayout.FieldRole, self.bti_palette_format)

        self.label_3 = QLabel(self.tab_5)
        self.label_3.setObjectName(u"label_3")

        self.formLayout.setWidget(4, QFormLayout.LabelRole, self.label_3)

        self.bti_wrap_s = QComboBox(self.tab_5)
        self.bti_wrap_s.setObjectName(u"bti_wrap_s")

        self.formLayout.setWidget(4, QFormLayout.FieldRole, self.bti_wrap_s)

        self.label_4 = QLabel(self.tab_5)
        self.label_4.setObjectName(u"label_4")

        self.formLayout.setWidget(5, QFormLayout.LabelRole, self.label_4)

        self.bti_wrap_t = QComboBox(self.tab_5)
        self.bti_wrap_t.setObjectName(u"bti_wrap_t")

        self.formLayout.setWidget(5, QFormLayout.FieldRole, self.bti_wrap_t)

        self.label_5 = QLabel(self.tab_5)
        self.label_5.setObjectName(u"label_5")

        self.formLayout.setWidget(6, QFormLayout.LabelRole, self.label_5)

        self.bti_min_filter = QComboBox(self.tab_5)
        self.bti_min_filter.setObjectName(u"bti_min_filter")

        self.formLayout.setWidget(6, QFormLayout.FieldRole, self.bti_min_filter)

        self.label_6 = QLabel(self.tab_5)
        self.label_6.setObjectName(u"label_6")

        self.formLayout.setWidget(7, QFormLayout.LabelRole, self.label_6)

        self.bti_mag_filter = QComboBox(self.tab_5)
        self.bti_mag_filter.setObjectName(u"bti_mag_filter")

        self.formLayout.setWidget(7, QFormLayout.FieldRole, self.bti_mag_filter)

        self.label_7 = QLabel(self.tab_5)
        self.label_7.setObjectName(u"label_7")

        self.formLayout.setWidget(8, QFormLayout.LabelRole, self.label_7)

        self.bti_alpha_setting = QLineEdit(self.tab_5)
        self.bti_alpha_setting.setObjectName(u"bti_alpha_setting")
        sizePolicy1 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.bti_alpha_setting.sizePolicy().hasHeightForWidth())
        self.bti_alpha_setting.setSizePolicy(sizePolicy1)
        self.bti_alpha_setting.setMaximumSize(QSize(35, 16777215))

        self.formLayout.setWidget(8, QFormLayout.FieldRole, self.bti_alpha_setting)

        self.label_8 = QLabel(self.tab_5)
        self.label_8.setObjectName(u"label_8")

        self.formLayout.setWidget(9, QFormLayout.LabelRole, self.label_8)

        self.bti_min_lod = QLineEdit(self.tab_5)
        self.bti_min_lod.setObjectName(u"bti_min_lod")
        sizePolicy1.setHeightForWidth(self.bti_min_lod.sizePolicy().hasHeightForWidth())
        self.bti_min_lod.setSizePolicy(sizePolicy1)
        self.bti_min_lod.setMaximumSize(QSize(35, 16777215))

        self.formLayout.setWidget(9, QFormLayout.FieldRole, self.bti_min_lod)

        self.label_9 = QLabel(self.tab_5)
        self.label_9.setObjectName(u"label_9")

        self.formLayout.setWidget(10, QFormLayout.LabelRole, self.label_9)

        self.bti_max_lod = QLineEdit(self.tab_5)
        self.bti_max_lod.setObjectName(u"bti_max_lod")
        sizePolicy1.setHeightForWidth(self.bti_max_lod.sizePolicy().hasHeightForWidth())
        self.bti_max_lod.setSizePolicy(sizePolicy1)
        self.bti_max_lod.setMaximumSize(QSize(35, 16777215))

        self.formLayout.setWidget(10, QFormLayout.FieldRole, self.bti_max_lod)

        self.label_10 = QLabel(self.tab_5)
        self.label_10.setObjectName(u"label_10")

        self.formLayout.setWidget(11, QFormLayout.LabelRole, self.label_10)

        self.bti_lod_bias = QLineEdit(self.tab_5)
        self.bti_lod_bias.setObjectName(u"bti_lod_bias")
        sizePolicy1.setHeightForWidth(self.bti_lod_bias.sizePolicy().hasHeightForWidth())
        self.bti_lod_bias.setSizePolicy(sizePolicy1)
        self.bti_lod_bias.setMaximumSize(QSize(45, 16777215))

        self.formLayout.setWidget(11, QFormLayout.FieldRole, self.bti_lod_bias)

        self.label_12 = QLabel(self.tab_5)
        self.label_12.setObjectName(u"label_12")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.label_12)

        self.bti_file_size = QLabel(self.tab_5)
        self.bti_file_size.setObjectName(u"bti_file_size")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.bti_file_size)

        self.bti_resolution = QLabel(self.tab_5)
        self.bti_resolution.setObjectName(u"bti_resolution")

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.bti_resolution)


        self.horizontalLayout_8.addLayout(self.formLayout)


        self.verticalLayout_6.addLayout(self.horizontalLayout_8)

        self.tabWidget.addTab(self.tab_5, "")
        self.tab_6 = QWidget()
        self.tab_6.setObjectName(u"tab_6")
        self.verticalLayout_7 = QVBoxLayout(self.tab_6)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.import_j3d = QPushButton(self.tab_6)
        self.import_j3d.setObjectName(u"import_j3d")

        self.horizontalLayout_6.addWidget(self.import_j3d)

        self.export_j3d = QPushButton(self.tab_6)
        self.export_j3d.setObjectName(u"export_j3d")

        self.horizontalLayout_6.addWidget(self.export_j3d)


        self.verticalLayout_7.addLayout(self.horizontalLayout_6)

        self.j3d_chunks_tree = QTreeWidget(self.tab_6)
        self.j3d_chunks_tree.setObjectName(u"j3d_chunks_tree")

        self.verticalLayout_7.addWidget(self.j3d_chunks_tree)

        self.tabWidget.addTab(self.tab_6, "")
        self.tab_4 = QWidget()
        self.tab_4.setObjectName(u"tab_4")
        self.verticalLayout_5 = QVBoxLayout(self.tab_4)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.import_jpc = QPushButton(self.tab_4)
        self.import_jpc.setObjectName(u"import_jpc")

        self.horizontalLayout_4.addWidget(self.import_jpc)

        self.export_jpc = QPushButton(self.tab_4)
        self.export_jpc.setObjectName(u"export_jpc")

        self.horizontalLayout_4.addWidget(self.export_jpc)

        self.add_particles_from_folder = QPushButton(self.tab_4)
        self.add_particles_from_folder.setObjectName(u"add_particles_from_folder")

        self.horizontalLayout_4.addWidget(self.add_particles_from_folder)

        self.export_jpc_folder = QPushButton(self.tab_4)
        self.export_jpc_folder.setObjectName(u"export_jpc_folder")

        self.horizontalLayout_4.addWidget(self.export_jpc_folder)


        self.verticalLayout_5.addLayout(self.horizontalLayout_4)

        self.jpc_particles_tree = QTreeWidget(self.tab_4)
        self.jpc_particles_tree.setObjectName(u"jpc_particles_tree")

        self.verticalLayout_5.addWidget(self.jpc_particles_tree)

        self.tabWidget.addTab(self.tab_4, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.verticalLayout_3 = QVBoxLayout(self.tab_2)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.decompress_yaz0 = QPushButton(self.tab_2)
        self.decompress_yaz0.setObjectName(u"decompress_yaz0")

        self.horizontalLayout_2.addWidget(self.decompress_yaz0)

        self.compress_yaz0 = QPushButton(self.tab_2)
        self.compress_yaz0.setObjectName(u"compress_yaz0")

        self.horizontalLayout_2.addWidget(self.compress_yaz0)


        self.verticalLayout_3.addLayout(self.horizontalLayout_2)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer)

        self.tabWidget.addTab(self.tab_2, "")

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
        self.actionReplaceRARCFile.setText(QCoreApplication.translate("MainWindow", u"Replace File", None))
        self.actionExtractRARCFile.setText(QCoreApplication.translate("MainWindow", u"Extract File", None))
        self.actionReplaceGCMFile.setText(QCoreApplication.translate("MainWindow", u"Replace File", None))
        self.actionExtractGCMFile.setText(QCoreApplication.translate("MainWindow", u"Extract File", None))
        self.actionAddGCMFile.setText(QCoreApplication.translate("MainWindow", u"Add File", None))
        self.actionAddRARCFile.setText(QCoreApplication.translate("MainWindow", u"Add File", None))
        self.actionDeleteRARCFile.setText(QCoreApplication.translate("MainWindow", u"Delete File", None))
        self.actionDeleteGCMFile.setText(QCoreApplication.translate("MainWindow", u"Delete File", None))
        self.actionOpenRARCImage.setText(QCoreApplication.translate("MainWindow", u"Open Image", None))
        self.actionOpenJPCImage.setText(QCoreApplication.translate("MainWindow", u"Open Image", None))
        self.actionOpenGCMImage.setText(QCoreApplication.translate("MainWindow", u"Open Image", None))
        self.actionOpenJ3DImage.setText(QCoreApplication.translate("MainWindow", u"Open Image", None))
        self.actionOpenRARCJ3D.setText(QCoreApplication.translate("MainWindow", u"Open J3D", None))
        self.actionReplaceJ3DImage.setText(QCoreApplication.translate("MainWindow", u"Replace Image", None))
        self.actionReplaceJPCImage.setText(QCoreApplication.translate("MainWindow", u"Replace Image", None))
        self.actionReplaceGCMImage.setText(QCoreApplication.translate("MainWindow", u"Replace Image", None))
        self.actionReplaceRARCImage.setText(QCoreApplication.translate("MainWindow", u"Replace Image", None))
        self.actionAddRARCFolder.setText(QCoreApplication.translate("MainWindow", u"Add Folder", None))
        self.actionDeleteRARCFolder.setText(QCoreApplication.translate("MainWindow", u"Delete Folder", None))
        self.import_gcm.setText(QCoreApplication.translate("MainWindow", u"Import GCM", None))
        self.export_gcm.setText(QCoreApplication.translate("MainWindow", u"Export GCM", None))
        self.import_folder_over_gcm.setText(QCoreApplication.translate("MainWindow", u"Import Folder Over GCM", None))
        self.export_gcm_folder.setText(QCoreApplication.translate("MainWindow", u"Export Folder", None))
        self.dump_all_gcm_textures.setText(QCoreApplication.translate("MainWindow", u"Dump All Textures", None))
        ___qtreewidgetitem = self.gcm_files_tree.headerItem()
        ___qtreewidgetitem.setText(1, QCoreApplication.translate("MainWindow", u"File Size", None));
        ___qtreewidgetitem.setText(0, QCoreApplication.translate("MainWindow", u"File Name", None));
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), QCoreApplication.translate("MainWindow", u"GCM ISOs", None))
        self.import_rarc.setText(QCoreApplication.translate("MainWindow", u"Import RARC", None))
        self.create_rarc.setText(QCoreApplication.translate("MainWindow", u"Create New RARC", None))
        self.create_rarc_from_folder.setText(QCoreApplication.translate("MainWindow", u"Create New RARC From Folder", None))
        self.export_rarc.setText(QCoreApplication.translate("MainWindow", u"Export RARC", None))
        self.import_folder_over_rarc.setText(QCoreApplication.translate("MainWindow", u"Import Folder Over RARC", None))
        self.export_rarc_folder.setText(QCoreApplication.translate("MainWindow", u"Export Folder", None))
        self.dump_all_rarc_textures.setText(QCoreApplication.translate("MainWindow", u"Dump All Textures", None))
        ___qtreewidgetitem1 = self.rarc_files_tree.headerItem()
        ___qtreewidgetitem1.setText(4, QCoreApplication.translate("MainWindow", u"File Size", None));
        ___qtreewidgetitem1.setText(3, QCoreApplication.translate("MainWindow", u"File ID", None));
        ___qtreewidgetitem1.setText(2, QCoreApplication.translate("MainWindow", u"File Index", None));
        ___qtreewidgetitem1.setText(1, QCoreApplication.translate("MainWindow", u"Folder Type", None));
        ___qtreewidgetitem1.setText(0, QCoreApplication.translate("MainWindow", u"File Name", None));
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("MainWindow", u"RARC Archives", None))
        self.import_bti.setText(QCoreApplication.translate("MainWindow", u"Import BTI", None))
        self.export_bti.setText(QCoreApplication.translate("MainWindow", u"Export BTI", None))
        self.import_bti_image.setText(QCoreApplication.translate("MainWindow", u"Import Image", None))
        self.export_bti_image.setText(QCoreApplication.translate("MainWindow", u"Export Image", None))
        self.bti_image_label.setText("")
        self.label_11.setText(QCoreApplication.translate("MainWindow", u"File Size", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Image Format", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Palette Format", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Wrap X", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Wrap Y", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"Min Filter", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"Mag Filter", None))
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"Alpha Setting", None))
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"Min LOD", None))
        self.label_9.setText(QCoreApplication.translate("MainWindow", u"Max LOD", None))
        self.label_10.setText(QCoreApplication.translate("MainWindow", u"LOD Bias", None))
        self.label_12.setText(QCoreApplication.translate("MainWindow", u"Resolution", None))
        self.bti_file_size.setText(QCoreApplication.translate("MainWindow", u"123", None))
        self.bti_resolution.setText(QCoreApplication.translate("MainWindow", u"123x123", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_5), QCoreApplication.translate("MainWindow", u"BTI Images", None))
        self.import_j3d.setText(QCoreApplication.translate("MainWindow", u"Import J3D File", None))
        self.export_j3d.setText(QCoreApplication.translate("MainWindow", u"Export J3D File", None))
        ___qtreewidgetitem2 = self.j3d_chunks_tree.headerItem()
        ___qtreewidgetitem2.setText(2, QCoreApplication.translate("MainWindow", u"Size", None));
        ___qtreewidgetitem2.setText(1, QCoreApplication.translate("MainWindow", u"Texture Name", None));
        ___qtreewidgetitem2.setText(0, QCoreApplication.translate("MainWindow", u"Chunk Type", None));
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_6), QCoreApplication.translate("MainWindow", u"J3D Files", None))
        self.import_jpc.setText(QCoreApplication.translate("MainWindow", u"Import JPC", None))
        self.export_jpc.setText(QCoreApplication.translate("MainWindow", u"Export JPC", None))
        self.add_particles_from_folder.setText(QCoreApplication.translate("MainWindow", u"Add Particles From Folder", None))
        self.export_jpc_folder.setText(QCoreApplication.translate("MainWindow", u"Export Folder", None))
        ___qtreewidgetitem3 = self.jpc_particles_tree.headerItem()
        ___qtreewidgetitem3.setText(1, QCoreApplication.translate("MainWindow", u"Texture Name", None));
        ___qtreewidgetitem3.setText(0, QCoreApplication.translate("MainWindow", u"Particle ID", None));
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_4), QCoreApplication.translate("MainWindow", u"JPC Particle Archives", None))
        self.decompress_yaz0.setText(QCoreApplication.translate("MainWindow", u"Decompress File", None))
        self.compress_yaz0.setText(QCoreApplication.translate("MainWindow", u"Compress File", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QCoreApplication.translate("MainWindow", u"Yaz0 Compression", None))
    # retranslateUi

