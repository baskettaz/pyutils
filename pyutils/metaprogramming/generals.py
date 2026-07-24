import inspect
from functools import wraps
from functools import lru_cache
from inspect import (
    signature,
    Parameter,
    Signature,
)

import weakref


class PosArgsOnlyCls:
    """
    A simple structure class that accepts only positional arguments.

    Example:
        >>> class Point(PosArgsOnlyCls):
        ...     _fields = ['x', 'y']

        >>> p = Point(10, 20)
        >>> print(p.x)  # 10
    """

    _fields = []

    def __init__(self, *args):
        if len(args) != len(self._fields):
            raise TypeError("Expected {} arguments".format(len(self._fields)))

        for name, value in zip(self._fields, args):
            setattr(self, name, value)


class PosArgsKwargsCls:
    """
    A structure class accepting positional and keyword arguments for field initialization.

    Define _fields as a list of field names in subclasses. Fields can be set via positional
    args (in order), keyword args, or both. All fields must be provided; no defaults.

    Raises:
        TypeError: If too many positional args, missing required fields, or invalid kwargs.

    Example:
        >>> class Stock(PosArgsKwargsCls):
        ...     _fields = ["name", "shares", "price"]

        >>> s = Stock("ACME", 50, price=91.1)
        >>> s.name, s.shares, s.price
        ('ACME', 50, 91.1)
    """

    _fields = []

    def __init__(self, *args, **kwargs):
        if len(args) > len(self._fields):
            raise TypeError("Expected {} arguments".format(len(self._fields)))

        # set all positional arguments
        for name, value in zip(self._fields, args):
            setattr(self, name, value)

        # set remaining keyword arguments
        for name in self._fields[len(args) :]:
            if name in kwargs:
                setattr(self, name, kwargs.pop(name))

        if kwargs:
            raise TypeError("Invalid argument(s): {}".format("|".join(kwargs)))


def assert_func_types(*ty_args, **ty_kwargs):
    """
    Decorator factory that enforces runtime type checks on a function's arguments.

    Usage:
        - Positional type specifications (``*ty_args``) are matched to parameter
          names by position using the decorated function's signature.
        - Keyword type specifications (``**ty_kwargs``) map parameter names to
          expected types directly.

    Behavior:
        - If Python is running with optimizations enabled (``__debug__ is False``),
          the decorator is a no-op and returns the original function.
        - The decorator binds the supplied type specifications to the function's
          parameter names using ``inspect.signature`` and ``bind_partial``.
        - At call time the wrapper binds actual call arguments to parameter names
          and checks any parameters that have an expected type. A ``TypeError``
          is raised when a value does not match the expected type.

    Notes:
        - The implementation currently requires the number of positional type
          specifications (``ty_args``) to equal the number of positional
          arguments supplied at call time; supply positional types accordingly.
        - ``ty_kwargs`` keys must match parameter names of the decorated function.

    Raises:
        TypeError: on mismatch between provided types and runtime arguments or
                   when an argument value is not an instance of the expected type.

    Example:
        >>> @assert_func_types(int, z=int)
        >>> def spam(x, y, z=42):
        ...    print(x, y, z)

        >>> spam(1, 2, 3)       # OK
        >>> spam(1, 2, "bob")   # Raises TypeError for z
    """

    def decorate(func):
        # If in optimized mode, disable type checking
        if not __debug__:
            return func

        # map function argument names to supplied types
        sig = signature(func)
        bound_types = sig.bind_partial(*ty_args, **ty_kwargs).arguments

        @wraps(func)
        def wrapper(*args, **kwargs):
            # Note:
            # =====
            # Intentionally hardened behavior to make the ty_args per argument explicit
            if len(ty_args) != len(args):
                raise TypeError(
                    f"Expected equal number of types and args ({len(ty_args)} != {len(args)}): {ty_args!r} | {args!r}"
                )

            bound_values = sig.bind(*args, **kwargs)
            # enforce type assertion across supplied arguments
            for name, value in bound_values.arguments.items():
                if name in bound_types:
                    if not isinstance(value, bound_types[name]):
                        raise TypeError("Argument {} must be {}".format(name, bound_types[name]))
            return func(*args, **kwargs)

        return wrapper

    return decorate


class NoInstances(type):
    # the metaclass prohibits the instance-creation
    def __call__(cls, *args, **kwargs):
        raise TypeError("Can't instantiate directly!")


class Singleton(type):
    # Metaclass that ensures only one instance of a class exists

    def __init__(self, *args, **kwargs):
        self.singled = None
        super().__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        # Return existing instance or create new one on first call.
        if self.singled is None:
            self.singled = super().__call__(*args, **kwargs)
        return self.singled


