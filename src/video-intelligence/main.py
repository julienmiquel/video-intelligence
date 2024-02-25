import io
import json
import functions_framework


import time
import os

from google.cloud import videointelligence
import gcs as gcs 
import videoedit as videoedit
import pandas as pd

video_client = videointelligence.VideoIntelligenceServiceClient()
 
REGION  = os.environ.get("REGION", "us-central1")
PROJECT_ID= os.environ.get("PROJECT_ID", "")
OUTPUT_BUCKET  = os.environ.get("OUTPUT_BUCKET", "video-working-bucket-2f60")
SPLIT_BY_FEATURES  = os.environ.get("SPLIT_BY_FEATURES", "1")

INPUT_BUCKET  = os.environ.get("INPUT_BUCKET", "")
WORKING_BUCKET  = os.environ.get("WORKING_BUCKET", "")
TAG_TO_ANALYZE = "CSA"

features = [
    videointelligence.Feature.OBJECT_TRACKING,
    videointelligence.Feature.LABEL_DETECTION,
    videointelligence.Feature.SHOT_CHANGE_DETECTION,
#    videointelligence.Feature.SPEECH_TRANSCRIPTION,
    videointelligence.Feature.LOGO_RECOGNITION,
    videointelligence.Feature.EXPLICIT_CONTENT_DETECTION,
    videointelligence.Feature.TEXT_DETECTION,
    videointelligence.Feature.FACE_DETECTION,
    videointelligence.Feature.PERSON_DETECTION,
]
 

def featureId(feature):
    if feature == videointelligence.Feature.OBJECT_TRACKING:
        return "OBJECT_TRACKING"
    if feature == videointelligence.Feature.LABEL_DETECTION:
        return "LABEL_DETECTION"
    if feature == videointelligence.Feature.SHOT_CHANGE_DETECTION:
        return "SHOT_CHANGE_DETECTION"
    if feature == videointelligence.Feature.SPEECH_TRANSCRIPTION:
        return "SPEECH_TRANSCRIPTION"
    if feature == videointelligence.Feature.LOGO_RECOGNITION:
        return "LOGO_RECOGNITION"
    if feature == videointelligence.Feature.EXPLICIT_CONTENT_DETECTION:
        return "EXPLICIT_CONTENT_DETECTION"
    if feature == videointelligence.Feature.TEXT_DETECTION:
        return "TEXT_DETECTION"
    if feature == videointelligence.Feature.FACE_DETECTION:
        return "FACE_DETECTION"
    if feature == videointelligence.Feature.PERSON_DETECTION:
        return "PERSON_DETECTION"
    
    return "UNKNOWN"


def main(cloud_event):
    process_event(cloud_event)
    

# Triggered by a change in a storage bucket
@functions_framework.cloud_event
def classify_video_with_gemini_event(cloud_event):
    data = cloud_event.data

    event_id = cloud_event["id"]
    event_type = cloud_event["type"]

    bucket = data["bucket"]    
    name = data["name"]
    metageneration = data["metageneration"]
    timeCreated = data["timeCreated"]
    updated = data["updated"]
    contentType = data["contentType"]


    print(f"Event ID: {event_id}")
    print(f"Event type: {event_type}")
    print(f"Bucket: {bucket}")
    print(f"File: {name}")
    print(f"Metageneration: {metageneration}")
    print(f"Created: {timeCreated}")
    print(f"Updated: {updated}")

    if contentType == "video/mp4" :
        print(f"Processing video file with gemini: {name}")

        uri = "gs://" + bucket + "/" + name
        moderate_video(uri, name)

import json
import os
import pandas as pd

def flatten_json(data):
    
    # Extract the CSA rules into a separate dictionary
    csa_rules = data['csa_rules']

    # Update the original data, removing inner 'csa_rules' and adding individual rules
    data.update(csa_rules)
    del data['csa_rules']  

    # Create a DataFrame from the modified data
    df = pd.DataFrame([data])

    return df

def moderate_video(uri, name):
    try:
        res = content_moderation_gemini(uri)
        print(f"moderation content done on chunck uri {uri} with res = {res}")
        print(res)
        print("save json result in output bucket")
        json_file_path = gcs.write_text_to_gcs(OUTPUT_BUCKET, name.replace(".mp4", ".json"), res, "text/json")
        print(f"json_file_path = {json_file_path}")

        dict= json.loads(res)
        df2 = flatten_json(dict)

        print("read tags from source uri")
        bucketname, video_blobname = gcs.split_gcs_uri(uri)

        tags = gcs.read_tags_from_gcs(bucketname, video_blobname)
        print(f"uri= {uri} - tags = {tags}")
        
        df1 = flatten_json(dict)
        df3 = pd.concat([df1, df2], axis=0)
        
        import bq as bq
        table_id = "media.results"

        bq.save_bq(df3,table_id, project_id=PROJECT_ID )
    except Exception as e:
        print(f"ERROR in content_moderation(uri) = {uri}")
        print(e)



