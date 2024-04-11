from time import sleep
from grpc import StatusCode
import config as config
import json

import vertexai
from vertexai.generative_models import GenerativeModel, Part
import vertexai.generative_models as generative_models

from tenacity import retry, stop_after_attempt, wait_random_exponential


# Initialize Vertex AI SDK
vertexai.init(project=config.PROJECT_ID, location=config.REGION)


def content_moderation(text):
    from vertexai.language_models import TextGenerationModel

    parameters = {
        "max_output_tokens": 8192,
        "temperature": 0.0,
        "top_p": 1,
        "top_k": 40
    }
    model = TextGenerationModel.from_pretrained("text-bison-32k")
    response = model.predict(
        f"""You are an expert in content moderation. 
You classify text with CSA rules. Answer short JSON results.
TEXT:
{text}

JSON:
    """,
        **parameters
    )
    print(f"Response from Model: {response.text}")
    
    str_json = CleanJsonOutput(response.text)
    print(str_json)
    json_data = json.loads(str_json)
    return json_data


import base64
import vertexai
from vertexai.generative_models import GenerativeModel, Part
import vertexai.generative_models as generative_models

@retry(wait=wait_random_exponential(min=10, max=60), stop=stop_after_attempt(100))
def content_moderation_gemini(video_input, prompt = None):
    print(f"content_moderation_gemini {video_input}")
    if type(video_input) == str:
        video_input = Part.from_uri(uri=video_input, mime_type="video/mp4")
        print("Create videoPArt")
        print(video_input)

    elif type(input) == 'Part':
        video_input = video_input
    else:
        print(f"input is not supported: {video_input}")
        return 
    
    if prompt == None:
#         prompt =    """Classification task. Choose between PEGI rating from (3, 7, 12, 16, 18). Based on the following content rate the intensity of the scene from: 
# PEGI 3 The content of video with a PEGI 3 rating is considered suitable for all age groups. The video should not contain any sounds or pictures that are likely to frighten young children. A very mild form of violence (in a comical context or a childlike setting) is acceptable. No bad language should be heard. 

# PEGI 7 video content with scenes or sounds that can possibly frightening to younger children should fall in this category. Very mild forms of violence (implied, non-detailed, or non-realistic violence) are acceptable for a video with a PEGI 7 rating 

# PEGI 12 Video that show violence of a slightly more graphic nature towards fantasy characters or nonrealistic violence towards human-like characters would fall in this age category. Sexual innuendo or sexual posturing can be present, while any bad language in this category must be mild. Gambling as it is normally carried out in real life in casinos or gambling halls can also be present.

# PEGI 16 This rating is applied once the depiction of violence (or sexual activity) reaches a stage that looks the same as would be expected in real life. The use of bad language in video with a PEGI 16 rating can be more extreme, while video of chance, and the use of tobacco, alcohol or illegal drugs can also be present. 

# PEGI 18 is rating for adult content.

# VIDEO : 
# """

        prompt = """Based on the following content rate the intensity of the scene from: 

** PEGI 3 ** 
The content of video with a PEGI 3 rating is considered suitable for all age groups. 
The video should not contain any sounds or pictures that are likely to frighten young children. 
A very mild form of violence (in a comical context or a childlike setting) is acceptable. No bad language should be heard. 

** PEGI 7 ** 
video content with scenes or sounds that can possibly frightening to younger children should fall in this category. 
Very mild forms of violence (implied, non-detailed, or non-realistic violence) are acceptable for a video with a PEGI 7 rating 

** PEGI 12 ** 
Video that show violence of a slightly more graphic nature towards fantasy characters or nonrealistic violence towards human-like characters would fall in this age category. 
Sexual innuendo or sexual posturing can be present, while any bad language in this category must be mild. 
Gambling as it is normally carried out in real life in casinos or gambling halls can also be present.

** PEGI 16 ** 
This rating is applied once the depiction of violence (or sexual activity) reaches a stage that looks the same as would be expected in real life. 
The use of bad language in video with a PEGI 16 rating can be more extreme, while video of chance, and the use of tobacco, alcohol or illegal drugs can also be present. 

** PEGI 18 ** 
Rating for sexual explicit content, gore intense."""


        prompt = "Describe for video description"

    isRetryAble = True
    errorMessage = ""
    stream=False
    while( isRetryAble):
        for location in config.REGIONS:
            try:
                print(f"vertexai init project={config.PROJECT_ID}, location={location}") 
            
                vertexai.init(project=config.PROJECT_ID, location=location)
                model = GenerativeModel(config.MODEL_MULTIMODAL)
                responses = model.generate_content(
                    [prompt, video_input],
                    generation_config={
                        "max_output_tokens": 2048,
                        "temperature": 0,
                        "top_p": 1,
                        "top_k": 40
                    },
                    safety_settings={
                        generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_NONE,
                        generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_NONE,
                        generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_NONE,
                        generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_NONE,
                    },
                    stream=stream,
                )
            
                if stream:
                    answer = []
                    for response in responses:
                        text = response.text
                        print(text, end="")    
                        answer.append(text)

                    str_json = "".join(answer)
                else:
                    str_json = responses.text

                print(str_json)
                str_json = CleanJsonOutput(str_json)
                if str_json == "ERROR":
                    isRetryAble = True
                    sleep(30)
                else:
                    return str_json

            except Exception as e:
                errorMessage = f"{e}"                
                print(f"ERROR in content_moderation_gemini(data) = {video_input} - location = {location} - ERROR: {errorMessage}")
                
                if ("RESOURCE_EXHAUSTED" in f"{e}") or ("Quota exceeded" in f"{e}"):
                    isRetryAble = True
                    sleep(30)
                else:
                    isRetryAble = False
                    

    print(f"File have not been processed {video_input} retry will be needed !!!!! {errorMessage}")
    return f"ERROR: {errorMessage}"

@retry(wait=wait_random_exponential(min=10, max=60), stop=stop_after_attempt(100))
def content_moderation_gemini_old(video_input):
    print(f"content_moderation_gemini {video_input}")
    if type(video_input) == str:
        video1 = Part.from_uri(uri=video_input, mime_type="video/mp4")
    
    elif type(input) == 'Part':
        video1 = video_input
    else:
        print(f"input is not supported: {video_input}")
        return 
    
    vertexai.init(project=config.PROJECT_ID, location=config.REGION)

    model = GenerativeModel("gemini-1.0-pro-vision-001")

    prompt = """You are an expert in violence content moderation.
Explain why you provide the rating with the content moderation rule and without offensive quote.

You classify text with CSA rules. Answer short JSON results like an API without quote with the following format:
{\"\\\"csa_rules\\\": {
    \\\"violence\\\": \"0\",
    \\\"violence_evidence\\\":  \\\"\\\"
}

Evaluate CSA rules based on this video part and output them in JSON. Return a valide JSON format."""

    responses = model.generate_content(
        [prompt, video1, "JSON"],
        generation_config={
            "max_output_tokens": 2048,
            "temperature": 0,
            "top_p": 1,
            "top_k": 40
        },
        safety_settings={
            generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_NONE,
            generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_NONE,
            generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_NONE,
            generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_NONE,
        },
        stream=True,
    )

    answer = []
    for response in responses:
        text = response.text
        #print(text, end="")    
        answer.append(text)
    
    str_json = "".join(answer)
    str_json = CleanJsonOutput(str_json)
    #print(str_json)
    
    return str_json

def CleanJsonOutput(str_json):
    str_json = str_json.replace("json", "").replace("JSON", "").replace("```", "")
    str_json = str_json.replace("\'", "\"")

    return str_json

