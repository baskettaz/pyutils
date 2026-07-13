# ===============================================================================================================================================================
# ===============================================================================================================================================================
# ===============================================================================================================================================================
from dataclasses import dataclass

# TO BE REORGANIZED

# NB: To be used as basis with the combination of dataclass for the
#     easy init + type check, somewhat pydantic, but much simpler


# structure with args only
class Structure:
    _fields = []
    def __init__(self, *args):
        if len(args)!=len(self._fields):
            raise TypeError("Expected {} arguments".format(len(self._fields)))

        for name, value in zip(self._fields, args):
            setattr(self, name, value)

# structure with args and kwargs
class Structure2:
    _fields = []

    def __init__(self, *args, **kwargs):
        if len(args) > len(self._fields):
            raise TypeError('Expected {} arguments'.format(len(self._fields)))

        # set all positional arguments
        for name, value in zip(self._fields, args):
            setattr(self, name, value)

        # set remaining keyword arguments
        for name in self._fields[len(args):]:
            setattr(self, name, kwargs.pop(name))

        if kwargs:
            raise TypeError("Invalid argument(s): {}".format("|".join(kwargs)))

# ===============================================================================================================================================================
# ===============================================================================================================================================================
# ===============================================================================================================================================================

if __name__ == '__main__':
    class Stock(Structure2):
        _fields = ["name", "shares", "price"]

        def __str__(self):
            return "\n".join(["%5s=%-10s"% (i, getattr(self,i)) for i in self._fields])

    c = Stock("ACME", 50, price=91.1)
    print(c)


from inspect import signature
from functools import wraps

def typeassert(*ty_args, **ty_kwargs):
    # <NB!>SUBTLE ASPECT:
    # -------------------
    # 1) the solution do not get applied to unsupplied arguments
    # with default values;
    def decorate(func):
        # ATTENTION: if in optimized mode, disable type checking
        # ------------------------------------------------------
        # in certain cases you may want to disable the functio-
        # nality added by a decorator. To do this return the func-
        # tion unwrapped (.__wrapped__) or use the trick below;
        # the optimized mode will return the function unwrapped :
        # -o or -oo in the interpreter
        if not __debug__:
            return func

        # map function argument names to supplied types
        sig = signature(func)
        bound_types = sig.bind_partial(*ty_args, **ty_kwargs).arguments

        @wraps(func)
        def wrapper(*args, **kwargs):
            bound_values = sig.bind(*args, **kwargs)
            # enforce type assertion across supplied arguments
            for name, value in bound_values.arguments.items():
                if name in bound_types:
                    if not isinstance(value, bound_types[name]):
                        raise TypeError("Argument {} must be {}".format(name, bound_types[name]))
            return func(*args, **kwargs)
        return wrapper
    return decorate

if __name__ == '__main__':
    @typeassert(int, z=int)
    def spam(x, y ,z=42):
        print(x, y, z)

    spam(1,2,3)
    spam(1, 2, "bob")

# ===============================================================================================================================================================
# ===============================================================================================================================================================
# ===============================================================================================================================================================

class Spam:
    def __init__(self, name):
        self.name = name

a = Spam("Guido")
a = Spam("Diana")
# =====================================================
# to customize the step of instance creation, you should reimplement __call__()

# EXAMPLE 1 - no instance
# =======================
class NoInstances(type):
    # the metaclass prohibits the instance-creation
    def __call__(cls, *args, **kwargs):
        raise TypeError("Can't instantiate directly!")

class Spam2(metaclass=NoInstances):
    @staticmethod
    def grok(x):
        print("Spam.grok")
# =====================================================

# EXAMPLE 2 - no instance
# =======================

class Singleton(type):
    def __init__(self, *args, **kwargs):
        self.__instance = None
        super().__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        if self.__instance is None:
            print(self.__mro__)
            print(super().__name__)
            self.__instance = super().__call__(*args, **kwargs)
            return self.__instance
        else:
            return self.__instance

class Spam3(metaclass=Singleton):
    def __init__(self):
        print("Creating Spam")
