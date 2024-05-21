
import io
import os
import pathlib
import random
import shutil
import time
from bs4 import BeautifulSoup
import streamlit as st
from vertexai.vision_models import ImageTextModel

from vertexai.preview.generative_models import (
    GenerationConfig,
    GenerativeModel,
    Image,
    Part,
)
import vertexai
from vertexai.preview.generative_models import (
    GenerationConfig,
    GenerativeModel,
    HarmCategory,
    HarmBlockThreshold,
    Part,
)
from vertexai.preview.vision_models import (
    Image, 
    ImageGenerationModel
)

import gcs as gcs
import config as config
import bq as bq
import bq_movie as bq_movie
import utils as utils
    
def start():
    vertexai.init(project=config.PROJECT_ID, location=config.REGION)
    st.set_page_config(page_title="Video content analyser - Google Cloud AI Demos", layout="wide")

    st.title("Video content analyser - Google Cloud AI Demos")

    film_filter = bq_movie.get_movies_list()

    from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, ColumnsAutoSizeMode

    # select the columns you want the users to see
    gb = GridOptionsBuilder.from_dataframe(film_filter[[ "video_blobname"]])
    # configure selection
    gb.configure_selection(selection_mode="single", use_checkbox=True, header_checkbox=True)
    gb.configure_side_bar()
    gridOptions = gb.build()

    data_filter = AgGrid(film_filter,
                gridOptions=gridOptions,
                enable_enterprise_modules=True,
                allow_unsafe_jscode=True,
                update_mode=GridUpdateMode.SELECTION_CHANGED,
                columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS)

    selected_rows = data_filter["selected_rows"]

    if selected_rows is not None:
        if len(selected_rows) != 0:

            filter = selected_rows['video_blobname']
            filter = filter[0]
            #st.markdown(f":orange[{selected_rows['video_blobname']}]")
            #print(80*"*")
            #print(type(filter))
            #print(filter[0])
            #print(80*"*")
            
            

            df_descriptions = bq_movie.get_movie_description(filter)
            #st.dataframe(df_descriptions)
                

            formatter = {
                'index': ('Index', {'width': 2, "pinned": "left"}),
                'description': ('Description', utils.PINLEFT),            
                'start': ('Start', {'width': 10}),
                'stop': ('Stop', {'width': 10}),
                'llm_model': ('Model', {'width': 10}),
            }

            row_number = st.number_input('Number of rows', min_value=0, value=20)
            gb_desc = utils.draw_grid(
                df_descriptions.head(row_number),
                formatter=formatter,
                fit_columns=True,
                selection='single',  # or 'single', or None
                use_checkbox='False',  # or False by default
                max_height=300, 
                wrap_text = True,
                auto_height = True
            )
            # gb_desc = GridOptionsBuilder.from_dataframe(df_descriptions)
            # # configure selection
            # gb_desc.configure_selection(selection_mode="single", 
            #                             use_checkbox=False, 
            #                             header_checkbox=False )
            
            # # # #gb_desc.configure_side_bar()
            # gb_desc.configure_grid_options()
            # gb_desc_gridOptions = gb_desc.build()
            # data_description = AgGrid(df_descriptions,
            #       gridOptions=gb_desc_gridOptions,
            #       enable_enterprise_modules=True,
            #       allow_unsafe_jscode=True,
            #       update_mode=GridUpdateMode.SELECTION_CHANGED,
            #       columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS)
            
            data_desc_selected_rows = gb_desc.selected_rows
            if data_desc_selected_rows is not None    and len(data_desc_selected_rows) != 0:
                uri = data_desc_selected_rows["uri"][0]
                description = data_desc_selected_rows["description"][0]
                index = data_desc_selected_rows["index"][0]

                image_name_prefix = f"generated_image_{index}_"
                
                #st.write(uri)
                uri_video = gcs.generate_download_signed_url(uri)
                st.video(uri_video)

                for i in [0,1,2,3]:
                    if os.path.exists(f'{image_name_prefix}{i}.png') == True:                

                        st.image(f'{image_name_prefix}{i}.png', width=350)
                    else:
                        #st.write(".")
                        with st.spinner("Generating images"):
                            st.write(filter)
                            import imagen as imagen
                            arr_images, arr_image_prompt = imagen.generate(filter,index,description)
                            if len(arr_images) > 0:
                                #st.image(arr_images, width=350, caption=arr_image_prompt)
                                for idx, image in enumerate(arr_images):                        
                                    prompt = arr_image_prompt[idx]
                                    print(prompt)
                                    st.image(image, width=350, caption=f"{prompt}")

                            else:
                                st.write("Cannot generate images.")




def main():          
    start()

start()