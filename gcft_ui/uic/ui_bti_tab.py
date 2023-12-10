# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'bti_tab.ui'
##
## Created by: Qt User Interface Compiler version 6.6.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QFormLayout, QFrame,
    QGridLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QScrollArea, QSizePolicy, QVBoxLayout,
    QWidget)

class Ui_BTITab(object):
    def setupUi(self, BTITab):
        if not BTITab.objectName():
            BTITab.setObjectName(u"BTITab")
        BTITab.resize(776, 515)
        self.verticalLayout = QVBoxLayout(BTITab)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.import_bti = QPushButton(BTITab)
        self.import_bti.setObjectName(u"import_bti")

        self.horizontalLayout_5.addWidget(self.import_bti)

        self.import_bti_image = QPushButton(BTITab)
        self.import_bti_image.setObjectName(u"import_bti_image")

        self.horizontalLayout_5.addWidget(self.import_bti_image)

        self.replace_bti_mipmap = QPushButton(BTITab)
        self.replace_bti_mipmap.setObjectName(u"replace_bti_mipmap")

        self.horizontalLayout_5.addWidget(self.replace_bti_mipmap)

        self.import_bti_from_bnr = QPushButton(BTITab)
        self.import_bti_from_bnr.setObjectName(u"import_bti_from_bnr")

        self.horizontalLayout_5.addWidget(self.import_bti_from_bnr)


        self.verticalLayout.addLayout(self.horizontalLayout_5)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.export_bti = QPushButton(BTITab)
        self.export_bti.setObjectName(u"export_bti")

        self.horizontalLayout.addWidget(self.export_bti)

        self.export_bti_image = QPushButton(BTITab)
        self.export_bti_image.setObjectName(u"export_bti_image")

        self.horizontalLayout.addWidget(self.export_bti_image)

        self.widget = QWidget(BTITab)
        self.widget.setObjectName(u"widget")

        self.horizontalLayout.addWidget(self.widget)

        self.widget_2 = QWidget(BTITab)
        self.widget_2.setObjectName(u"widget_2")

        self.horizontalLayout.addWidget(self.widget_2)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.bti_image_container = QWidget(BTITab)
        self.bti_image_container.setObjectName(u"bti_image_container")
        self.verticalLayout_12 = QVBoxLayout(self.bti_image_container)
        self.verticalLayout_12.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_12.setObjectName(u"verticalLayout_12")
        self.bti_image_scroll_area = QScrollArea(self.bti_image_container)
        self.bti_image_scroll_area.setObjectName(u"bti_image_scroll_area")
        palette = QPalette()
        brush = QBrush(QColor(255, 255, 255, 255))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Base, brush)
        brush1 = QBrush(QColor(255, 255, 255, 0))
        brush1.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Window, brush1)
        palette.setBrush(QPalette.Inactive, QPalette.Base, brush)
        palette.setBrush(QPalette.Inactive, QPalette.Window, brush1)
        palette.setBrush(QPalette.Disabled, QPalette.Base, brush1)
        palette.setBrush(QPalette.Disabled, QPalette.Window, brush1)
        self.bti_image_scroll_area.setPalette(palette)
        self.bti_image_scroll_area.setFrameShape(QFrame.NoFrame)
        self.bti_image_scroll_area.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 550, 431))
        self.gridLayout = QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout.setObjectName(u"gridLayout")
        self.bti_image_label = QLabel(self.scrollAreaWidgetContents)
        self.bti_image_label.setObjectName(u"bti_image_label")
        sizePolicy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.bti_image_label.sizePolicy().hasHeightForWidth())
        self.bti_image_label.setSizePolicy(sizePolicy)
        self.bti_image_label.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.bti_image_label, 0, 0, 1, 1)

        self.bti_image_scroll_area.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout_12.addWidget(self.bti_image_scroll_area)


        self.horizontalLayout_8.addWidget(self.bti_image_container)

        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setFieldGrowthPolicy(QFormLayout.FieldsStayAtSizeHint)
        self.label_11 = QLabel(BTITab)
        self.label_11.setObjectName(u"label_11")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label_11)

        self.bti_file_size = QLabel(BTITab)
        self.bti_file_size.setObjectName(u"bti_file_size")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.bti_file_size)

        self.label_12 = QLabel(BTITab)
        self.label_12.setObjectName(u"label_12")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.label_12)

        self.bti_resolution = QLabel(BTITab)
        self.bti_resolution.setObjectName(u"bti_resolution")

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.bti_resolution)

        self.label_13 = QLabel(BTITab)
        self.label_13.setObjectName(u"label_13")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.label_13)

        self.bti_num_colors = QLabel(BTITab)
        self.bti_num_colors.setObjectName(u"bti_num_colors")

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.bti_num_colors)

        self.label_15 = QLabel(BTITab)
        self.label_15.setObjectName(u"label_15")

        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.label_15)

        self.bti_max_colors = QLabel(BTITab)
        self.bti_max_colors.setObjectName(u"bti_max_colors")

        self.formLayout.setWidget(3, QFormLayout.FieldRole, self.bti_max_colors)

        self.label = QLabel(BTITab)
        self.label.setObjectName(u"label")

        self.formLayout.setWidget(4, QFormLayout.LabelRole, self.label)

        self.bti_image_format = QComboBox(BTITab)
        self.bti_image_format.setObjectName(u"bti_image_format")
        self.bti_image_format.setMinimumSize(QSize(80, 0))

        self.formLayout.setWidget(4, QFormLayout.FieldRole, self.bti_image_format)

        self.label_2 = QLabel(BTITab)
        self.label_2.setObjectName(u"label_2")

        self.formLayout.setWidget(5, QFormLayout.LabelRole, self.label_2)

        self.bti_palette_format = QComboBox(BTITab)
        self.bti_palette_format.setObjectName(u"bti_palette_format")

        self.formLayout.setWidget(5, QFormLayout.FieldRole, self.bti_palette_format)

        self.label_3 = QLabel(BTITab)
        self.label_3.setObjectName(u"label_3")

        self.formLayout.setWidget(6, QFormLayout.LabelRole, self.label_3)

        self.bti_wrap_s = QComboBox(BTITab)
        self.bti_wrap_s.setObjectName(u"bti_wrap_s")

        self.formLayout.setWidget(6, QFormLayout.FieldRole, self.bti_wrap_s)

        self.label_4 = QLabel(BTITab)
        self.label_4.setObjectName(u"label_4")

        self.formLayout.setWidget(7, QFormLayout.LabelRole, self.label_4)

        self.bti_wrap_t = QComboBox(BTITab)
        self.bti_wrap_t.setObjectName(u"bti_wrap_t")

        self.formLayout.setWidget(7, QFormLayout.FieldRole, self.bti_wrap_t)

        self.label_5 = QLabel(BTITab)
        self.label_5.setObjectName(u"label_5")

        self.formLayout.setWidget(8, QFormLayout.LabelRole, self.label_5)

        self.bti_min_filter = QComboBox(BTITab)
        self.bti_min_filter.setObjectName(u"bti_min_filter")

        self.formLayout.setWidget(8, QFormLayout.FieldRole, self.bti_min_filter)

        self.label_6 = QLabel(BTITab)
        self.label_6.setObjectName(u"label_6")

        self.formLayout.setWidget(9, QFormLayout.LabelRole, self.label_6)

        self.bti_mag_filter = QComboBox(BTITab)
        self.bti_mag_filter.setObjectName(u"bti_mag_filter")

        self.formLayout.setWidget(9, QFormLayout.FieldRole, self.bti_mag_filter)

        self.label_7 = QLabel(BTITab)
        self.label_7.setObjectName(u"label_7")

        self.formLayout.setWidget(10, QFormLayout.LabelRole, self.label_7)

        self.bti_alpha_setting = QLineEdit(BTITab)
        self.bti_alpha_setting.setObjectName(u"bti_alpha_setting")
        sizePolicy1 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.bti_alpha_setting.sizePolicy().hasHeightForWidth())
        self.bti_alpha_setting.setSizePolicy(sizePolicy1)
        self.bti_alpha_setting.setMaximumSize(QSize(35, 16777215))

        self.formLayout.setWidget(10, QFormLayout.FieldRole, self.bti_alpha_setting)

        self.label_8 = QLabel(BTITab)
        self.label_8.setObjectName(u"label_8")

        self.formLayout.setWidget(11, QFormLayout.LabelRole, self.label_8)

        self.bti_min_lod = QLineEdit(BTITab)
        self.bti_min_lod.setObjectName(u"bti_min_lod")
        sizePolicy1.setHeightForWidth(self.bti_min_lod.sizePolicy().hasHeightForWidth())
        self.bti_min_lod.setSizePolicy(sizePolicy1)
        self.bti_min_lod.setMaximumSize(QSize(35, 16777215))

        self.formLayout.setWidget(11, QFormLayout.FieldRole, self.bti_min_lod)

        self.label_9 = QLabel(BTITab)
        self.label_9.setObjectName(u"label_9")

        self.formLayout.setWidget(12, QFormLayout.LabelRole, self.label_9)

        self.bti_max_lod = QLineEdit(BTITab)
        self.bti_max_lod.setObjectName(u"bti_max_lod")
        sizePolicy1.setHeightForWidth(self.bti_max_lod.sizePolicy().hasHeightForWidth())
        self.bti_max_lod.setSizePolicy(sizePolicy1)
        self.bti_max_lod.setMaximumSize(QSize(35, 16777215))

        self.formLayout.setWidget(12, QFormLayout.FieldRole, self.bti_max_lod)

        self.label_10 = QLabel(BTITab)
        self.label_10.setObjectName(u"label_10")

        self.formLayout.setWidget(13, QFormLayout.LabelRole, self.label_10)

        self.bti_lod_bias = QLineEdit(BTITab)
        self.bti_lod_bias.setObjectName(u"bti_lod_bias")
        sizePolicy1.setHeightForWidth(self.bti_lod_bias.sizePolicy().hasHeightForWidth())
        self.bti_lod_bias.setSizePolicy(sizePolicy1)
        self.bti_lod_bias.setMaximumSize(QSize(45, 16777215))

        self.formLayout.setWidget(13, QFormLayout.FieldRole, self.bti_lod_bias)

        self.label_14 = QLabel(BTITab)
        self.label_14.setObjectName(u"label_14")

        self.formLayout.setWidget(14, QFormLayout.LabelRole, self.label_14)

        self.bti_mipmap_count = QLineEdit(BTITab)
        self.bti_mipmap_count.setObjectName(u"bti_mipmap_count")
        self.bti_mipmap_count.setMaximumSize(QSize(35, 16777215))

        self.formLayout.setWidget(14, QFormLayout.FieldRole, self.bti_mipmap_count)

        self.label_16 = QLabel(BTITab)
        self.label_16.setObjectName(u"label_16")

        self.formLayout.setWidget(15, QFormLayout.LabelRole, self.label_16)

        self.bti_curr_mipmap = QComboBox(BTITab)
        self.bti_curr_mipmap.setObjectName(u"bti_curr_mipmap")
        self.bti_curr_mipmap.setMinimumSize(QSize(100, 0))

        self.formLayout.setWidget(15, QFormLayout.FieldRole, self.bti_curr_mipmap)


        self.horizontalLayout_8.addLayout(self.formLayout)

        self.horizontalLayout_8.setStretch(0, 1)

        self.verticalLayout.addLayout(self.horizontalLayout_8)


        self.retranslateUi(BTITab)

        QMetaObject.connectSlotsByName(BTITab)
    # setupUi

    def retranslateUi(self, BTITab):
        BTITab.setWindowTitle(QCoreApplication.translate("BTITab", u"Form", None))
        self.import_bti.setText(QCoreApplication.translate("BTITab", u"Import BTI", None))
        self.import_bti_image.setText(QCoreApplication.translate("BTITab", u"Import Image", None))
        self.replace_bti_mipmap.setText(QCoreApplication.translate("BTITab", u"Replace Mipmap", None))
        self.import_bti_from_bnr.setText(QCoreApplication.translate("BTITab", u"Import From Banner (.bnr)", None))
        self.export_bti.setText(QCoreApplication.translate("BTITab", u"Export BTI", None))
        self.export_bti_image.setText(QCoreApplication.translate("BTITab", u"Export Image", None))
        self.bti_image_label.setText("")
        self.label_11.setText(QCoreApplication.translate("BTITab", u"File Size", None))
        self.bti_file_size.setText(QCoreApplication.translate("BTITab", u"123", None))
        self.label_12.setText(QCoreApplication.translate("BTITab", u"Resolution", None))
        self.bti_resolution.setText(QCoreApplication.translate("BTITab", u"123x123", None))
        self.label_13.setText(QCoreApplication.translate("BTITab", u"Num Colors", None))
        self.bti_num_colors.setText(QCoreApplication.translate("BTITab", u"123", None))
        self.label_15.setText(QCoreApplication.translate("BTITab", u"Max Colors", None))
        self.bti_max_colors.setText(QCoreApplication.translate("BTITab", u"123", None))
        self.label.setText(QCoreApplication.translate("BTITab", u"Image Format", None))
        self.label_2.setText(QCoreApplication.translate("BTITab", u"Palette Format", None))
        self.label_3.setText(QCoreApplication.translate("BTITab", u"Wrap X", None))
        self.label_4.setText(QCoreApplication.translate("BTITab", u"Wrap Y", None))
        self.label_5.setText(QCoreApplication.translate("BTITab", u"Min Filter", None))
        self.label_6.setText(QCoreApplication.translate("BTITab", u"Mag Filter", None))
        self.label_7.setText(QCoreApplication.translate("BTITab", u"Alpha Setting", None))
        self.label_8.setText(QCoreApplication.translate("BTITab", u"Min LOD", None))
        self.label_9.setText(QCoreApplication.translate("BTITab", u"Max LOD", None))
        self.label_10.setText(QCoreApplication.translate("BTITab", u"LOD Bias", None))
        self.label_14.setText(QCoreApplication.translate("BTITab", u"Num Mipmaps", None))
        self.label_16.setText(QCoreApplication.translate("BTITab", u"Selected Mipmap", None))
    # retranslateUi

