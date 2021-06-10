import os
import random
from csv import reader
from json import dumps, load, loads, dump
from os import getpid
from sys import argv
from threading import Thread, current_thread
from time import sleep, time
from PyQt5.QtGui import QFontDatabase

import psutil
from PyQt5 import QtCore, QtWidgets
from PyQt5.Qt import QApplication, QMainWindow, QWidget, QWindow, QFormLayout
from PyQt5.QtCore import QProcess
from selenium import webdriver
from win32 import win32process
from win32gui import FindWindow

from PyQt5.QtWidgets import QComboBox, QDialog, QDialogButtonBox, QFileDialog, QHBoxLayout, QMessageBox, QTreeWidgetItem, QVBoxLayout
from PyQt5.Qt import QWindow, QLabel, QLineEdit

from extension import Element, Page, subClass, Struct, sequentialStruct, Field
from Ui_main import Ui_MainWindow
from utils import receipt, stop_thread

_translate = QtCore.QCoreApplication.translate


class QD(QDialog):
    """
    QD

    Args:
        QDialog ([type]): [description]
    """
    def __init__(self,
                 fparent,
                 parent=None,
                 title="",
                 accepted=lambda x: print('accepted')):
        super().__init__(parent)
        self.fparent = fparent
        self.setWindowModality(QtCore.Qt.WindowModal)
        if title:
            self.setWindowTitle(title)
        self.accepted = accepted

    def show(self):
        layout = QFormLayout(self)
        for n, f in self.fparent.fields.items():
            layout.addRow(QLabel(n), f.askQt(self))
        buttonBox = QDialogButtonBox()
        buttonBox.setOrientation(QtCore.Qt.Horizontal)  # 设置为水平方向
        buttonBox.setStandardButtons(QDialogButtonBox.Ok
                                     | QDialogButtonBox.Cancel)
        layout.addRow(buttonBox)
        buttonBox.accepted.connect(lambda x=self: self.accepted(x))  # 确定
        buttonBox.rejected.connect(self.close)
        self.setLayout(layout)

        super().show()


