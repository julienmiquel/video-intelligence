
import json
import os
import pandas as pd

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
    