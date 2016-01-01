#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""Pytests for dsdemos/census.py

"""


# Import standard packages.
import collections
import json
import os
import sys
# Import installed packages.
import pytest
# Import local packages.
sys.path.insert(0, os.path.curdir)
import dsdemos.census as census


def test_parse_pumsdatadict2013(
    path:str=os.path.join(
        os.path.curdir,
        'tests/test_census/test_parse_pumsdatadict2013.txt'),
    ref_path:str=os.path.join(
        os.path.curdir,
        'tests/test_census/test_parse_pumsdatadict2013.json')) -> None:
    r"""Pytest for parse_pumsdatadict2013.
    
    Notes:
        * Create 'test_parse_pumsdatadict2013.txt' from the source document.[^url]
        * Create 'test_parse_pumsdatadict2013.json' by
            ```
            with open(path, 'w') as fobj:
                json.dump(test, fobj, indent=4)
            ```
        
    References:
        [^url]: http://www2.census.gov/programs-surveys/acs/tech_docs/pums/data_dict/PUMSDataDict2013.txt
        
    """
    with open(ref_path) as fobj:
        ref_ddict = json.load(fobj)
    test_ddict = census.parse_pumsdatadict2013(path=path)
    assert ref_ddict == test_ddict
    # Raise FileNotFoundError.
    with pytest.raises(FileNotFoundError):
        census.parse_pumsdatadict2013(path='does/not/exist.txt')
    return None


def test_parse_pumsdatadict20092013(
    path:str=os.path.join(
        os.path.curdir,
        'tests/test_census/test_parse_pumsdatadict20092013.txt'),
    ref_path:str=os.path.join(
        os.path.curdir,
        'tests/test_census/test_parse_pumsdatadict20092013.json')) -> None:
    r"""Pytest for parse_pumsdatadict20092013.
    
    Notes:
        * Create 'test_parse_pumsdatadict20092013.txt' from the source document.[^url]
        * Create 'test_parse_pumsdatadict20092013.json' by
            ```
            with open(path, 'w') as fobj:
                json.dump(test, fobj, indent=4)
            ```
        
    References:
        [^url]: http://www2.census.gov/programs-surveys/acs/tech_docs/pums/data_dict/PUMSDataDict2013.txt
        
    """
    with open(ref_path) as fobj:
        ref_ddict = json.load(fobj)
    test_ddict = census.parse_pumsdatadict20092013(path=path)
    assert ref_ddict == test_ddict
    # Raise FileNotFoundError.
    with pytest.raises(FileNotFoundError):
        census.parse_pumsdatadict20092013(path='does/not/exist.txt')
    return None
