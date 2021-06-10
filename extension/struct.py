from extension.field import selectField
from time import sleep
from PyQt5.QtGui import QColor, QBrush
import types
from . import intField, strField, fileField
from . import Field, subClass, Page, Element
from csv import reader
# elements = {i.name(): i for i in subClass(Element)}
# pages = {i.name(): i for i in subClass(Page)}


class Struct:
    autoLoad = True
    fields = {}

    @classmethod
    def name(cls):
        return cls.__name__

    def __init__(self) -> None:
        self.operations = []

    def vs(self, recode):
        self.v = {}
        for fn, f in self.fields.items():
            self.v[fn] = f.load(self.fields_[fn])

    def load(self, fields):
        """
        TODO
        """
        self.fields_ = fields

    def setItem(self, item):
        self.item = item

    def dumps(self):
        result = {
            'super': 'Struct',
            'class_': self.name(),
            'fields': self.fields_,
            'data': []
        }

        for op in self.operations:
            result['data'].append(op.dumps())
        return result

    def add(self, operation):
        """
        TODO
        """
        self.operations.append(operation)

    def play(self, window, driver, recode=[], **args):
        self.vs(recode)
        print(self, self.name())


class sequentialStruct(Struct):
    """
    TODO:顺序结构
    Args:
        Struct ([type]): [description]
    """
    def play(self, window, driver, recode=[], **args):
        super().play(window, driver, recode, **args)
        for op in self.operations:
            item = op.item
            while not window.isworking:
                sleep(0.1)
            op.play(window, driver, recode, **args)


class nextPageStruct(Struct):
    """
    TODO:nextPageStuct

    Args:
        Struct ([type]): [description]
    """
    fields = {}

    def play(self, window, driver, recode=[], **args):
        super().play(window, driver, recode=recode, **args)
        nextPage = True
        while nextPage:
            nextPage = False
            for op in self.operations:
                item = op.item
                # if not isinstance(op, Struct):
                #     item.setBackground(0, QBrush(QColor("#0000FF")))
                while not window.isworking:
                    sleep(0.1)
                op.play(window, driver, recode, **args)
            for t in ['下页', '下一页']:
                try:
                    element = driver.find_element_by_link_text(t)
                    element.click()
                    nextPage = True

                    break
                except:
                    continue


class rightTagLeft(Struct):
    def play(self, window, driver, recode=[], **args):
        super().play(window, driver, recode=recode, **args)
        while driver.current_window_handle != driver.window_handles[-1]:
            for op in self.operations:
                item = op.item
                # if not isinstance(op, Struct):
                #     item.setBackground(0, QBrush(QColor("#0000FF")))
                while not window.isworking:
                    sleep(0.1)
                op.play(window, driver, recode, **args)


class forRangeStruct(Struct):
    """
    TODO:forWhileStruct

    Args:
        Struct ([type]): [description]
    """
    fields = {
        'start': intField(0, False, 'int'),
        'stop': intField(10, False, 'int'),
        'step': intField(1, False, 'int')
    }

    def play(self, window, driver, recode=[], **args):
        super().play(window, driver, recode, **args)

        for i in range(self.v['start'], self.v['stop'], self.v['step']):
            for op in self.operations:
                item = op.item
                # if not isinstance(op, Struct):
                #     item.setBackground(0, QBrush(QColor("#0000FF")))
                while not window.isworking:
                    sleep(0.1)
                op.play(window, driver, recode, **args)

                # if not isinstance(op, Struct):
                #     item.setBackground(0, QBrush(QColor("#0000FF")))


class readCsvStruct(Struct):
    """
    TODO:readFileStruct

    Args:
        Struct ([type]): [description]
    """
    fields = {
        'Csv': fileField('test.csv'),
        'WithHeader': selectField([True, False])
    }

    def play(self, window, driver, recode=[], **args):
        super().play(window, driver, recode, **args)

        with open(self.v['Csv'], 'r', encoding='utf-8') as f:
            f_csv = reader(f)
            i = 0
            recodes = list(f_csv)
        if self.v['WithHeader']:
            header = recodes[0]
            recodes = recodes[1:]

        for recode in recodes:
            if self.v['WithHeader']:
                recode = dict(zip(header, recode))
            for op in self.operations:
                item = op.item
                # if not isinstance(op, Struct):
                #     item.setBackground(0, QBrush(QColor("#0000FF")))
                while not window.isworking:
                    sleep(0.1)
                op.play(window, driver, recode, **args)

                # if not isinstance(op, Struct):
                #     item.setBackground(0, QBrush(QColor("#0000FF")))


class AsequentialStruct(Struct):
    """
    TODO:顺序结构
    Args:
        Struct ([type]): [description]
    """
    def play(self, window, driver, recode=[], **args):
        super().play(window, driver, recode, **args)
        for op in self.operations:
            item = op.item
            while not window.isworking:
                sleep(0.1)
            op.play(window, driver, recode, **args)

    def play(self, window, driver, recode=[], **args):
        super().play(window, driver, recode, **args)
        初始化表达式
        while 控制表达式:
            for op in self.operations:
                while not window.isworking:
                    暂停一段时间
                op.play(window, driver, recode, **args)
            更新表达式