
from tenacity import retry, stop_after_attempt, wait_random_exponential


import config as config
import json

import vertexai
from vertexai.preview.generative_models import GenerativeModel, Part
import vertexai.preview.generative_models as generative_models

from google.cloud import videointelligence_v1 as vi
import vertexai

vertexai.init(project=config.PROJECT_ID, location=config.REGION)

def content_moderation(text):
    from vertexai.language_models import TextGenerationModel

    parameters = {
        "max_output_tokens": 8192,
        "temperature": 0.1,
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



import base64
import vertexai
from vertexai.preview.generative_models import GenerativeModel, Part
import vertexai.preview.generative_models as generative_models



def content_moderation(text):
    from vertexai.language_models import TextGenerationModel

    parameters = {
        "max_output_tokens": 8192,
        "temperature": 0.1,
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



@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(3))
def content_moderation_gemini(video_input):
    print(f"content_moderation_gemini {video_input}")
    if type(video_input) == str:
        #if video_input.startswith("gs://"):
        video1 = Part.from_uri(uri=video_input, mime_type="video/mp4")
        # else:
        #     video1 = Part(video_input)
    
    elif type(input) == 'Part':
        video1 = video_input
    else:
        print(f"input is not supported: {video_input}")
        return 
    

    model = GenerativeModel("gemini-pro-vision")
    responses = model.generate_content(
    ["""You are an expert in content moderation. 
Explain in detail why you provide the rating with the content moderation rule and without offensive quote.

You classify text with CSA rules. Answer short JSON results like an API without quote with the following format:
{"\"csa_rules\": {
    \"violence\": 0,
    \"violence_evidence\":  \"\",

    \"hate_speech\": 0,
    \"hate_evidence\":  \"\",

    \"sexual_content\": 0,
    \"sexual_evidence\":  \"\",

    \"drugs_and_alcohol\": 0,
    \"drugs_and_alcohol_evidence\":  \"\",

    \"profanity\": 0,
    \"profanity_evidence\":  \"\",
  }
}

Evaluate CSA rules based on this video part and output them in JSON. Return a valide JSON format.

VIDEO:
"""
         , video1, "JSON:"],
        generation_config={
            "max_output_tokens": 2048,
            "temperature": 0.1,
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