# =====================================================

# EXAMPLE 3 - cached instances
# ============================
import weakref
class Cached(type):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__cache = weakref.WeakValueDictionary()

    def __call__(self, *args, **kwargs):
        if args in self.__cache:
            return self.__cache[args]
        else:
            obj = super().__call__(*args, **kwargs)
            self.__cache[args] = obj
            return obj

class Spam4(metaclass=Cached):
    def __init__(self, name):
        print("Creating Spam4 {!r}".format(name))
        self.name = name

if __name__ == '__main__':
    # Spam2.grok(42)
    # s = Spam2()

    # a = Spam3()
    # b = Spam3()
    # print("a is b ? : ", a is b)

    a = Spam4("Guido")
    b = Spam4("Diana")
    c = Spam4("Diana")
    print("a is b? ", a is b)
    print("b is c? ", b is c)

# ===============================================================================================================================================================
# ===============================================================================================================================================================
# ===============================================================================================================================================================

# metaclass that uses OrderedDict for the class body
class OrderedMeta(type):
    def __new__(cls, clsname, bases, clsdict):
        d = dict(clsdict) # up to this point, we need a OrderedDict()
                          # afterwards will be turned to normal dict()
                          # smart trick !
        order = []
        for name, value in clsdict.items():
            if isinstance(value, Typed):
                value._name = name
                order.append(name)
        d["_order"] = order # extracted from the cls_dict and stored into cls_attr "_order"
        return type.__new__(cls, clsname, bases, d)

    @classmethod
    def __prepare__(cls, clsname, bases):
        return OrderedDict()


class Structure(metaclass=OrderedMeta):
    def as_csv(self):
        return ",".join(str(getattr(self, name)) for name in self._order)

if __name__ == '__main__':
    class Stock(Structure):
        name = String()
        shares = Integer()
        price = Float()
        def __init__(self, name, shares, price):
            self.name = name
            self.shares = shares
            self.price = price


    s = Stock("GOOG", 100, 490.1)
    print(s.name)
    print(s.as_csv())
    print("="*15)
    print(s.__dict__)
    print(type(s).__dict__)
    print("="*15)
    from pprint import pp
    inst_dict = s.__dict__
    cls_dict = type(s).__dict__
    pp({k:cls_dict[k] for k in inst_dict if k in cls_dict})
    print("=" * 15)

# ===============================================================================================================================================================
# ===============================================================================================================================================================
# ===============================================================================================================================================================


# metaclass with optional arguments, to control or
# configure the processing during type creation

# IMPLEMENTATION STRATEGY !!! - this pattern is a must !
# ======================================================

# e.g
# ---
# to support Spam() creation the pattern must be fulfilled !
class MyMeta(type):
    # Optional
    @classmethod
    def __prepare__(cls, name, bases, *, debug=False, synchronize=False):
        # Custom processing
        ...
        return super().__prepare__(name, bases)
    # Required
    def __new__(cls, name, bases, ns, *, debug=False, synchronize=False):
        # Custom processing
        ...
        return super().__new__(cls, name, bases, ns)
    # Required
    def __init__(self, name, bases, ns, *, debug=False, synchronize=False):
        # Custom processing
        ...
        super().__init__(name, bases, ns)

# implemented class with additional kwargs supplied
# VARIATION 1:
class Spam(metaclass=MyMeta, debug=True, synchronize=True):
    ...

# VARIATION 2:
class Spam(metaclass=MyMeta):
    debug = True
    synchronize = True
    ...

# <NB!> SUBTLE DIFFERENCE !
# =========================
# In VARIATOIN 1 the parameters are available in __prepare__(), which runs prioer to any
# statement in the class body.

# In VARIATION 2 the class variables would only be accessible in the __new__() and __init__()


# ===============================================================================================================================================================
# ===============================================================================================================================================================
# ===============================================================================================================================================================

from inspect import Signature, Parameter

def make_sig(*names):
    parms = [Parameter(name, Parameter.POSITIONAL_OR_KEYWORD) for name in names]
    return Signature(parms)

