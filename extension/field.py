import inspect
import random
from PyQt5.QtWidgets import QComboBox, QLineEdit


class Field:
    def __init__(self, default=1, recode=True, description="") -> None:
        # self.parent = parent
        self.default = default
        self.recode = recode
        self.description = description

    @classmethod
    def name(cls):
        return cls.__name__

    def load(self, data, recode=[]):
        """
        TODO
        """
        return data

    def loads(self, qw):
        """
        TODO:GUI
        """
        return qw.text()

    def askQt(self, parent=None):
        return QLineEdit(parent)


class strField(Field):
    """
    TODO

    Args:
        Field ([type]): [description]
    """

    def load(self, data, recode=[]):
        # return eval('str(f"{data}")')
        try:
            return str(eval(data))
        except:
            return str(data)

    def loads(self, qw):
        if qw.text() == '':
            return False, ''
        else:
            return True, qw.text()


class intField(Field):
    """
    TODO

    Args:
        Field ([type]): [description]
    """

    def load(self, data, recode=[]):
        try:
            return int(eval(data))
        except:
            return int(data)

    def loads(self, qw):
        if qw.text() == '':
            return False, 0
        else:
            return True, qw.text()


class fileField(Field):
    """
    TODO

    Args:
        Field ([type]): [description]
    """

    def load(self, data, recode=[]):
        return eval('str(f"{data}")')

    def loads(self, qw):
        if qw.text() == '':
            return False, ''
        else:
            return True, qw.text()


class selectField(Field):
    def load(self, data, recode=[]):
        return self.default[data]

    def loads(self, qw):
        return True, qw.currentIndex()

    def askQt(self, parent=None):
        qb = QComboBox(parent)
        for i in self.default:
            qb.addItem(str(i))
        return qb
