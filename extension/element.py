from PyQt5.QtWidgets import QMessageBox
from extension.field import selectField
from . import strField, intField, fileField
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
import random


class Element:
    autoLoad = False
    tags = ['div']
    fields = {}

    def __init__(self) -> None:
        self.isRecode = False

    @classmethod
    def name(cls):
        return cls.__name__

    def play(self, window, driver, recode=[], **args):
        print(self, self.name())
        self.vs(recode)
        print(self.v)
        print(self.fields_)

    def load(self, data, fields):
        self.data = data.copy()
        self.fields_ = fields.copy()

    def vs(self, recode):
        self.v = {}
        for fn, f in self.fields.items():
            self.v[fn] = f.load(self.fields_[fn], recode)

    def setItem(self, item):
        self.item = item

    def dumps(self):
        return {
            'super': 'Element',
            'class_': self.name(),
            'fields': self.fields_,
            'data': self.data
        }


class Info(Element):
    autoLoad = False
    tags = ['div', 'input', 'select', 'button', 'textarea']

    def play(self, window, driver, recode=[], **args):
        super().play(window, driver, recode, **args)

        try:
            element = driver.find_element_by_xpath(self.data['seleniumXpath'])
            print(element)
        except:
            pass


class click(Element):
    autoLoad = True
    tags = ['a', 'div']


class InputElement(Element):
    autoLoad = True
    tags = ['input']
    fields = {'TEXT': strField('text')}

    def play(self, window, driver, recode=[], **args):
        super().play(window, driver, recode, **args)
        element = driver.find_element_by_xpath(self.data['seleniumXpath'])
        element.send_keys(self.v['TEXT'])


class SelectSelect(Element):
    autoLoad = True
    tags = ['select']
    fields = {
        'SelectType': selectField(['text', 'index']),
        'TEXT': strField('text')
    }

    def play(self, window, driver, recode=[], **args):
        super().play(window, driver, recode, **args)

        element = driver.find_element_by_xpath(self.data['seleniumXpath'])
        try:
            select = Select(element)
            if self.v['SelectType'] == 'text':
                select.select_by_visible_text(self.v['TEXT'])
            else:
                select.select_by_index(int(self.v['TEXT']))
        except Exception as e:
            window.pauseTask()
            window.info('Something Wrong', f'select {self.v["TEXT"]} wrong')


class SelectTd(Element):
    autoLoad = True
    tags = ['td']
    fields = {'index': intField('text')}

    def play(self, window, driver, recode=[], **args):
        super().play(window, driver, recode, **args)

        element = driver.find_element_by_xpath(self.data['seleniumXpath'])
        try:
            element.find_element_by_tag_name('td')[self.v['index']].click()
        except:
            pass


class UlOpen(Element):
    autoLoad = True
    tags = ['ul']

    fields = {}

    def play(self, window, driver, recode=[], **args):
        super().play(window, driver, recode, **args)
        element = driver.find_element_by_xpath(self.data['seleniumXpath'])
        actions = ActionChains(driver)
        for e in element.find_elements_by_tag_name('a'):
            actions.key_down(Keys.CONTROL).perform()
            e.click()
            actions.key_up(Keys.CONTROL).perform()


class Article(Element):
    autoLoad = True
    tags = ['div']

    fields = {'saveDir': fileField('saveHtml.html')}

    def play(self, window, driver, recode=[], **args):
        super().play(window, driver, recode, **args)
        element = driver.find_element_by_xpath(self.data['seleniumXpath'])
        with open(self.v['saveDir'] + '/' + driver.current_url.split('/')[-1],
                  'a',
                  encoding='utf-8') as f:
            f.write(element.text)
        # element.screenshot(
        #     self.v['saveDir']+'/'+driver.current_url.split('/')[-1]+'.png')

        driver.save_screenshot(self.v['saveDir'] + '/' +
                               driver.current_url.split('/')[-1] + '.png')