class Structure:
    __signature__ = make_sig()
    def __init__(self, *args, **kwargs):
        bound_values = self.__signature__.bind(*args, **kwargs)
        for name, value in bound_values.arguments.items():
            setattr(self, name, value)

# or with metaclass ...
class StructureMeta(type):
    def __new__(cls, clsname, bases, clsdict):
        clsdict["__signature__"] = make_sig(*clsdict.get("_fields", []))
        return super().__new__(cls, clsname, bases, clsdict)

class Structure2(metaclass=StructureMeta):
    #__signature__ is a special attribute, which will be seen from inspect.signature
    # otherwise it won't be shown properly !, that's why the metaclass here, just to
    # ensure that the __signature__ is available
    _fields = []
    def __init__(self, *args, **kwargs):
        bound_values = self.__signature__.bind(*args, **kwargs)
        for name, value in bound_values.arguments.items():
            setattr(self, name, value)

if __name__ == '__main__':
    class Stock(Structure):
        __signature__ = make_sig("name", "shares", "price")

    class Stock2(Structure2):
        _fields = ["name", "shares", "price"]

    import inspect
    print("inspect 2:", inspect.signature(Stock2))


# ===============================================================================================================================================================
# ===============================================================================================================================================================
# ===============================================================================================================================================================


class NoMixedCaseMeta(type):
    def __new__(cls, clsname, bases, clsdict):
        for name in clsdict.keys():
            if name.lower() != name:
                raise TypeError("Bad attribute name: " + name)
        return super().__new__(cls, clsname, bases, clsdict)

class Root(metaclass=NoMixedCaseMeta):
    pass

class A(Root):
    def foo_bar(self):
        pass

# class B(Root):
#     def fooBar(self):
#         pass


# ANOTHER EXAMPLE

from inspect import signature
import logging

class MatchSignaturesMeta(type):
    # matches the method signatures
    def __init__(self, clsname, bases, clsdict):
        super().__init__(clsname, bases, clsdict)
        sup = super(self, self)
        for name, value in clsdict.items():
            if name.startswith("_") or not callable(value):
                continue
            # get the previous definition (if any) and compare the signatures
            prev_dfn = getattr(sup, name, None)
            if prev_dfn:
                prev_sig = signature(prev_dfn)
                val_sig = signature(value)
                if prev_sig !=val_sig:
                    logging.warning("Signature mismatch in %s. %s != %s",
                                    value.__qualname__, prev_sig, val_sig)


class Root2(metaclass=MatchSignaturesMeta):
    pass

class A2(Root2):
    def foo(self, x, y):
        pass

    def spam(self, x, *, z):
        pass

class B2(A2):
    def foo(self, a, b):
        pass

    def spam(self, x, z):
        pass

if __name__ == '__main__':

    a = A() # OK
    #b = B() #TypeError !

# ===============================================================================================================================================================
# ===============================================================================================================================================================
# ===============================================================================================================================================================

import inspect
import types

class MultiMethod:
    """
    Represents a single multimethod ...
    """
    def __init__(self, name):
        self._methods = {}
        self.__name__ = name

    def register(self, meth):
        """
        Register a new method as a multimethod
        """
        sig = inspect.signature(meth)

        # build a type signature from the method's annotations
        types = []
        for name, parm in sig.parameters.items():
            if name == "self":
                continue

            if parm.annotation is inspect.Parameter.empty:
                raise TypeError("Argument {} must be annotated with a type".format(name))

            if not isinstance(parm.annotation, type):
                raise TypeError("Argument {} annotation must be a type".format(name))

            if parm.default is not inspect.Parameter.empty:
                self._methods[tuple(types)] = meth

            types.append(parm.annotation)

        self._methods[tuple(types)] = meth

    def __call__(self, *args):
        """
        Call a method based on type signature of the arguments
        """
        types = tuple(type(arg) for arg in args[1:])
        meth = self._methods.get(types,None)
        if meth:
            return meth(*args)
        else:
            raise TypeError("No matching method for types {}".format(types))

    def __get__(self, instance, cls):
        """
        Descriptor method needed to make calls work in a class
        """
        if instance is not None:
            return types.MethodType(self, instance)
        else:
            return self

