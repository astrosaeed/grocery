import streamlit as st
import re

import sys

from vendors import VENDORS
not_needed= [ 'ewey doy you get cu btst', '650 HARRY L DRIVE', 'johnson city,ny 13790', '607729-7782','@','sc','dp','wt','650 harry l drive']
#VENDORS =['wegmans','walmart']
def convert_to_float_if_decimal(input_str):
    decimal_pattern = r'^(?!\@)\$?\d+\.\d{2}.?[a-zA-Z]?$'
#r'^\d+\.\d{2}[a-zA-Z]?$'   #
    
    if re.match(decimal_pattern, input_str):
        numeric_part = re.search(r'\d+\.\d{2}', input_str).group()
        return float(numeric_part)
    else:
        return input_str

def check_left_to_right(mixed_results):

    for i,entity in enumerate(mixed_results):
        if isinstance(entity,str):
            if 'balance' in entity.lower() or 'total' in entity.lower() :
                if isinstance(mixed_results[i+1],float):
                    return True
                elif isinstance(mixed_results[i-1],float):
                    return False
    sys.exit('Something wrong')



def build_table(mixed_results):

    # Define the modified regex pattern for mm/dd/YY format
    date_pattern = r'\b\d{1,2}[-/]\d{2}[-/]\d{2}\S*'

    left_to_right = check_left_to_right(mixed_results)
    costs=[]
    names = []
    for i,entity in enumerate(mixed_results):
            
        if type(entity) ==float:
            costs.append(entity)
            if not left_to_right:
                names.append(mixed_results[i+1])
            else:
                names.append(mixed_results[i-1])
        #line bellow can potentially be taken care of in the mixed results
        elif isinstance(entity,str) and len(re.findall(date_pattern, entity))>0:
            dates = re.findall(date_pattern, entity)
        
        elif not entity.lower() in not_needed or '@' in entity or 'sc' in entity or 'dp' in entity or 'wt' in entity:
            continue
        
        elif entity.lower() in VENDORS:
            vendor = entity
        else:
            if 'balance' in entity.lower():
                break
    
    assert len(costs) ==len(names)
    try:
        all_dates = [dates[0][:8] for x in names]
    except:
        all_dates = ['N/A' for _ in names]

    try:
        all_vendors = [vendor for _ in names]
    except:
        all_vendors = ['N/A' for _ in names]
    return names, costs, all_dates, all_vendors
