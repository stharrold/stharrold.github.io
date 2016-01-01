#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""Pytests for dsdemos/census.py

"""


# Import standard packages.
import os
import sys
# Import installed packages.
# Import local packages.
sys.path.insert(0, os.path.curdir)
import dsdemos.census as census


# TODO: def test_parse_pumsddict13
# def test_check_arguments() -> None:
#     r"""Pytest for check_arguments.
    
#     """
#     def myfunc(arg0: int, arg1: str) -> float:
#         utils.check_arguments(
#             antns=myfunc.__annotations__,
#             lcls=locals())
#         return 1.0
#     # Nothing should be raised.
#     myfunc(arg0=1, arg1='mystring')
#     # Raise ValueError.
#     with pytest.raises(ValueError):
#         myfunc(arg0=1.0, arg1='mystring')
#     return None