class MultiDict(dict):
    """
    Special dictionary to build multimethods in a metaclass
    """
    def __setitem__(self, key, value):
        if key in self:
            # if key already exists, it must be a multimethod or callable
            current_value = self[key]
            if isinstance(current_value, MultiMethod):
                current_value.register(value)
            else:
                mvalue = MultiMethod(key)
                mvalue.register(current_value)
                mvalue.register(value)
                super().__setitem__(key, mvalue)
        else:
            super().__setitem__(key, value)


class MultiMeta(type):
    """
    Metaclass that allows multiple dispatch of methods
    """
    def __new__(cls, clsname, bases, clsdict):
        return type.__new__(cls,clsname, bases, dict(clsdict))

    @classmethod
    def __prepare__(cls, clsname, bases):
        return MultiDict()


# =================================================================
# ALTERNATIVE WITH DECORATOR (for me is much more elegant then the
# solution with the metaclasses ....)
# =================================================================
class multimethod:
    def __init__(self, func):
        self._methods = {}
        self.__name__ = func.__name__
        self._default = func

    def match(self, *types):
        def register(func):
            ndefaults = len(func.__defaults__) if func.__defaults__ else 0
            for n in range(ndefaults + 1):
                self._methods[types[:len(types) - n]] = func
            return self
        return register

    def __call__(self, *args):
        types = tuple(type(arg) for arg in args[1:])
        meth = self._methods.get(types, None)
        if meth:
            return meth(*args)
        else:
            return self._default(*args)

    def __get__(self, instance, cls):
        if instance is not None:
            return types.MethodType(self, instance)
        else:
            return self


if __name__ == '__main__':
    # simple usage of the metaclass
    class Spam(metaclass=MultiMeta):
        def bar(self, x:int, y:int):
            print("Bar 1: ", x, y)

        def bar(self, s:str, n:int=0):
            print("Bar 2: ", s, n)

    s1  = Spam()
    s1.bar(100,100)
    s1.bar("kur")

    # example of overloading __init__
    import time
    class Date(metaclass=MultiMeta):
        def __init__(self, year:int, month:int, day:int):
            self.year = year
            self.month = month
            self.day = day

        def __init__(self):
            t = time.localtime()
            self.__init__(t.tm_year, t.tm_mon, t.tm_mday)

    d = Date(1988,12,21)
    print(d.year)
    e = Date()
    print(e.year)

    # ALTERNATIVE WITH DECORATOR

    class Spam2:
        @multimethod
        def bar(self, *args):
            # defaulf method called if no match
            raise TypeError("No matching method for bar")

        @bar.match(int, int)
        def bar(self, x, y):
            print("Bar 1: ", x, y)

        @bar.match(str, int)
        def bar(self, s, n = 0):
            print("Bar 2: ", s, n)

    print("="*25)
    s2 = Spam2()
    s2.bar(10, 10)
    s2.bar("blups", 100)


# ===============================================================================================================================================================
# ===============================================================================================================================================================
# ===============================================================================================================================================================

def typed_property(name, expected_type):
    storage_name = "_" + name

    @property
    def prop(self):
        return getattr(self,storage_name)

    @prop.setter
    def prop(self, value):
        if not isinstance(value, expected_type):
            raise TypeError("{} must be a {}".format(name, expected_type))
        setattr(self, storage_name, value)
    return prop

if __name__ == '__main__':
    #example use
    class Person:
        name = typed_property("name", str)
        age = typed_property("age", int)
        def __init__(self, name, age):
            self.name = name
            self.age = age

    # nice perk :
    from functools import partial

    String = partial(typed_property, expected_type=str)
    Integer = partial(typed_property, expected_type=int)

    class Person2:
        name = String("name")
        age = Integer("age")
        def __init__(self, name, age):
            self.name = name
            self.age = age