# Triggered by a change in a storage bucket
@functions_framework.cloud_event
def process_event(cloud_event):
    data = cloud_event.data

    event_id = cloud_event["id"]
    event_type = cloud_event["type"]

    bucket = data["bucket"]    
    name = data["name"]
    metageneration = data["metageneration"]
    timeCreated = data["timeCreated"]
    updated = data["updated"]
    contentType = data["contentType"]


    print(f"Event ID: {event_id}")
    print(f"Event type: {event_type}")
    print(f"Bucket: {bucket}")
    print(f"File: {name}")
    print(f"Metageneration: {metageneration}")
    print(f"Created: {timeCreated}")
    print(f"Updated: {updated}")

    if contentType == "video/mp4" and TAG_TO_ANALYZE in name:
        print(f"Processing video file with gemini: {name}")

        uri = "gs://" + bucket + "/" + name

        try:
            print("read tags from source uri")
            bucketname, video_blobname = gcs.split_gcs_uri(uri)
            tags = gcs.read_tags_from_gcs(bucketname, video_blobname)            
            print(f"uri= {uri} - tags = {tags}")
        
            res = content_moderation_gemini(uri)
            print(f"moderation content done on chunck uri {uri} with res = {res}")
            print(res)
            json_data = json.loads(res)
            json_data["uri"] = video_input
            json_data["tags"] =tags
            
            res = json.dumps(json_data, indent=4)
            print(res)

            

            print("save json result in output bucket")
            json_file_path = gcs.write_text_to_gcs(OUTPUT_BUCKET, name.replace(".mp4", ".json"), res, "text/json")
            print(f"json_file_path = {json_file_path}")

        except Exception as e:
            print(f"ERROR in content_moderation(uri) = {uri}")
            print(e)

    elif contentType == "video/mp4" and ".mp4" in name:


        input_uri =  "gs://" + bucket + "/" + name
        
        file_system = name.split(".")[0].split("/")[-1]
        
        language_code="en-US"
        #if the input_uri contain "en-US" set the language_code variable to "en-US"
        if "en-US" in input_uri:
            language_code="en-US"
            
        if "fr-FR" in input_uri:        
            language_code="fr-FR"
            
        if "es-ES" in input_uri:        
            language_code="es-ES"   
            
        if "de-DE" in input_uri:        
            language_code="de-DE"

        if "it-IT" in input_uri:        
            language_code="it-IT"

        if "pt-PT" in input_uri:        
            language_code="pt-PT"

        if "pt-BR" in input_uri:        
            language_code="pt-BR"

        if "zh-CN" in input_uri:        
            language_code="zh-CN"

        if "ja-JP" in input_uri:        
            language_code="ja-JP"

        if "ko-KR" in input_uri:        
            language_code="ko-KR"

        if "ar-XA" in input_uri:        
            language_code="ar-XA"

        if "ru-RU" in input_uri:        
            language_code="ru-RU"

        if "hi-IN" in input_uri:        
            language_code="hi-IN"

        if SPLIT_BY_FEATURES == "1" :
            annotate_video_split_by_features(input_uri, file_system, language_code)
        else:
            annotate_video(input_uri, file_system, language_code)
        

    elif contentType == "application/octet-stream" or contentType == "text/json"  or contentType == "application/json":
        print("Processing json file: ", name)
        data = gcs.read_json_from_gcs(bucket, name)

        from google.cloud import videointelligence_v1 as vi
        annotation = vi.AnnotateVideoResponse(data)
        
        content_moderation_text_based = None
        texts = None
        index = 0
        for annotation_result in annotation.annotation_results:
            # ex: input_bucket     "input_uri": "/video-input-bucket-2f60/fr-FR/cdanslair.mp4",

            print(f"Finished processing input: {annotation_result.input_uri}" ) 
            uri  = "gs:/"+annotation_result.input_uri
            
            print(f"full uri = {uri}")
            # gs://video-input-bucket-2f60/fr-FR/cdanslair.mp4

            bucketname, video_blobname = gcs.split_gcs_uri(uri)
            print(f"bucketname = {bucketname} - blobname = {video_blobname}")
            # video-input-bucket-2f60  /fr-FR/cdanslair.mp4
            localfile = video_blobname.replace("/", "_") # -{index}
            print(f"localfile = {localfile}")
            # fr-FR_cdanslair.mp4

            video_input = gcs.store_temp_video_from_gcs(bucketname, video_blobname, localfile= localfile)
            
            print(f"video_input = {video_input}")

            for input_part, t1,t2 in videoedit.split_video_shots(video_input,annotation_result ):
                print(f"split_video_shots input_part = {input_part}")
                index = index + 1
                # remove file extention
                #video_blobname = os.path.splitext(video_blobname)[0]

                gcs_file_name = f"{TAG_TO_ANALYZE}/{video_blobname}/chunks - {index} - {t1} - {t2}.mp4"
                print(f"write in output bucket chunck file gcs_file_name = {gcs_file_name}")
                tags = {
                    "video_source": uri,                    
                    "video_blobname": video_blobname,
                    "index": index,
                    "time_start": t1,
                    "time_stop": t2                    
                }

                # write in output bucket chunck file                
                blob = gcs.write_file_to_gcs(OUTPUT_BUCKET, 
                                             gcs_file_name=gcs_file_name, 
                                             local_file_path=input_part, 
                                             tags=tags)
                
                chunck_uri=  f"gs://{OUTPUT_BUCKET}/{blob.name}"

                print(80*"*" + f" CHUNK URI {chunck_uri}" + 80*"*")
                print(f"VIDEO chunck uri = {chunck_uri}")

                # try:
                #     res = content_moderation_gemini(chunck_uri)
                #     print(f"moderation content done on chunck uri {chunck_uri} with res = {res}")
                #     print(res)
                #     print("save json result in output bucket")
                #     json_file_path = gcs.write_text_to_gcs(OUTPUT_BUCKET, gcs_file_name.replace(".mp4", ".json"), res, "text/json")
                #     print(f"json_file_path = {json_file_path}")

                # except Exception as e:
                #     print(f"ERROR in content_moderation(uri) = {uri}")
                #     print(e)

                # with io.open(input_part.replace(".mp4", ".json"), 'w') as f:
                #     f.write(res)
            
        #texts = videoedit.get_video_text(annotation_result)

        # unique_array = list(set(texts))
        # text = ', '.join(unique_array)
        # print(text)
        #content_moderation_text_based = content_moderation(text)

    else :
        print("Unsupported file type: ", contentType)

    print("end.") 

