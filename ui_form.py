# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'form.ui'
##
## Created by: Qt User Interface Compiler version 6.7.3
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
from PySide6.QtWidgets import (QApplication, QLabel, QMainWindow, QPushButton,
    QSizePolicy, QStatusBar, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(562, 201)
        self.Exit = QAction(MainWindow)
        self.Exit.setObjectName(u"Exit")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.BtnConvert = QPushButton(self.centralwidget)
        self.BtnConvert.setObjectName(u"BtnConvert")
        self.BtnConvert.setGeometry(QRect(30, 100, 111, 31))
        self.BtnSelectFile = QPushButton(self.centralwidget)
        self.BtnSelectFile.setObjectName(u"BtnSelectFile")
        self.BtnSelectFile.setGeometry(QRect(30, 20, 111, 31))
        self.LblFileName = QLabel(self.centralwidget)
        self.LblFileName.setObjectName(u"LblFileName")
        self.LblFileName.setGeometry(QRect(150, 20, 231, 31))
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(30, 140, 51, 31))
        self.LblStatus = QLabel(self.centralwidget)
        self.LblStatus.setObjectName(u"LblStatus")
        self.LblStatus.setGeometry(QRect(90, 140, 161, 31))
        self.BtnExit = QPushButton(self.centralwidget)
        self.BtnExit.setObjectName(u"BtnExit")
        self.BtnExit.setGeometry(QRect(440, 140, 101, 31))
        self.BtnSelectDestinationFolder = QPushButton(self.centralwidget)
        self.BtnSelectDestinationFolder.setObjectName(u"BtnSelectDestinationFolder")
        self.BtnSelectDestinationFolder.setGeometry(QRect(30, 60, 111, 31))
        font = QFont()
        font.setPointSize(8)
        self.BtnSelectDestinationFolder.setFont(font)
        self.LblDestinationName = QLabel(self.centralwidget)
        self.LblDestinationName.setObjectName(u"LblDestinationName")
        self.LblDestinationName.setGeometry(QRect(150, 60, 401, 31))
        self.LblFinalPath = QLabel(self.centralwidget)
        self.LblFinalPath.setObjectName(u"LblFinalPath")
        self.LblFinalPath.setGeometry(QRect(150, 100, 381, 31))
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.Exit.setText(QCoreApplication.translate("MainWindow", u"Exit", None))
        self.BtnConvert.setText(QCoreApplication.translate("MainWindow", u"Convert", None))
        self.BtnSelectFile.setText(QCoreApplication.translate("MainWindow", u"Select file", None))
        self.LblFileName.setText(QCoreApplication.translate("MainWindow", u"File not selected yet", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Status  : ", None))
        self.LblStatus.setText("")
        self.BtnExit.setText(QCoreApplication.translate("MainWindow", u"Exit", None))
        self.BtnSelectDestinationFolder.setText(QCoreApplication.translate("MainWindow", u"Destination Folder", None))
        self.LblDestinationName.setText(QCoreApplication.translate("MainWindow", u"The file path is not selected. It will be the same directory as the selected File", None))
        self.LblFinalPath.setText("")
    # retranslateUi

