# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'bmg_tab.ui'
##
## Created by: Qt User Interface Compiler version 6.8.2
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
from PySide6.QtWidgets import (QApplication, QGridLayout, QHBoxLayout, QHeaderView,
    QLabel, QLineEdit, QPushButton, QScrollArea,
    QSizePolicy, QTextEdit, QTreeView, QVBoxLayout,
    QWidget)

class Ui_BMGTab(object):
    def setupUi(self, BMGTab):
        if not BMGTab.objectName():
            BMGTab.setObjectName(u"BMGTab")
        BMGTab.resize(785, 535)
        self.verticalLayout = QVBoxLayout(BMGTab)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.import_bmg = QPushButton(BMGTab)
        self.import_bmg.setObjectName(u"import_bmg")

        self.horizontalLayout_2.addWidget(self.import_bmg)

        self.export_bmg = QPushButton(BMGTab)
        self.export_bmg.setObjectName(u"export_bmg")

        self.horizontalLayout_2.addWidget(self.export_bmg)

        self.set_preview_font = QPushButton(BMGTab)
        self.set_preview_font.setObjectName(u"set_preview_font")

        self.horizontalLayout_2.addWidget(self.set_preview_font)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.filter = QLineEdit(BMGTab)
        self.filter.setObjectName(u"filter")

        self.verticalLayout.addWidget(self.filter)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.bmg_msgs_tree = QTreeView(BMGTab)
        self.bmg_msgs_tree.setObjectName(u"bmg_msgs_tree")

        self.horizontalLayout.addWidget(self.bmg_msgs_tree)

        self.msg_preview_container = QWidget(BMGTab)
        self.msg_preview_container.setObjectName(u"msg_preview_container")
        self.verticalLayout_2 = QVBoxLayout(self.msg_preview_container)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.scrollArea = QScrollArea(self.msg_preview_container)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 377, 222))
        self.gridLayout = QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout.setObjectName(u"gridLayout")
        self.msg_preview_label = QLabel(self.scrollAreaWidgetContents)
        self.msg_preview_label.setObjectName(u"msg_preview_label")
        self.msg_preview_label.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)

        self.gridLayout.addWidget(self.msg_preview_label, 0, 0, 1, 1)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout_2.addWidget(self.scrollArea)

        self.msg_string_text_edit = QTextEdit(self.msg_preview_container)
        self.msg_string_text_edit.setObjectName(u"msg_string_text_edit")

        self.verticalLayout_2.addWidget(self.msg_string_text_edit)


        self.horizontalLayout.addWidget(self.msg_preview_container)


        self.verticalLayout.addLayout(self.horizontalLayout)


        self.retranslateUi(BMGTab)

        QMetaObject.connectSlotsByName(BMGTab)
    # setupUi

    def retranslateUi(self, BMGTab):
        BMGTab.setWindowTitle(QCoreApplication.translate("BMGTab", u"Form", None))
        self.import_bmg.setText(QCoreApplication.translate("BMGTab", u"Import BMG", None))
        self.export_bmg.setText(QCoreApplication.translate("BMGTab", u"Export BMG", None))
        self.set_preview_font.setText(QCoreApplication.translate("BMGTab", u"Set Preview Font", None))
        self.filter.setPlaceholderText(QCoreApplication.translate("BMGTab", u"Filter", None))
        self.msg_preview_label.setText("")
    # retranslateUi

