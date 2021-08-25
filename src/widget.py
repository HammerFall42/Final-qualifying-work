import sys
from os import environ
from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import QApplication, QWidget
from searcher import Searcher
from docformer import Docformer
import datetime

def suppress_qt_warnings():
    environ["QT_DEVICE_PIXEL_RATIO"] = "0"
    environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    environ["QT_SCREEN_SCALE_FACTORS"] = "1"
    environ["QT_SCALE_FACTOR"] = "1"


class MainWindow(QWidget):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.ui = uic.loadUi("form.ui", self)
        self.searcher = Searcher()
        self.docformer = Docformer()

    @pyqtSlot(name='on_addButton_clicked')
    def addUrl(self):
        self.listWidget.addItem(self.urlEdit.text())

    @pyqtSlot(name='on_deleteButton_clicked')
    def deleteUrl(self):
        listItems = self.listWidget.selectedItems()
        if not listItems:
            return
        for item in listItems:
            self.listWidget.takeItem(self.listWidget.row(item))

    @pyqtSlot(name='on_setParamButton_clicked')
    def setParams(self):
        if self.synCheck.isChecked():
            syn_count = self.synCount.text()
        else:
            syn_count = 0
        if self.linkCheck.isChecked():
            link_count = self.linkCount.text()
        else:
            link_count = 0
        if self.semanticCheck.isChecked():
            if self.themeRadButton.isChecked():
                depth = 1
            elif self.subThemeOneRadButton.isChecked():
                depth = 2
            else:
                depth = 3
        else:
            depth = -1
        self.searcher = Searcher(link_count, self.precCount.text(), self.folCount.text(), syn_count, depth)

    @pyqtSlot(name='on_searchButton_clicked')
    def searchUrls(self):
        dt = datetime.datetime.now()
        items = []
        for index in range(self.listWidget.count()):
            items.append(self.listWidget.item(index).text())
        result = self.searcher.startSearch(items, self.targetEdit.text(), self.unsplittableCheck.isChecked())
        self.docformer.createDoc(result, self.outputEdit.text())
        print((datetime.datetime.now() - dt).total_seconds())

def qt_app():
    suppress_qt_warnings()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()