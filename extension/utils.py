import importlib
import inspect
import os
import sys


def subClass(class_):
    res = set()
    for i in os.listdir(__package__):
        # print(i)
        if os.path.isdir(os.path.join(__package__, i)) or i in ['__init__.py']:
            continue
        lazyImport = importlib.import_module(
            f'.{i.split(".")[0]}', __package__)

        for name, class__ in inspect.getmembers(lazyImport, inspect.isclass):
            # print(name, class_)
            if issubclass(class_, class__) ^ issubclass(class__, class_):
                res.add(class__)
    return res
