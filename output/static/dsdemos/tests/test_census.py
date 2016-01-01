#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""Pytests for dsdemos/census.py

"""


# Import standard packages.
import collections
import os
import sys
# Import installed packages.
import pytest
# Import local packages.
sys.path.insert(0, os.path.curdir)
import dsdemos.census as census


def test_parse_pumsdatadict13(
    path:str='test_census/test_parse_pumsdatadict13.txt',
    ref_path:str='test_census/test_parse_pumsdatadict13.json') -> None
    r"""Pytest for parse_pumsdatadict13.
    
    """
    # TODO:
    # * select a few choice examples from datadict as the test
    # * read ref_path into ref_ddict
    # * assert ref_ddict == test_ddict
    # Raise FileNotFoundError.
    with pytest.raises(FileNotFoundError):
        census.parse_pumsdatadict13(path='does/not/exist.txt')
    return None
