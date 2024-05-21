import os

import gcs as gcs
import config as config


def llm(prompt):
    import config as config
    import base64
    #import bigframes.dataframe

    import vertexai
    from vertexai.generative_models import GenerativeModel, Part
    import vertexai.generative_models as generative_models


    location = config.REGION_BACKUP_3
    #print(f"vertexai init project={config.PROJECT_ID}, location={location}")

    vertexai.init(project=config.PROJECT_ID, location=location)
    #model = GenerativeModel(config.MODEL_TEXT )
    model = GenerativeModel("gemini-1.5-pro-preview-0409")

    responses = model.generate_content(
        [prompt],
        generation_config={
            "max_output_tokens": 2048,
            "temperature": 0.3,
            "top_p": 1,
            "top_k": 40
        },
        safety_settings={
            generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_NONE,
            generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_NONE,
            generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_NONE,
            generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_NONE,
        },
        stream=False,
    )


    return responses.text


llm('what is gemini llm ?')


image_model_name = "imagegeneration@006"
negativePrompt = """
<Image_Quality>
    low quality
    blurry
    jpeg artifacts
    out of focus
    cropped
</Image_Quality>

<Anatomy_and_Composition>
    bad anatomy
    bad proportions
    deformed
    disfigured
    extra limbs
    missing limbs
    floating limbs
    disconnected limbs
    unrealistic
</Anatomy_and_Composition>

<Other>
    text
    watermark
    signature
    cartoon
    out of frame
    nonsense

    pen_spark

    nsfw
    NSFW (not safe for work)
</Other>
"""
sampleCount = 4
sampleImageSize = 192



from PIL import Image as PIL_Image
from io import BytesIO
import base64
from IPython import display

from matplotlib import pyplot as plt
import math

import requests
import json

sampleImageSize = '1024' #@param {type:"string"}
sampleCount = 2 #@param {type:"integer"}

def get_access_token():
    #return """ya29.a0AXooCgsNpxzNguxJgibzvp675i1vOf9fJAw3QYOmPaxp4JBnp43YaZI4oKIotcc-8j6XRdmCwmXrZ8JpV0cdyigCoOcQSelDE0FdNGEDNlebCHZetrYHNb9NQ9cWzPI-prARDDSCGtHQxe4AnwoAVUfkc7kSg5W0OwSjfohMkCG9EOTDJbzCaCgYKAesSARASFQHGX2Mi2KrO-581DMpR7Mbgo1oYXQ0187"""
    import google.auth
    import google.auth.transport.requests

    # Getting the auth token via SDK
    creds, project = google.auth.default()

    auth_req = google.auth.transport.requests.Request()
    creds.refresh(auth_req)
    ACCESS_TOKEN = creds.token
    return ACCESS_TOKEN

ACCESS_TOKEN = get_access_token()

#@title Helper Functions
# https://cloud.google.com/vertex-ai/docs/generative-ai/model-reference/image-generation
def imagen_generate(
    model_name: str,
    prompt: str,    
    sampleImageSize: str,    
    sampleCount: int,
    negativePrompt: str = None,
    seed = None,
    disablePersonFace = False,
    sampleImageStyle = None,
    PROJECT_ID = config.PROJECT_ID,
    REGION = config.REGION
    ):
  
  ACCESS_TOKEN = get_access_token()
  headers = {
      'Authorization': f'Bearer {ACCESS_TOKEN}',
      'Content-Type': 'application/json; charset=UTF-8'
  }
  # Advanced option, try different the seed numbers
  # any random integer number range: (0, 2147483647)
  data = {"instances": [{"prompt": prompt}], "parameters": {"sampleImageSize": sampleImageSize, "sampleCount": sampleCount, "disablePersonFace": disablePersonFace}}

  # Use & provide a seed, if possible, so that we can reproduce the results when needed.
  if seed:
    data["parameters"]["seed"] = seed
  if negativePrompt:
    data["parameters"]["negativePrompt"] = negativePrompt
  if sampleImageStyle and (sampleImageStyle != "none"):
    data["parameters"]["sampleImageStyle"] = sampleImageStyle

  # print(data)
  endpoint_url = f'projects/{PROJECT_ID}/locations/{REGION}/publishers/google/models/{model_name}'
  print(endpoint_url)
  response = requests.post(f'https://{REGION}-aiplatform.googleapis.com/v1/{endpoint_url}:predict', data=json.dumps(data), headers=headers)
  json_response = json.loads(response.text)

  images = []
  if 'predictions' in json_response.keys():
    predictions = json_response['predictions']
    for index, key in enumerate(predictions):
      im_bytes = base64.b64decode(predictions[index]['bytesBase64Encoded'])
      img = PIL_Image.open(BytesIO(im_bytes))
      images.append(img)
  else:
    print("An error occured calling the API.")
    print("1. Check if response was not blocked based on policy violation, check if the UI behaves the same way...")
    print("2. Try a different prompt to see if that was the problem.\n")
    print(response.text)
    #raise Exception(response.text)
    print(80*"*")
    print(prompt)
    print(80*"*")
    
    return images, None

  return images, response

