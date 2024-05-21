
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



from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode, JsCode
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, ColumnsAutoSizeMode

MAX_TABLE_HEIGHT = 500


def get_numeric_style_with_precision(precision: int) -> dict:
    return {"type": ["numericColumn", "customNumericFormat"], "precision": precision}


PRECISION_ZERO = get_numeric_style_with_precision(0)
PRECISION_ONE = get_numeric_style_with_precision(1)
PRECISION_TWO = get_numeric_style_with_precision(2)
PINLEFT = {"pinned": "left"}


def draw_grid(
        df,
        formatter: dict = None,
        selection="multiple",
        use_checkbox=False,
        fit_columns=False,
        theme="streamlit",
        max_height: int = MAX_TABLE_HEIGHT,
        wrap_text: bool = False,
        auto_height: bool = False,
        grid_options: dict = None,
        key=None,
        css: dict = None
):

    gb = GridOptionsBuilder()
    gb.configure_default_column(
        filterable=True,
        groupable=False,
        editable=False,
        wrapText=wrap_text,
        autoHeight=auto_height
    )

    if grid_options is not None:
        gb.configure_grid_options(**grid_options)

    for latin_name, (cyr_name, style_dict) in formatter.items():
        gb.configure_column(latin_name, header_name=cyr_name, **style_dict)

    gb.configure_selection(selection_mode=selection, use_checkbox=use_checkbox)

    return AgGrid(
        df,
        gridOptions=gb.build(),
        update_mode=GridUpdateMode.SELECTION_CHANGED ,
        allow_unsafe_jscode=True,
        fit_columns_on_grid_load=fit_columns,
        height=min(max_height, (1 + len(df.index)) * 29),
        theme=theme,
        key=key,
        custom_css=css,
        columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS
    )


def highlight(color, condition):
    code = f"""
        function(params) {{
            color = "{color}";
            if ({condition}) {{
                return {{
                    'backgroundColor': color
                }}
            }}
        }};
    """
    return JsCode(code)


def embed_video(uri):
    code = f"""
        function(params) {{
             return {{
                   <video controls width="250">
  <source src="{uri}" type="video/webm" />

  <source src="{uri}" type="video/mp4" />

</video>


                }}
        }};
    """
    return JsCode(code)