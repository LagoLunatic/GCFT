# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'anim_control.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
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
from PySide6.QtWidgets import (QApplication, QGroupBox, QHBoxLayout, QLabel,
    QPushButton, QSizePolicy, QSlider, QSpinBox,
    QWidget)

class Ui_AnimControl(object):
    def setupUi(self, AnimControl):
        if not AnimControl.objectName():
            AnimControl.setObjectName(u"AnimControl")
        AnimControl.resize(400, 51)
        self.horizontalLayout = QHBoxLayout(AnimControl)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.pause_button = QPushButton(AnimControl)
        self.pause_button.setObjectName(u"pause_button")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pause_button.sizePolicy().hasHeightForWidth())
        self.pause_button.setSizePolicy(sizePolicy)
        self.pause_button.setMaximumSize(QSize(30, 16777215))

        self.horizontalLayout.addWidget(self.pause_button)

        self.seek_slider = QSlider(AnimControl)
        self.seek_slider.setObjectName(u"seek_slider")
        self.seek_slider.setOrientation(Qt.Horizontal)

        self.horizontalLayout.addWidget(self.seek_slider)

        self.frame_spinbox = QSpinBox(AnimControl)
        self.frame_spinbox.setObjectName(u"frame_spinbox")

        self.horizontalLayout.addWidget(self.frame_spinbox)

        self.duration_label = QLabel(AnimControl)
        self.duration_label.setObjectName(u"duration_label")

        self.horizontalLayout.addWidget(self.duration_label)

        self.detach_button = QPushButton(AnimControl)
        self.detach_button.setObjectName(u"detach_button")
        sizePolicy.setHeightForWidth(self.detach_button.sizePolicy().hasHeightForWidth())
        self.detach_button.setSizePolicy(sizePolicy)
        self.detach_button.setMaximumSize(QSize(30, 16777215))
        icon = QIcon()
        iconThemeName = u"accessories-calculator"
        if QIcon.hasThemeIcon(iconThemeName):
            icon = QIcon.fromTheme(iconThemeName)
        else:
            icon.addFile(u".", QSize(), QIcon.Mode.Normal, QIcon.State.Off)

        self.detach_button.setIcon(icon)

        self.horizontalLayout.addWidget(self.detach_button)


        self.retranslateUi(AnimControl)

        QMetaObject.connectSlotsByName(AnimControl)
    # setupUi

    def retranslateUi(self, AnimControl):
        AnimControl.setWindowTitle(QCoreApplication.translate("AnimControl", u"Form", None))
        self.pause_button.setText("")
        self.duration_label.setText(QCoreApplication.translate("AnimControl", u"/ 0", None))
#if QT_CONFIG(tooltip)
        self.detach_button.setToolTip(QCoreApplication.translate("AnimControl", u"Unload animation", None))
#endif // QT_CONFIG(tooltip)
        self.detach_button.setText("")
    # retranslateUi