# Images should be an array of images in PIL image format
def display_images(pil_images, sampleImageSize, ):
  scale = 0.25
  width = int(float(sampleImageSize)*scale)
  height = int(float(sampleImageSize)*scale)
  for index, result in enumerate(pil_images):
    width, height = pil_images[index].size
    print(index)
    display.display(pil_images[index].resize((int(pil_images[index].size[0]*scale),int(pil_images[index].size[1]*scale)), 0) )
    print()

# Images should be an array of images in PIL image format
def display_images_grid(pil_images, columns = 3):
  # create figure
  fig = plt.figure(figsize=(12, 12))

  # Get number of images
  pics = len(list(enumerate(pil_images)))

  # setting values to rows and column variables
  # rows = 2
  rows = math.ceil(pics / columns)

  for index, result in enumerate(pil_images):
    img = pil_images[index]

    # Adds a subplot at the x position
    fig.add_subplot(rows, columns, index + 1)

    # showing image
    plt.imshow(img)
    plt.axis('off')
    plt.title(str(index))





#sampleImageSize = 768
sampleImageSize = 1536
sampleCount = 4

def generate_df(df, filter):
    arr_images = []
    arr_image_prompt = []


    for index, row in df.iterrows():

        # if index ==0:
        #     print(f"skip index = {index}")
        #     continue

        print(f"Processing index = {index}")
        description = row['description']
        to_add_arr_images,to_add_arr_image_prompt = generate(filter, index, row, description)
        
        #TODO: Check this
        arr_images.append(to_add_arr_images)
        arr_image_prompt.append(to_add_arr_image_prompt)
            
    return     arr_images,   arr_image_prompt

def generate(filter, index, description):
    arr_images = []
    arr_image_prompt = []

    sampleImageSize = 1536
    sampleCount = 4

    file_name = "demo"

    prompt = f'''
<description>
{description}
</description>
<Guideslines>
    The prompt follow generation guides lines.
    The prompt does not contains any sensitive words that violate Google's Responsible AI practices.
</<Guideslines>
<task>
    Generate an advanced prompt to generate image.
    The prompt is based on the description of an action.
    The prompt use advanced technic to describe in detail the image.
</task>
        '''
        
        #arr_image_prompt.append(image_prompt)
    image_name_prefix = f"generated_image_{index}_"

    if os.path.exists(f'{image_name_prefix}0.png') == False:
        image_prompt = llm(prompt)
        seed = 0
        retry = True
        if True:
        #while(retry):
            images, images_generate_response = imagen_generate(image_model_name,
                                                                    prompt=image_prompt,
                                                                    #negativePrompt=negativePrompt,
                                                                    sampleCount = sampleCount,
                                                                    sampleImageSize=sampleImageSize,
                                                                    #seed=seed,
                                                                    PROJECT_ID=config.PROJECT_ID
                                                                    )
            print(index)
            # if images == None or len(images) == 0  or seed > 5:
            #     retry = True
            #     seed = None
            #     sampleImageSize = 192
            #     sampleCount = 4
            #     gcs.write_text_to_gcs(config.OUTPUT_BUCKET, f"{filter}/images/{file_name}_bad_prompt.txt", image_prompt)
            # else:
            if True:
                retry = False
                for image in images:
                    arr_images.append(image)
                    arr_image_prompt.append(image_prompt)

                display_images_grid(images)
                    #image_names = []
                gcs.write_text_to_gcs(config.OUTPUT_BUCKET, f"{filter}/images/{file_name}_prompt.txt", image_prompt)
                for image_index, image in enumerate(images):
                        #image_names.append(f'{image_name_prefix}{image_index}.png')
                    file_name = f'{image_name_prefix}{image_index}.png'
                    image.save(file_name)
                    blob =gcs.write_file_to_gcs(config.OUTPUT_BUCKET, f"{filter}/images/{file_name}", file_name)
                    print(blob.path)


    return arr_images, arr_image_prompt