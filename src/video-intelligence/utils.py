
import json
import os
import pandas as pd
import datetime

def flatten_json(data):
    
    # # Extract the CSA rules into a separate dictionary
    # csa_rules = data['csa_rules']

    # # Update the original data, removing inner 'csa_rules' and adding individual rules
    # data.update(csa_rules)
    # del data['csa_rules']  

    # Create a DataFrame from the modified data
    df = pd.DataFrame([data])

    return df

def replace_extension(filename,  new_extension):
    """Replaces the extension of a filename with a new extension."""
    base, ext = os.path.splitext(filename)  # Split into base filename and extension    
    return base + new_extension
    

def get_date_time_string(timestamp = None):
    """Returns a string representing the current date and time.

    Args:
        timestamp: A timestamp object.

    Returns:
        A string representing the current date and time.
    """
    if timestamp is None:
        timestamp = datetime.datetime.now()

    return timestamp.strftime("%Y-%m-%d %H:%M:%S")  
