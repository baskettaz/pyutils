from pyutils.metaprogramming.generals import (
    PosArgsOnlyCls,
    PosArgsKwargsCls,
    assert_func_types,
    NoInstances,
    Singleton,
    Cached,
)

import pytest


def test_pos_args_only_correct():
    class Point(PosArgsOnlyCls):
        _fields = ["x", "y"]

    p = Point(10, 20)
    assert p.x == 10
    assert p.y == 20

    assert len(vars(p)) == 2


def test_pos_args_only_incorrect():
    class Point(PosArgsOnlyCls):
        _fields = ["x", "y"]

    with pytest.raises(TypeError):
        Point(10, 20, 30)

    with pytest.raises(TypeError):
        Point(10)


def test_pos_args_kwargs_correct():
    class Point(PosArgsKwargsCls):
        _fields = ["x", "y"]

    p = Point(10, y=20)
    assert p.x == 10
    assert p.y == 20

    assert len(vars(p)) == 2

    # Note: Special condition no kwargs, but still correct
    p2 = Point(10)
    assert p2.x == 10
    assert len(vars(p2)) == 1


def test_pos_args_kwargs_incorrect():
    class Point(PosArgsKwargsCls):
        _fields = ["x", "y"]

    with pytest.raises(TypeError):
        Point(10, y=20, z=30)

    with pytest.raises(TypeError):
        Point(10, z=20)


def test_assert_func_types_with_args_only():

    @assert_func_types(int, int)
    def dummy_func_correct(x, y):
        return x + y

    assert dummy_func_correct(10, 20) == 30

    with pytest.raises(TypeError):
        dummy_func_correct(10, 20.0)


def test_assert_func_types_with_args_and_kwargs():

    @assert_func_types(int, int, z=int)
    def dummy_func_correct(x, y, z=10):
        return x + y + z

    assert dummy_func_correct(10, 20) == 40
    assert dummy_func_correct(10, 20, z=5) == 35

    with pytest.raises(TypeError):
        dummy_func_correct(10, 20.0)

    with pytest.raises(TypeError):
        dummy_func_correct(10.0, 20)

    with pytest.raises(TypeError):
        dummy_func_correct(10.0, 20, xx=10, yy=20)


def test_no_instance():
    class Dummy(metaclass=NoInstances):
        @staticmethod
        def grok(x):
            print("Spam.grok")

    with pytest.raises(TypeError):
        Dummy()


def test_singleton():
    class Dummy(metaclass=Singleton):
        pass

    d1 = Dummy()
    d2 = Dummy()

    assert id(d1) == id(d2)


def test_cached_object_args_and_kwargs():
    class Dummy(metaclass=Cached):
        def __init__(self, a1, a2, b1=1, b2=2):
            pass

    d1 = Dummy(1, 2, b2=5, b1=6)
    d2 = Dummy(1, 2, b1=6, b2=5)
    assert id(d1) == id(d2)

    d3 = Dummy(1, 2)
    assert id(d3) != id(d1)



def test_cached_object_kwargs_only():
    class Dummy(metaclass=Cached):
        def __init__(self, b1=1, b2=2, b3=3):
            pass

    d1 = Dummy()
    d2 = Dummy(b2=2,b1=1, b3=3)
    d3 = Dummy(b3=3,b1=1, b2=2)
    d4 = Dummy(b2=2,b3=3, b1=1)

    assert id(d1) == id(d2) == id(d3) == id(d4)


def test_cached_object_with_not_hashable_args():
    class Dummy(metaclass=Cached):
        def __init__(self, a1 = [1,2,3]):
            pass


    with pytest.raises(TypeError):
        Dummy()
