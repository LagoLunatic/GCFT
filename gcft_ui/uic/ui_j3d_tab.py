# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'j3d_tab.ui'
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
    QPushButton, QScrollArea, QSizePolicy, QSlider,
    QSplitter, QTreeWidget, QTreeWidgetItem, QVBoxLayout,
    QWidget)

from gcft_ui.j3d_viewer import J3DViewer

class Ui_J3DTab(object):
    def setupUi(self, J3DTab):
        if not J3DTab.objectName():
            J3DTab.setObjectName(u"J3DTab")
        J3DTab.resize(1095, 702)
        self.actionOpenJ3DImage = QAction(J3DTab)
        self.actionOpenJ3DImage.setObjectName(u"actionOpenJ3DImage")
        self.actionReplaceJ3DImage = QAction(J3DTab)
        self.actionReplaceJ3DImage.setObjectName(u"actionReplaceJ3DImage")
        self.verticalLayout = QVBoxLayout(J3DTab)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.import_j3d = QPushButton(J3DTab)
        self.import_j3d.setObjectName(u"import_j3d")

        self.horizontalLayout_6.addWidget(self.import_j3d)

        self.export_j3d = QPushButton(J3DTab)
        self.export_j3d.setObjectName(u"export_j3d")

        self.horizontalLayout_6.addWidget(self.export_j3d)


        self.verticalLayout.addLayout(self.horizontalLayout_6)

        self.splitter = QSplitter(J3DTab)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Horizontal)
        self.verticalLayoutWidget_2 = QWidget(self.splitter)
        self.verticalLayoutWidget_2.setObjectName(u"verticalLayoutWidget_2")
        self.verticalLayout_6 = QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.j3d_chunks_tree = QTreeWidget(self.verticalLayoutWidget_2)
        self.j3d_chunks_tree.setObjectName(u"j3d_chunks_tree")
        self.j3d_chunks_tree.setMinimumSize(QSize(370, 0))

        self.verticalLayout_6.addWidget(self.j3d_chunks_tree)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.anim_pause_button = QPushButton(self.verticalLayoutWidget_2)
        self.anim_pause_button.setObjectName(u"anim_pause_button")
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.anim_pause_button.sizePolicy().hasHeightForWidth())
        self.anim_pause_button.setSizePolicy(sizePolicy)
        self.anim_pause_button.setMaximumSize(QSize(30, 16777215))

        self.horizontalLayout.addWidget(self.anim_pause_button)

        self.anim_slider = QSlider(self.verticalLayoutWidget_2)
        self.anim_slider.setObjectName(u"anim_slider")
        self.anim_slider.setOrientation(Qt.Horizontal)

        self.horizontalLayout.addWidget(self.anim_slider)


        self.verticalLayout_6.addLayout(self.horizontalLayout)

        self.splitter.addWidget(self.verticalLayoutWidget_2)
        self.j3d_sidebar = QWidget(self.splitter)
        self.j3d_sidebar.setObjectName(u"j3d_sidebar")
        self.verticalLayout_2 = QVBoxLayout(self.j3d_sidebar)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.j3d_sidebar_label = QLabel(self.j3d_sidebar)
        self.j3d_sidebar_label.setObjectName(u"j3d_sidebar_label")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.j3d_sidebar_label.sizePolicy().hasHeightForWidth())
        self.j3d_sidebar_label.setSizePolicy(sizePolicy1)

        self.horizontalLayout_2.addWidget(self.j3d_sidebar_label)

        self.toggle_visibility = QPushButton(self.j3d_sidebar)
        self.toggle_visibility.setObjectName(u"toggle_visibility")
        self.toggle_visibility.setMaximumSize(QSize(60, 16777215))

        self.horizontalLayout_2.addWidget(self.toggle_visibility)

        self.update_j3d_preview = QPushButton(self.j3d_sidebar)
        self.update_j3d_preview.setObjectName(u"update_j3d_preview")
        sizePolicy.setHeightForWidth(self.update_j3d_preview.sizePolicy().hasHeightForWidth())
        self.update_j3d_preview.setSizePolicy(sizePolicy)
        self.update_j3d_preview.setMaximumSize(QSize(30, 16777215))

        self.horizontalLayout_2.addWidget(self.update_j3d_preview)


        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.scrollArea = QScrollArea(self.j3d_sidebar)
        self.scrollArea.setObjectName(u"scrollArea")
        sizePolicy2 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(5)
        sizePolicy2.setHeightForWidth(self.scrollArea.sizePolicy().hasHeightForWidth())
        self.scrollArea.setSizePolicy(sizePolicy2)
        self.scrollArea.setMinimumSize(QSize(250, 0))
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 369, 618))
        self.verticalLayout_3 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout_2.addWidget(self.scrollArea)

        self.verticalLayout_2.setStretch(1, 1)
        self.splitter.addWidget(self.j3d_sidebar)
        self.verticalLayoutWidget = QWidget(self.splitter)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayout_5 = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.j3dultra_error_area = QScrollArea(self.verticalLayoutWidget)
        self.j3dultra_error_area.setObjectName(u"j3dultra_error_area")
        sizePolicy3 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.j3dultra_error_area.sizePolicy().hasHeightForWidth())
        self.j3dultra_error_area.setSizePolicy(sizePolicy3)
        self.j3dultra_error_area.setWidgetResizable(True)
        self.scrollAreaWidgetContents_2 = QWidget()
        self.scrollAreaWidgetContents_2.setObjectName(u"scrollAreaWidgetContents_2")
        self.scrollAreaWidgetContents_2.setGeometry(QRect(0, 0, 308, 69))
        self.verticalLayout_4 = QVBoxLayout(self.scrollAreaWidgetContents_2)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(-1, 0, -1, 0)
        self.j3dultra_error_label = QLabel(self.scrollAreaWidgetContents_2)
        self.j3dultra_error_label.setObjectName(u"j3dultra_error_label")
        self.j3dultra_error_label.setWordWrap(True)
        self.j3dultra_error_label.setTextInteractionFlags(Qt.LinksAccessibleByMouse|Qt.TextSelectableByMouse)

        self.verticalLayout_4.addWidget(self.j3dultra_error_label)

        self.j3dultra_error_area.setWidget(self.scrollAreaWidgetContents_2)

        self.verticalLayout_5.addWidget(self.j3dultra_error_area)

        self.j3d_viewer = J3DViewer(self.verticalLayoutWidget)
        self.j3d_viewer.setObjectName(u"j3d_viewer")
        sizePolicy4 = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(5)
        sizePolicy4.setHeightForWidth(self.j3d_viewer.sizePolicy().hasHeightForWidth())
        self.j3d_viewer.setSizePolicy(sizePolicy4)
        self.j3d_viewer.setMinimumSize(QSize(300, 300))
        self.j3d_viewer.setFocusPolicy(Qt.ClickFocus)

        self.verticalLayout_5.addWidget(self.j3d_viewer)

        self.splitter.addWidget(self.verticalLayoutWidget)

        self.verticalLayout.addWidget(self.splitter)

        self.verticalLayout.setStretch(1, 1)

        self.retranslateUi(J3DTab)

        QMetaObject.connectSlotsByName(J3DTab)
    # setupUi

    def retranslateUi(self, J3DTab):
        J3DTab.setWindowTitle(QCoreApplication.translate("J3DTab", u"Form", None))
        self.actionOpenJ3DImage.setText(QCoreApplication.translate("J3DTab", u"Open Image", None))
        self.actionReplaceJ3DImage.setText(QCoreApplication.translate("J3DTab", u"Replace Image", None))
        self.import_j3d.setText(QCoreApplication.translate("J3DTab", u"Import J3D File", None))
        self.export_j3d.setText(QCoreApplication.translate("J3DTab", u"Export J3D File", None))
        ___qtreewidgetitem = self.j3d_chunks_tree.headerItem()
        ___qtreewidgetitem.setText(2, QCoreApplication.translate("J3DTab", u"Size", None));
        ___qtreewidgetitem.setText(1, QCoreApplication.translate("J3DTab", u"Name", None));
        ___qtreewidgetitem.setText(0, QCoreApplication.translate("J3DTab", u"Chunk Type", None));
        self.anim_pause_button.setText("")
        self.j3d_sidebar_label.setText(QCoreApplication.translate("J3DTab", u"Extra information will be displayed here as necessary.", None))
        self.toggle_visibility.setText("")
        self.j3dultra_error_label.setText(QCoreApplication.translate("J3DTab", u"No errors to display.", None))
    # retranslateUi

