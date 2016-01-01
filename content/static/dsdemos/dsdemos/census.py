#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""Utilities for working with the United States Census Bureau.[^cb]

Notes:
    * Acronyms:
        ACS: American Community Survey[^acs]
        PUMS: Public Use Microdata Sample[^pums], specific to ACS

References:
    [^cb]: http://www.census.gov/
    [^acs]: https://www.census.gov/programs-surveys/acs/
    [^pums]: https://www.census.gov/programs-surveys/acs/technical-documentation/pums.html

"""


# Import standard packages.
import collections
import os
# Import installed packages.
# Import local packages.
import dsdemos.utils as utils


def parse_pumsdatadict13(path:str) -> collections.OrderedDict:
    r"""Parse the ACS PUMS Data Dictionary for 2013.
    
    Args:
        path (str): Path to downloaded PUMSDataDict13.txt.[^url]
        
    Returns:
        ddict (collections.OrderedDict): Parsed data dictionary with original
            key order preserved.
    
    Raises:
        FileNotFoundError: Raised if `path` does not exist.

    Notes:
        * Values are all strings. No data types are inferred from the
            original file.
    
    References:
        [^url]: http://www2.census.gov/programs-surveys/acs/tech_docs/pums/data_dict/PUMSDataDict13.txt
    
    """
    # Check arguments.
    utils.check_arguments(
        antns=parse_pumsdatadict13.__annotations__,
        lcls=locals())
    if not os.path.exists(path):
        raise FileNotFoundError(
            "Path does not exist:\n{path}".format(path=path))
    # Parse data dictionary.
    # Note:
    # * Data dictionary keys and values are "codes for variables",
    #   using the ACS terminology,
    #   https://www.census.gov/programs-surveys/acs/technical-documentation/pums/documentation.html
    # * The data dictionary is not all encoded in UTF-8. Replace encoding
    #   errors when found.
    ddict = collections.OrderedDict()
    with open(path, encoding='utf-8', errors='replace') as fobj:
        # Data dictionary name is line 1.
        ddict['name'] = fobj.readline().strip()
        # Data dictionary date is line 2.
        ddict['date'] = fobj.readline().strip()    
        # Initialize flags to catch lines.
        catch_var_name = None
        catch_var_desc = None
        catch_var_code = None
        for line in fobj:
            line = line.rstrip()
            # Record type is section header 'HOUSING RECORD' or 'PERSON RECORD'.
            if (line.strip() == 'HOUSING RECORD'
                or line.strip() == 'PERSON RECORD'):
                record_type = line.strip()
                ddict[record_type] = dict()
            # A newline precedes a variable name.
            # A newline follows the last variable code.
            elif line == '':    
                catch_var_name = True
                catch_var_code = False
            # Variable name is 1 line with 0 space indent.
            # Variable name is followed by variable description.
            elif (catch_var_name and not line.startswith(' ')
                and len(line.split()) == 2):
                (var_name, var_len) = line.strip().split()
                ddict[record_type][var_name] = dict()
                ddict[record_type][var_name]['length'] = var_len
                catch_var_name = False
                catch_var_desc = True
            # Variable description is 1 line with 4 space indent.
            # Variable description is followed by variable code(s).
            # Catch explicit instances of inconsistently formatted data.
            elif catch_var_desc:
                is_valid_desc = None
                if line.startswith(' '*4):
                    is_valid_desc = True
                # Example inconsistent format case:
                # ADJHSG     7      
                # Adjustment factor for housing dollar amounts (6 implied decimal places)
                elif 'ADJ' in var_name and 'Adjustment factor' in line:
                    is_valid_desc = True
                else:
                    pass
                if is_valid_desc:
                    var_desc = line.strip()
                    ddict[record_type][var_name]['description'] = var_desc
                    catch_var_desc = False
                    catch_var_code = True
                if is_valid_desc is None:
                    raise AssertionError(
                        "Program error. `is_valid_desc` must be set within if-elif-else.")
            # Variable code(s) is 1+ line with 8+ space indent. Example:
            # NP         2      
            #     Number of person records following this housing record
            #                00 .Vacant unit
            #                01 .One person record (one person in household or  
            #                   .any person in group quarters)
            #            02..20 .Number of person records (number of persons in
            #                   .household)
            # The last variable code is followed by a newline.
            # Catch explicit instances of inconsistently formatted data.
            elif catch_var_code:
                is_valid_code = None
                if line.startswith(' '*8):
                    # Example case: ".any person in group quarters)"
                    if line.strip().startswith('.'):
                        var_code_desc = line.strip().lstrip('.')
                        ddict[record_type][var_name][var_code] += ' '+var_code_desc
                        is_valid_code = False
                    # Example inconsistent format case:
                    # DEAR<tab>   1
                    #     Hearing difficulty
                    #            1. Yes
                    #            2. No
                    elif 'DEAR' in var_name and ('1. Yes' in line or '2. No' in line):
                        (var_code, var_code_desc) = line.strip().split(sep='. ', maxsplit=1)
                        is_valid_code = True
                    # Example inconsistent format case:
                    # MARHYP     4
                    #     Year last married
                    #            bbbb. N/A (age less than 15 years; never married)
                    #            1932 .1932 or earlier (Bottom-coded)
                    #            1933 .1933
                    elif 'MARHYP' in var_name and 'bbbb. N/A' in line:
                        (var_code, var_code_desc) = line.strip().split(sep='. ', maxsplit=1)
                        is_valid_code = True
                    # Example case: "01 .One person record (one person in household or"
                    else:
                        (var_code, var_code_desc) = line.strip().split(sep=' .', maxsplit=1)
                        is_valid_code = True
                # Example inconsistent format case:
                # RWAT       1      
                #     Hot and cold running water
                #            b .N/A (GQ)
                #            1 .Yes
                #            2 .No
                # <tab>   9. Case is from Puerto Rico, RWAT not applicable
                elif 'RWAT' in var_name and '9. Case is from' in line:
                    (var_code, var_code_desc) = line.strip().split(sep='. ', maxsplit=1)
                    is_valid_code = True
                # Example inconsistent format:
                # SMP        5      
                #     Total payment on all second and junior mortgages and home equity loans 
                #     (monthly amount)
                #                   bbbbb .N/A (GQ/vacant/not owned or being bought/
                #                         ./no second or junior mortgages or home equity loans)
                #            00001..99999 .$1 to $99999 (Rounded and top-coded)
                elif 'SMP' in var_name and '(monthly amount)' in line:
                    var_desc = line.strip()
                    ddict[record_type][var_name]['description'] += ' '+var_desc
                    is_valid_code = False
                else:
                    is_valid_code = False
                if is_valid_code:
                    ddict[record_type][var_name][var_code] = var_code_desc
                if is_valid_code is None:
                    raise AssertionError(
                        "Program error. `is_valid_code` must be set within if-elif-else.")
            # Variable note is preceded by newline.
            # Variable note is 1 line.
            # Variable note is followed by newline.
            elif line.startswith('Note:'):
                var_note = line.lstrip('Note:').strip()
                ddict[record_type][var_name]['note'] = var_note
            # Notes for entire data dictionary are at the end.
            else:
                if 'notes' not in ddict:
                    ddict['notes'] = list()
                ddict['notes'].append(line)
    return ddict
