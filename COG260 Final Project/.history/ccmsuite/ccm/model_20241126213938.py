from __future__ import generators
from __future__ import print_function

from . import scheduler
from . import logger
import random
import inspect
import copy

# import ccm.config as config


class MethodWrapper:
    def __init__(self, obj, func, name):
        self.func = func
        self.obj = obj
        self.func_name = name
        self.begins = scheduler.Trigger(name + " begin")
        self.ends = scheduler.Trigger(name + " end")
        self.default_trigger = self.ends

    def __call__(self, *args, **keys):
        self.obj.sch.trigger(self.begins)
        val = self.func(self.obj, *args, **keys)
        self.obj.sch.trigger(self.ends)
        return val


class MethodGeneratorWrapper(MethodWrapper):
    def _generator(self, *args, **keys):
        self.obj.sch.trigger(self.begins)
        for x in self.func(self.obj, *args, **keys):
            yield x
        self.obj.sch.trigger(self.ends)

    def __call__(self, *args, **keys):
        return self.obj.sch.add(self._generator, args=args, keys=keys)

    def __str__(self):
        return "<MGW %s %s>" % (self.obj, self.func_name)


def log_everything(model, log=None):
    if log is None:
        log = logger.log_proxy
    if not hasattr(model, "log"):
        model.run(limit=0)
    model.log = log
    for k, v in model.__dict__.items():
        if k[0] != "_" and k != "parent":
            if isinstance(v, Model) and v.parent is model:
                log_everything(v, getattr(log, k))


class Model(object):
    __converted = False
    _convert_methods = True
    _auto_run_start = True
    name = "top"

    def __init__(self, log=None, **keys):
        self.__init_log = log
        for k, v in keys.items():
            setattr(self, k, v)

    def __convert(self, parent=None, name=None):
        assert self.__converted == False
        self.__converted = True
        self.changes = scheduler.Trigger()

        if hasattr(self, "parent"):
            parent = self.parent

        methods = {}
        objects = {}

        for k, v in self.__class__.__dict__.items():
            if k[0] != "_":
                if inspect.isfunction(v):
                    if k not in ["run", "now", "get_children"] and k not in methods:
                        methods[k] = v
                else:
                    if inspect.isclass(v) and Model in inspect.getmro(v):
                        v = v()
                    if k not in objects:
                        objects[k] = v
        objects = copy.deepcopy(objects)

        if parent:
            if not parent.__converted:
                parent.__convert()
            self.sch = parent.sch
            self.log = logger.dummy
            self.random = parent.random
            self.parent = parent
        else:
            self.sch = scheduler.Scheduler()
            if self.__init_log is True:
                self.log = logger.log()
            elif self.__init_log is None:
                self.log = logger.dummy
            else:
                self.log = self.__init_log
            self.random = random.Random()
            self.parent = None

        self._convert_info(objects, methods)

        for name, obj in objects.items():
            if isinstance(obj, Model):
                if not obj.__converted:
                    obj.__convert(self, name)
                else:
                    obj.name = name
                try:
                    self._children[name] = obj
                except AttributeError:
                    self._children = {name: obj}
            self.__dict__[name] = obj

        if self._convert_methods:
            for name, func in methods.items():
                if func.__code__.co_flags & 0x20 == 0x20:
                    w = MethodGeneratorWrapper(self, func, name)
                else:
                    w = MethodWrapper(self, func, name)
                self.__