class Cached(type):
    """
    Metaclass that caches instances by their __init__ argument values.

    Behavior
    - When a class uses this metaclass, calling Class(*args, **kwargs) returns a
      cached instance if one was previously created with the same bound
      initialization arguments; otherwise a new instance is created and cached.
    - Cache keys are computed by binding the call to the class's __init__ signature
      (default values applied) and using ``tuple(bound.arguments.items())`` with
      the ``self`` entry removed.

    Implementation notes
    - A per-class weak-value cache is created in the metaclass ``__init__`` (each
      class gets a ``cache`` attribute). Entries are removed automatically when
      objects are garbage-collected.
    - Keys must be hashable; using unhashable init arguments (e.g. ``list`` or
      ``dict``) will raise ``TypeError`` when attempting to use them as cache keys.

    Limitations / Caveats
    - Not thread-safe: concurrent creations can race and produce duplicate
      instances or corrupt the cache. Wrap cache access with a lock if used from
      multiple threads.
    - Equality of instances is determined solely by bound init-argument identity.
      If ``__init__`` has side effects or depends on external state, caching may
      be inappropriate.
    """

    def make_keys(cls, *args, **kwargs) -> tuple:
        sig = inspect.signature(cls.__init__)
        bound = sig.bind(None, *args, **kwargs)  # None represents self
        bound.apply_defaults()
        bound.arguments.pop("self")

        return tuple(bound.arguments.items())

    def __init__(cls, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        cls.cache = weakref.WeakValueDictionary()

    def __call__(cls, *args, **kwargs):
        keys = cls.make_keys(*args, **kwargs)
        if not keys in cls.cache:
            obj = super().__call__(*args, **kwargs)
            cls.cache[keys] = obj

        return cls.cache[keys]



# # metaclass that uses OrderedDict for the class body
# class OrderedMeta(type):
#     def __new__(cls, clsname, bases, clsdict):
#         d = dict(clsdict)  # up to this point, we need a OrderedDict()
#         # afterwards will be turned to normal dict()
#         # smart trick !
#         order = []
#         for name, value in clsdict.items():
#             if isinstance(value, Typed):
#                 value._name = name
#                 order.append(name)
#         d["_order"] = order  # extracted from the cls_dict and stored into cls_attr "_order"
#         return type.__new__(cls, clsname, bases, d)
#
#     @classmethod
#     def __prepare__(cls, clsname, bases):
#         return OrderedDict()
#
#
# class Structure(metaclass=OrderedMeta):
#     def as_csv(self):
#         return ",".join(str(getattr(self, name)) for name in self._order)
#
#
# if __name__ == "__main__":
#
#     class Stock(Structure):
#         name = String()
#         shares = Integer()
#         price = Float()
#
#         def __init__(self, name, shares, price):
#             self.name = name
#             self.shares = shares
#             self.price = price
#
#     s = Stock("GOOG", 100, 490.1)
#     print(s.name)
#     print(s.as_csv())
#     print("=" * 15)
#     print(s.__dict__)
#     print(type(s).__dict__)
#     print("=" * 15)
#     from pprint import pp
#
#     inst_dict = s.__dict__
#     cls_dict = type(s).__dict__
#     pp({k: cls_dict[k] for k in inst_dict if k in cls_dict})
#     print("=" * 15)
#
#
# # metaclass with optional arguments, to control or
# # configure the processing during type creation
#
# # IMPLEMENTATION STRATEGY !!! - this pattern is a must !
# # ======================================================
#
#
# # e.g
# # ---
# # to support Spam() creation the pattern must be fulfilled !
# class MyMeta(type):
#     # Optional
#     @classmethod
#     def __prepare__(cls, name, bases, *, debug=False, synchronize=False):
#         # Custom processing
#         ...
#         return super().__prepare__(name, bases)
#
#     # Required
#     def __new__(cls, name, bases, ns, *, debug=False, synchronize=False):
#         # Custom processing
#         ...
#         return super().__new__(cls, name, bases, ns)
#
#     # Required
#     def __init__(self, name, bases, ns, *, debug=False, synchronize=False):
#         # Custom processing
#         ...
#         super().__init__(name, bases, ns)
#
#
# # implemented class with additional kwargs supplied
# # VARIATION 1:
# class Spam(metaclass=MyMeta, debug=True, synchronize=True): ...
#
#
# # VARIATION 2:
# class Spam(metaclass=MyMeta):
#     debug = True
#     synchronize = True
#     ...
#
#
# # <NB!> SUBTLE DIFFERENCE !
# # =========================
# # In VARIATOIN 1 the parameters are available in __prepare__(), which runs prioer to any
# # statement in the class body.
#
# # In VARIATION 2 the class variables would only be accessible in the __new__() and __init__()
#
#
#
#
# def make_sig(*names):
#     parms = [Parameter(name, Parameter.POSITIONAL_OR_KEYWORD) for name in names]
#     return Signature(parms)
#
#
# class Structure:
#     __signature__ = make_sig()
#
#     def __init__(self, *args, **kwargs):
#         bound_values = self.__signature__.bind(*args, **kwargs)
#         for name, value in bound_values.arguments.items():
#             setattr(self, name, value)
#
#
# # or with metaclass ...
# class StructureMeta(type):
#     def __new__(cls, clsname, bases, clsdict):
#         clsdict["__signature__"] = make_sig(*clsdict.get("_fields", []))
#         return super().__new__(cls, clsname, bases, clsdict)
#
#
# class Structure2(metaclass=StructureMeta):
#     # __signature__ is a special attribute, which will be seen from inspect.signature
#     # otherwise it won't be shown properly !, that's why the metaclass here, just to
#     # ensure that the __signature__ is available
#     _fields = []
#
#     def __init__(self, *args, **kwargs):
#         bound_values = self.__signature__.bind(*args, **kwargs)
#         for name, value in bound_values.arguments.items():
#             setattr(self, name, value)
#
#
# if __name__ == "__main__":
#
#     class Stock(Structure):
#         __signature__ = make_sig("name", "shares", "price")
#
#     class Stock2(Structure2):
#         _fields = ["name", "shares", "price"]
#
#     import inspect
#
#     print("inspect 2:", inspect.signature(Stock2))
#
#
# class NoMixedCaseMeta(type):
#     def __new__(cls, clsname, bases, clsdict):
#         for name in clsdict.keys():
#             if name.lower() != name:
#                 raise TypeError("Bad attribute name: " + name)
#         return super().__new__(cls, clsname, bases, clsdict)
#
#
# class Root(metaclass=NoMixedCaseMeta):
#     pass
#
#
# class A(Root):
#     def foo_bar(self):
#         pass
#
#
# # class B(Root):
# #     def fooBar(self):
# #         pass
#
#
# # ANOTHER EXAMPLE
#
# import logging
#
#
# class MatchSignaturesMeta(type):
#     # matches the method signatures
#     def __init__(self, clsname, bases, clsdict):
#         super().__init__(clsname, bases, clsdict)
#         sup = super(self, self)
#         for name, value in clsdict.items():
#             if name.startswith("_") or not callable(value):
#                 continue
#             # get the previous definition (if any) and compare the signatures
#             prev_dfn = getattr(sup, name, None)
#             if prev_dfn:
#                 prev_sig = signature(prev_dfn)
#                 val_sig = signature(value)
#                 if prev_sig != val_sig:
#                     logging.warning("Signature mismatch in %s. %s != %s", value.__qualname__, prev_sig, val_sig)
#
#
# class Root2(metaclass=MatchSignaturesMeta):
#     pass
#
#
# class A2(Root2):
#     def foo(self, x, y):
#         pass
#
#     def spam(self, x, *, z):
#         pass
#
#
# class B2(A2):
#     def foo(self, a, b):
#         pass
#
#     def spam(self, x, z):
#         pass
#
#
# if __name__ == "__main__":
#     a = A()  # OK
#     # b = B() #TypeError !
#
#
# import types
#
#
# class MultiMethod:
#     """
#     Represents a single multimethod ...
#     """
#
#     def __init__(self, name):
#         self._methods = {}
#         self.__name__ = name
#
#     def register(self, meth):
#         """
#         Register a new method as a multimethod
#         """
#         sig = inspect.signature(meth)
#
#         # build a type signature from the method's annotations
#         types = []
#         for name, parm in sig.parameters.items():
#             if name == "self":
#                 continue
#
#             if parm.annotation is inspect.Parameter.empty:
#                 raise TypeError("Argument {} must be annotated with a type".format(name))
#
#             if not isinstance(parm.annotation, type):
#                 raise TypeError("Argument {} annotation must be a type".format(name))
#
#             if parm.default is not inspect.Parameter.empty:
#                 self._methods[tuple(types)] = meth
#
#             types.append(parm.annotation)
#
#         self._methods[tuple(types)] = meth
#
#     def __call__(self, *args):
#         """
#         Call a method based on type signature of the arguments
#         """
#         types = tuple(type(arg) for arg in args[1:])
#         meth = self._methods.get(types, None)
#         if meth:
#             return meth(*args)
#         else:
#             raise TypeError("No matching method for types {}".format(types))
#
#     def __get__(self, instance, cls):
#         """
#         Descriptor method needed to make calls work in a class
#         """
#         if instance is not None:
#             return types.MethodType(self, instance)
#         else:
#             return self
#
#
# class MultiDict(dict):
#     """
#     Special dictionary to build multimethods in a metaclass
#     """
#
#     def __setitem__(self, key, value):
#         if key in self:
#             # if key already exists, it must be a multimethod or callable
#             current_value = self[key]
#             if isinstance(current_value, MultiMethod):
#                 current_value.register(value)
#             else:
#                 mvalue = MultiMethod(key)
#                 mvalue.register(current_value)
#                 mvalue.register(value)
#                 super().__setitem__(key, mvalue)
#         else:
#             super().__setitem__(key, value)
#
#
# class MultiMeta(type):
#     """
#     Metaclass that allows multiple dispatch of methods
#     """
#
#     def __new__(cls, clsname, bases, clsdict):
#         return type.__new__(cls, clsname, bases, dict(clsdict))
#
#     @classmethod
#     def __prepare__(cls, clsname, bases):
#         return MultiDict()
#
#
# # =================================================================
# # ALTERNATIVE WITH DECORATOR (for me is much more elegant then the
# # solution with the metaclasses ....)
# # =================================================================
# class multimethod:
#     def __init__(self, func):
#         self._methods = {}
#         self.__name__ = func.__name__
#         self._default = func
#
#     def match(self, *types):
#         def register(func):
#             ndefaults = len(func.__defaults__) if func.__defaults__ else 0
#             for n in range(ndefaults + 1):
#                 self._methods[types[: len(types) - n]] = func
#             return self
#
#         return register
#
#     def __call__(self, *args):
#         types = tuple(type(arg) for arg in args[1:])
#         meth = self._methods.get(types, None)
#         if meth:
#             return meth(*args)
#         else:
#             return self._default(*args)
#
#     def __get__(self, instance, cls):
#         if instance is not None:
#             return types.MethodType(self, instance)
#         else:
#             return self
#
#
# if __name__ == "__main__":
#     # simple usage of the metaclass
#     class Spam(metaclass=MultiMeta):
#         def bar(self, x: int, y: int):
#             print("Bar 1: ", x, y)
#
#         def bar(self, s: str, n: int = 0):
#             print("Bar 2: ", s, n)
#
#     s1 = Spam()
#     s1.bar(100, 100)
#     s1.bar("kur")
#
#     # example of overloading __init__
#     import time
#
#     class Date(metaclass=MultiMeta):
#         def __init__(self, year: int, month: int, day: int):
#             self.year = year
#             self.month = month
#             self.day = day
#
#         def __init__(self):
#             t = time.localtime()
#             self.__init__(t.tm_year, t.tm_mon, t.tm_mday)
#
#     d = Date(1988, 12, 21)
#     print(d.year)
#     e = Date()
#     print(e.year)
#
#     # ALTERNATIVE WITH DECORATOR
#
#     class Spam2:
#         @multimethod
#         def bar(self, *args):
#             # defaulf method called if no match
#             raise TypeError("No matching method for bar")
#
#         @bar.match(int, int)
#         def bar(self, x, y):
#             print("Bar 1: ", x, y)
#
#         @bar.match(str, int)
#         def bar(self, s, n=0):
#             print("Bar 2: ", s, n)
#
#     print("=" * 25)
#     s2 = Spam2()
#     s2.bar(10, 10)
#     s2.bar("blups", 100)
#
#
# def typed_property(name, expected_type):
#     storage_name = "_" + name
#
#     @property
#     def prop(self):
#         return getattr(self, storage_name)
#
#     @prop.setter
#     def prop(self, value):
#         if not isinstance(value, expected_type):
#             raise TypeError("{} must be a {}".format(name, expected_type))
#         setattr(self, storage_name, value)
#
#     return prop
#
#
# if __name__ == "__main__":
#     # example use
#     class Person:
#         name = typed_property("name", str)
#         age = typed_property("age", int)
#
#         def __init__(self, name, age):
#             self.name = name
#             self.age = age
#
#     # nice perk :
#     from functools import partial
#
#     String = partial(typed_property, expected_type=str)
#     Integer = partial(typed_property, expected_type=int)
#
#     class Person2:
#         name = String("name")
#         age = Integer("age")
#
#         def __init__(self, name, age):
#             self.name = name
#             self.age = age