def annotate_video(input_uri, file_system, language_code):
    
    output_uri = f"gs://{WORKING_BUCKET}/{language_code}/{file_system} - {time.time()}.json"
        
    print(f"input_uri = {input_uri} - output_uri = {output_uri} file_sytem = {file_system}")

    person_config = videointelligence.PersonDetectionConfig(
            include_bounding_boxes=True,
            include_attributes=True,
            include_pose_landmarks=True,
        )
        
    face_config = videointelligence.FaceDetectionConfig(
            include_bounding_boxes=True,
            include_attributes=True,
        )
    speech_config = videointelligence.SpeechTranscriptionConfig(
            language_code=language_code,
            enable_automatic_punctuation=True,
            enable_speaker_diarization=True,
            #diarization_speaker_count=2,
        )

    video_context = videointelligence.VideoContext(
            speech_transcription_config=speech_config,
            person_detection_config=person_config,
            face_detection_config=face_config,
        )    
    print("Processing video ", input_uri)




    operation = video_client.annotate_video(
            request={
                "features": features,
                "input_uri": input_uri,
                "output_uri": output_uri,
                "video_context": video_context,
            }
        )   

    print("Processing video.", operation)

    while not operation.done():
        print("Waiting for operation to complete...", operation)
        print(operation.metadata)
        time.sleep(30)
    
    print("finished processing.")       


def annotate_video_split_by_features(input_uri, file_system, language_code):
    operations = []
    for feature in features:
        print(featureId(feature))

        output_uri = f"gs://{WORKING_BUCKET}/{language_code}/{featureId(feature)}/{file_system} - {time.time()}.json"
            
        print(f"input_uri = {input_uri} - output_uri = {output_uri} file_sytem = {file_system}")

        person_config = videointelligence.PersonDetectionConfig(
                include_bounding_boxes=True,
                include_attributes=True,
                include_pose_landmarks=True,
            )
            
        face_config = videointelligence.FaceDetectionConfig(
                include_bounding_boxes=True,
                include_attributes=True,
            )
        speech_config = videointelligence.SpeechTranscriptionConfig(
                language_code=language_code,
                enable_automatic_punctuation=True,
                enable_speaker_diarization=True,
                #diarization_speaker_count=2,
            )

        video_context = videointelligence.VideoContext(
#                speech_transcription_config=speech_config,
                person_detection_config=person_config,
                face_detection_config=face_config,
            )    
        print("Processing video ", input_uri)

        operation = video_client.annotate_video(
                request={
                    "features": [feature],
                    "input_uri": input_uri,
                    "output_uri": output_uri,
                    "video_context": video_context,
                }
            )   

        print("Processing video.", operation)
        operations.append(operation)

    print("Waiting for the operations to complete...")    
    for operation in operations:
        while not operation.done():
            print("Waiting for operation to complete...", operation)
            print(operation.metadata)
            time.sleep(30)
    
    print("finished processing.")       








import vertexai
from vertexai.preview.generative_models import GenerativeModel, Part
import vertexai.preview.generative_models as generative_models

from google.cloud import videointelligence_v1 as vi
import vertexai

vertexai.init(project=PROJECT_ID, location=REGION)

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
    
    str_json = response.replace("json", "").replace("```", "")
    print(str_json)
    json_data = json.loads(str_json)
    return json_data



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

You classify text with CSA rules. Answer short JSON results like an API without quote with the following format:""", 
"""{""", 
"""\"csa_rules\": {
    \"description\": \"description of action in the video\",

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

Evaluate CSA rules based on this video part and output them in JSON."""
         , video1],
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
        print(text, end="")    
        answer.append(text)
    
    str_json = "".join(answer)
    str_json = str_json.replace("json", "").replace("```", "")
    print(str_json)
    
    return str_json

