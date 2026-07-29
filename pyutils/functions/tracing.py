import sys
from functools import wraps
import types
from typing import Callable

trace_types = (
    types.MethodType,
    types.FunctionType,
    types.BuiltinFunctionType,
    types.BuiltinMethodType,
    types.MethodDescriptorType,
    types.ClassMethodDescriptorType
)



def trace_func(func):

    if hasattr(func, "tracing"):
        return func

    @wraps(func)
    def wrapper(*args, **kwargs):
        result = None

        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            result = e
            raise
        finally:
            print(f"{func.__name__}() -> {result!r}")

    wrapper.tracing = True
    return wrapper


def trace_class_decorator(klass):
    for key in dir(klass):
        value = getattr(klass, key)
        if isinstance(value, trace_types):
            wrapped = trace_func(value)
            setattr(klass, key, wrapped)
    return klass



class TraceMeta(type):
    def __new__(meta, name, bases, class_dict):
        klass = super().__new__(meta, name, bases, class_dict)

        for key in dir(klass):
            value  = getattr(klass, key)
            if isinstance(value, trace_types):
                wrapped  = trace_func(value)
                setattr(klass, key, wrapped)

        return klass


def trace_everything() -> None:
    """
    Enable low-level frame tracing; logs every line executed via sys.settrace().

    Behavior
    - Registers an inner trace function with sys.settrace() that captures all frame
      events and logs line-level execution details.
    - For each "line" event, logs "{filename}:{lineno}" at DEBUG level via the module logger.
    - Other frame events ("call", "return", "exception") are silently ignored.
    - Once enabled, tracing remains active until sys.settrace(None) is called.
    """
    def trace(frame, event, arg) -> Callable:
        if event == "line":
            print(f"{frame.f_code.co_filename}:{frame.f_lineno}")
        return trace

    sys.settrace(trace)





if __name__ == '__main__':
    trace_everything()
    def bla():
        print('how coool')

    bla()
