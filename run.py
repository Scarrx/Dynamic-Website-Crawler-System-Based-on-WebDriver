from sys import argv
from threading import Thread
from PyQt5.Qt import QApplication

from utils import downloadChromeDriver, checkVersionMatch
from extension import Element, Page
from main import MainWindow
# from test import MainWindow
from utils import app

VERSION = '1.0'
DEBUG = False

if __name__ == '__main__':
    qApp = QApplication(argv)
    # window = Window()
    Thread(
        target=app.run,
        daemon=True,
        kwargs={
            #    'debug': DEBUG,
            'ssl_context': 'adhoc'
        }).start()

    window = MainWindow()

    window.show()

    exit(qApp.exec_())