class ElementQd(QDialog):
    def __init__(self,
                 item,
                 title,
                 parent=None,
                 accepted=lambda x: print('accepted')):
        super().__init__(parent)
        self.setWindowModality(QtCore.Qt.WindowModal)
        if title:
            self.setWindowTitle(title)
        self.accepted = accepted
        self.item = item

    def show(self):
        pass
        qb = QComboBox(self)
        tag = self.item.data['localName']

        elements = self.parent().tags[tag]
        for element in elements:
            qb.addItem(element.name())
        self.qb = qb

        buttonBox = QDialogButtonBox()
        buttonBox.setOrientation(QtCore.Qt.Horizontal)  # 设置为水平方向
        buttonBox.setStandardButtons(QDialogButtonBox.Ok
                                     | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.pull)  # 确定
        buttonBox.rejected.connect(self.close)
        layout = QVBoxLayout(self)
        layout.addWidget(self.qb)
        layout.addWidget(buttonBox)
        super().show()

    def pull(self):
        currentIndex = self.qb.currentIndex()
        tag = self.item.data['localName']
        currentElement = self.parent().tags[tag][currentIndex]
        self.qd = QD(currentElement,
                     self,
                     'Add ELement',
                     lambda x=self: self.accepted(x))
        self.qd.data = self.item.data
        self.qd.show()


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.bindJs = self.readJs()
        self.setupUi(self)

    def setupUi(self, MainWindow):
        """注册安装组件
        """
        super().setupUi(MainWindow)
        self.verifyDriver()
        self.setupChrome()
        self.setupExtension()
        self.setupTimer()
        self.selectDemoButton.clicked.connect(self.selectDemo)
        self.saveDemoButton.clicked.connect(self.saveDemo)
        self.selectTaskButton.clicked.connect(self.selectTask)
        self.pauseTaskButton.clicked.connect(self.pauseTask)
        self.startTaskButton.clicked.connect(self.startTask)
        self.subClass = {
            'Struct': self.subStruct,
            'Element': self.subElement,
            'Page': self.subPage
        }
        self.chromeTask = None
        self.threadTask = None
        self.isworking = False
        # TODO
        # self.rightTree.itemDoubleClicked.connect(self)
        print()

    def verifyDriver(self):
        """
        TODO:验证或下载驱动
        """
        pass

    def setupExtension(self):
        """
        安装扩展
        """
        self.setupStructExtension()
        self.setupPageExtension()
        self.setupElementExtension()
        self.actionBind.triggered.connect(lambda x: self.addBinds())
        self.actionRemoveElements.triggered.connect(
            lambda: self.removeElements())
        self.rightTree.expandAll()

    def setupStructExtension(self):
        """
        """
        print(subClass(Struct))

        self.subStruct = dict()
        self.structMenu.clear()
        while self.structTree.topLevelItem(0):
            self.structTree.takeTopLevelItem(0)

        for ss in subClass(Struct):
            if ss is not sequentialStruct:

                action = QtWidgets.QAction(self)
                action.setCheckable(True)
                action.setObjectName('structSelect' + ss.name())
                action.setText(_translate("MainWindow", ss.name()))
                action.triggered.connect(
                    lambda checked, ss=ss: self.setupStruct(ss))
                self.structMenu.addAction(action)
                self.subStruct[ss.name()] = {
                    'class_': ss,
                    'action': action,
                    'load': False
                }

                if ss.autoLoad:
                    self.setupStruct(ss)
            else:
                self.subStruct[ss.name()] = {'class_': ss, 'load': True}
        self.structTree.itemDoubleClicked.connect(self.addStruct)
        self.structTree.expandAll()

        self.structDemo = sequentialStruct()
        self.structDemo.load({})
        item = self.itemWithField(self.rightTree, self.structDemo)
        self.structDemo.setItem(item)

        self.itemDemo = item

    def setupStruct(self, ss):
        """
        setupStruct
        """
        print('addPageExtension', ss.name())
        ssdict = self.subStruct[ss.name()]
        ssdict['load'] = not ssdict['load']
        action = ssdict['action']
        action.setChecked(ssdict['load'])

        if ssdict['load']:
            item = self.itemWithField(self.structTree, ss)
            item.class_ = ss
        else:
            i = 0
            while self.structTree.topLevelItem(i):
                if self.structTree.topLevelItem(i).text(0) == ss.name():
                    self.structTree.takeTopLevelItem(i)
                    self.structTree.update()
                    return
                else:
                    i += 1

    def addStruct(self, item, column):
        """
        addStruct
        """
        while not hasattr(item, 'class_'):
            item = item.parent()

        # if issubclass(item.class_, (Struct)):
        qd = QD(item.class_, self, 'AddStruct', self.addStructGui)
        qd.show()

    def addStructGui(self, qd: QD):
        """
        AddStructGui
        """

        tmp = []
        i = 0
        for i in range(qd.layout().count()):
            item = qd.layout().itemAt(i).widget()
            if isinstance(item, QLabel):

                continue
            tmp.append(item)
        tmp = tmp[:len(qd.fparent.fields)]

        fields = {}
        for (fn, f), q in zip(qd.fparent.fields.items(), tmp):
            r, fields[fn] = f.loads(q)
            if not r:
                QMessageBox.information(
                    qd, 'add Page wrong',
                    f'{fn} has a wrong input!\nTry it again.', QMessageBox.Ok)
                return

        qd.close()

        self.addStructJson(qd.fparent, fields)

    def addStructJson(self, ss, fields):
        """
        AddStructjson
        """
        struct = ss()
        struct.load(fields)

        self.structDemo.add(struct)
        item = self.itemWithField(self.itemDemo, struct, fields)
        item.class_ = struct
        struct.setItem(item)
        self.structDemo = struct
        self.itemDemo = item

    def setupPageExtension(self):
        """
        安装Page扩展
        """
        print(subClass(Page))

        column = 0

        self.subPage = dict()
        self.pageMenu.clear()

        while self.pageTree.topLevelItem(0):
            self.pageTree.takeTopLevelItem(0)

        for sp in subClass(Page):
            action = QtWidgets.QAction(self)
            action.setCheckable(True)
            action.setObjectName('pageSelect' + sp.name())
            action.setText(_translate("MainWindow", sp.name()))
            action.triggered.connect(lambda checked, sp=sp: self.setupPage(sp))
            self.pageMenu.addAction(action)
            self.subPage[sp.name()] = {
                'class_': sp,
                'action': action,
                'load': False
            }

            if sp.autoLoad:
                self.setupPage(sp)

        self.pageTree.expandAll()
        self.pageTree.itemDoubleClicked.connect(self.addPage)

    def itemWithField(self, parent, class_, fields=None):
        item = QTreeWidgetItem(parent)
        item.setText(0, _translate('MainWindow', class_.name()))
        item.class_ = class_
        for fn in class_.fields:
            tmp = QTreeWidgetItem(item)
            if hasattr(class_, 'fields_'):
                tmp.setText(
                    0, _translate('MainWindow', f'{fn}:{class_.fields_[fn]}'))
            elif fields:
                tmp.setText(0, _translate('MainWindow', f'{fn}:{fields[fn]}'))
            else:
                tmp.setText(0, _translate('MainWindow', f'{fn}'))
        return item

    def itemElement(self, parent, data, se=None, fields={}):

        if se:
            item = self.itemWithField(parent, se, fields)
            item.setText(
                0,
                _translate('MainWindow',
                           f'{se.name()}:{data["seleniumXpath"]}'))
        else:
            item = QTreeWidgetItem(parent)
            item.class_ = Element
            item.setText(0, _translate('MainWindow', data['seleniumXpath']))
        for n in ['localName', 'className']:
            if n in data:
                tmp = QTreeWidgetItem(item)
                tmp.setText(0, _translate('MainWindow', f'{n}:{data[n]}'))
        item.class_ = se
        return item

    def setupPage(self, sp: Page):
        """
        安装Page扩展
        Args:
            sp (Page): [description]
        """
        print('addPageExtension', sp.name())
        column = 1
        spdict = self.subPage[sp.name()]
        spdict['load'] = not spdict['load']
        action = spdict['action']
        action.setChecked(spdict['load'])

        if spdict['load']:
            item = self.itemWithField(self.pageTree, sp)
            item.class_ = sp
        else:
            i = 0
            while self.pageTree.topLevelItem(i):
                if self.pageTree.topLevelItem(i).text(0) == sp.name():
                    self.pageTree.takeTopLevelItem(i)
                    self.pageTree.update()
                    return
                else:
                    i += 1

    def addPage(self, item, column):
        """
        addPage
        """
        while not hasattr(item, 'class_'):
            item = item.parent()
        qd = QD(item.class_, self, 'AddPage', self.addPageGui)
        qd.show()

    def addPageGui(self, qd: QD):
        """
        Args:
            qd (QD): [description]
        """

        tmp = []
        i = 0
        print(qd.layout().count())
        for i in range(qd.layout().count()):
            item = qd.layout().itemAt(i).widget()
            if isinstance(item, QLabel):
                continue
            tmp.append(item)
        tmp = tmp[:len(qd.fparent.fields)]

        fields = {}
        for (fn, f), q in zip(qd.fparent.fields.items(), tmp):
            r, fields[fn] = f.loads(q)
            if not r:
                QMessageBox.information(
                    qd, 'add Page wrong',
                    f'{fn} has a wrong input!\nTry it again.', QMessageBox.Ok)
                return

        qd.close()

        self.addPageJson(qd.fparent, fields)

    def addPageJson(self, sp, fields):
        """
        AddStructjson
        """
        page = sp()
        page.load(fields)
        self.structDemo.add(page)
        item = self.itemWithField(self.itemDemo, page, fields)
        page.setItem(item)
        item.class_ = page

    def setupElementExtension(self):
        """
        安装Element扩展
        """
        column = 0

        self.subElement = dict()
        self.tags = {}
        for se in subClass(Element):

            action = QtWidgets.QAction(self)
            action.setCheckable(True)
            action.setObjectName('elementSelect' + se.name())
            action.setText(_translate("MainWindow", se.name()))
            action.triggered.connect(
                lambda checked, se=se: self.setupElement(se))
            print(action.triggered)
            self.elementMenu.addAction(action)
            self.subElement[se.name()] = {
                'class_': se,
                'action': action,
                'load': False
            }
            if se.autoLoad:
                self.setupElement(se)
        self.elementTree.itemDoubleClicked.connect(self.addElement)

        print(self.elementTree.itemPressed.connect(lambda x, y: print(x, y)))

    def setupElement(self, se: Element):
        """
        安装Element扩展
        """
        print('setupElement', se.name())
        column = 0
        sedict = self.subElement[se.name()]
        sedict['load'] = not sedict['load']
        action = sedict['action']
        action.setChecked(sedict['load'])
        if sedict['load']:
            for tag in se.tags:
                if tag in self.tags:
                    self.tags[tag].append(se)
                else:
                    self.tags[tag] = [se]
                    self.addBinds(tag)
        else:
            for tag in se.tags:
                self.tags[tag].remove(se)
                if not self.tags[tag]:
                    self.removeBinds(tag)
                    self.tags.pop(tag)

    def addElement(self, item, column):
        """
        addElement
        """
        while not hasattr(item, 'class_'):
            item = item.parent()
        qd = ElementQd(item, 'AddElement', self, self.addElementGui)
        qd.show()

    def removeElement(self, item, column):
        while not hasattr(item, 'class_'):
            item = item.parent()
        i = 0
        tmp = self.elementTree.topLevelItem(i)
        while tmp:
            if tmp is item:
                self.elementTree.takeTopLevelItem(i)
                self.elements.pop(item.data['seleniumXpath'])
                return
            i += 1
            tmp = self.elementTree.topLevelItem(i)

    def removeElements(self):
        self.elements = {}
        while self.elementTree.topLevelItem(0):
            self.elementTree.takeTopLevelItem(0)

    def removeAllElement(self):
        item = self.leftTree.topLevelItem(0)
        while item:
            self.removeElement(item, 0)
            item = self.leftTree.topLevelItem(0)

    def addElementGui(self, qd: QD):
        """
        Args:
            qd (QD): [description]
        """

        tmp = []
        i = 0
        print(qd.layout().count())
        for i in range(qd.layout().count()):
            item = qd.layout().itemAt(i).widget()
            if isinstance(item, QLabel):
                continue
            tmp.append(item)
        tmp = tmp[:len(qd.fparent.fields)]

        fields = {}
        for (fn, f), q in zip(qd.fparent.fields.items(), tmp):
            r, fields[fn] = f.loads(q)
            if not r:
                QMessageBox.information(
                    qd, 'add Page wrong',
                    f'{fn} has a wrong input!\nTry it again.', QMessageBox.Ok)
                return
        qd.parent().close()
        self.removeElement(qd.parent().item, 0)
        qd.close()

        self.addElementJson(
            qd.fparent,
            qd.data,
            fields,
        )

    def addElementJson(self, se, data, fields):
        element = se()
        element.load(data, fields)
        self.structDemo.add(element)
        # item = self.itemWithField(self.itemDemo, element, fields)
        item = self.itemElement(self.itemDemo, data, element, fields)
        item.class_ = element
        element.setItem(item)
        return

    def setupChrome(self):
        """打开并连接chrome
        """

        options = webdriver.ChromeOptions()
        options.add_argument('--ignore-certificate-errors')
        options.add_experimental_option(
            "excludeSwitches", ['enable-automation', 'enable-logging'])
        try:
            self.chrome = webdriver.Chrome(options=options, keep_alive=True)
        except Exception as e:
            print(e)
        cwid = 0
        while not cwid:
            if not self.chrome.title:
                cwid = FindWindow(None,
                                  self.chrome.current_url + ' - Google Chrome')
            else:
                cwid = FindWindow(None, self.chrome.title + ' - Google Chrome')
        pWin = QWindow.fromWinId(cwid)
        pWid = QWidget.createWindowContainer(pWin, self)
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(pWid)
        # self.chrome.get('https://www.baidu.com')
        self.middle.setLayout(layout)
        self.middle.update()

    def readJs(self, path='utils/script.js'):
        """读取绑定Js
        """
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()

    def addBinds(self, tag=''):
        # self.chrome.execute_script(self.bindJs)
        print('addBinds', tag)
        if tag:
            self.chrome.execute_script(f'{self.bindJs};\nadd_binds("{tag}");')
        else:
            for tag in self.tags:
                self.addBinds(tag)

    def removeBinds(self, tag):
        self.chrome.execute_script(f'{self.bindJs};\nremove_binds("{tag}");')

    def setupTimer(self):
        self.elements = {}
        self.pollingTimer = QtCore.QTimer(self)
        self.pollingTimer.timeout.connect(self.polling)
        self.pollingTimer.start(1000)

    def polling(self):
        try:
            for r in receipt['data']:
                if r['seleniumXpath'] not in self.elements:
                    self.elements[r['seleniumXpath']] = r
                    item = self.itemElement(self.elementTree, r)
                    item.data = r
                receipt['data'].remove(r)
        except Exception as e:
            print(e)

    def saveDemo(self):
        """
        saveDemo
        """
        saveFile = QFileDialog.getSaveFileName(self, '选择一个json文件', './.',
                                               'All(*.*)')[0]
        item = self.rightTree.topLevelItem(0)
        struct = item.class_
        if saveFile:
            try:
                with open(saveFile, 'w', encoding='utf-8') as f:
                    dump(struct.dumps(), f)
            except Exception as e:
                print(e)

    def selectTask(self):
        readFile = QFileDialog.getOpenFileName(self, '选择一个json文件', './.',
                                               'All(*.*)')[0]
        with open(readFile, 'r', encoding='utf-8') as f:
            data = loads(f.read(), strict=False)
        self.isworking = False
        if self.threadTask:
            try:
                stop_thread(self.threadTask)
            except Exception as e:
                pass
            finally:
                self.threadTask = None
        while self.taskTree.topLevelItem(0):
            self.taskTree.takeTopLevelItem(0)
        self.loadDemo(self.taskTree, data)

    def getChromeTask(self):
        try:
            self.chromeTask.current_url
        except:
            self.chromeTask = webdriver.Chrome()
        finally:
            return self.chromeTask

    def startTask(self):
        """
        开始/继续
        """
        if self.isworking:
            pass
        else:
            self.isworking = True
            if not self.threadTask:
                self.itemTask = self.taskTree.topLevelItem(0)
                if self.itemTask:
                    self.structTask = self.itemTask.class_
                else:
                    print('no demo')
                    return
                self.threadTask = Thread(target=self.execute)
                self.threadTask.setDaemon(True)
                self.threadTask.start()

    def execute(self):
        self.itemTask = self.taskTree.topLevelItem(0)
        if self.itemTask:
            class_ = self.itemTask.class_
            class_.play(self, self.getChromeTask())

    def pauseTask(self):
        """
        暂停/停止
        """
        if self.isworking:
            self.isworking = False
        else:
            if self.threadTask:
                stop_thread(self.threadTask)
                self.threadTask = None

    def selectDemo(self):
        readFile = QFileDialog.getOpenFileName(self, '选择一个json文件', './.',
                                               'All(*.*)')[0]
        with open(readFile, 'r', encoding='utf-8') as f:
            data = loads(f.read())
        while self.rightTree.topLevelItem(0):
            self.rightTree.takeTopLevelItem(0)
        self.loadDemo(self.rightTree, data)

    def loadDemo(self, parent, data):
        class_ = self.subClass[data['super']][data['class_']]['class_']()
        fields = data['fields']
        # class_ = class_()
        if data['super'] == 'Element':
            class_.load(data['data'], fields)
            item = self.itemElement(parent, data['data'], class_, fields)
            item.class_ = class_
            class_.setItem(item)
        else:
            class_.load(fields)
            item = self.itemWithField(parent, class_, fields)
            class_.setItem(item)
        if data['super'] == 'Struct':
            for d in data['data']:
                c_, i_ = self.loadDemo(item, d)
                class_.add(c_)
        return class_, item

    def info(self, title, info):
        QMessageBox.information(self, title, info, QMessageBox.Ok)


if __name__ == '__main__':
    qApp = QApplication(argv)
    window = MainWindow()

    window.show()
    exit(qApp.exec_())
