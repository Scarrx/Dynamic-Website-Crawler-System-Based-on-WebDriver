from PyQt5.QtWidgets import QTreeWidgetItem
from . import Field, intField, strField, fileField
from time import sleep

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys


class Page:
    autoLoad = False
    fields = {}

    def __init__(self) -> None:
        pass

    @classmethod
    def name(cls):
        return cls.__name__

    def load(self, fields):
        """
        TODO:针对字典
        """
        self.fields_ = fields.copy()

    def setItem(self, item):
        self.item = item

    def play(self, window, driver, recode=[], **args):
        self.vs(recode)
        print(self, self.name())

    def vs(self, recode):
        self.v = {}
        for fn, f in self.fields.items():
            self.v[fn] = f.load(self.fields_[fn])

    def dumps(self):
        return {'super': 'Page', 'class_': self.name(), 'fields': self.fields_}


class back(Page):
    autoLoad = True

    def play(self, window, driver, recode=[], **args):
        super().play(window, driver, recode, **args)
        driver.back()


class forward(Page):
    autoLoad = True

    def play(self, window, driver, recode=[], **args):
        super().play(window, driver, recode, **args)
        driver.forward()


class deleteAllCookies(Page):
    autoLoad = True

    def play(self, window, driver, recode=[], **args):
        super().play(driver, recode, **args)
        driver.delete_all_cookies()


class Sleep(Page):
    autoLoad = True
    fields = {'sleepTime': intField(1, False, 'sleepTime')}

    def play(self, window, driver, recode=[], **args):
        super().play(window, driver, recode, **args)
        sleep(self.v['sleepTime'])


class waitStart(Page):
    autoLoad = True

    def play(self, window, driver, recode=[], **args):
        super().play(window, driver, recode, **args)
        window.pauseTask()


class get_url(Page):
    autoLoad = True
    fields = {'url': strField('https://www.baidu.com')}

    def play(self, window, driver, recode=[], **args):
        super().play(window, driver, recode=recode, **args)
        driver.get(self.v['url'])


class newTag(Page):
    autoLoad = True

    def play(self, window, driver, recode=[], **args):
        super().play(window, driver, recode=recode, **args)
        js = "window.open()"
        driver.execute_script(js)


class switch_to_next(Page):
    autoLoad = True

    def play(self, window, driver, recode=[], **args):
        super().play(window, driver, recode=recode, **args)
        window_handle = driver.current_window_handle
        handles = driver.window_handles
        index = handles.index(window_handle)
        if index == len(handles) - 1:
            pass
        else:
            driver.switch_to.window(handles[index + 1])


class switch_to_last(Page):
    autoLoad = True

    def play(self, window, driver, recode=[], **args):
        super().play(window, driver, recode=recode, **args)
        window_handle = driver.current_window_handle
        handles = driver.window_handles
        index = handles.index(window_handle)
        if index == 0:
            pass
        else:
            driver.switch_to.window(handles[index - 1])


class clossTag(Page):
    autoLoad = True

    def play(self, window, driver, recode=[], **args):
        super().play(window, driver, recode=recode, **args)
        window_handle = driver.current_window_handle
        handles = driver.window_handles
        index = handles.index(window_handle)
        try:
            driver.close()

            if index == 0:
                driver.switch_to.window(handles[index])
            else:
                driver.switch_to.window(handles[index - 1])
        except Exception as e:
            print(e)


class refresh(Page):
    autoLoad = True

    def play(self, window, driver, recode=[], **args):
        super().play(window, driver, recode=recode, **args)
        driver.refresh()
