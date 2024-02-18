import functions_framework


import time
import os

from google.cloud import videointelligence
 
video_client = videointelligence.VideoIntelligenceServiceClient()
 
LOCATION  = os.environ.get("REGION", "us-central1")
PROJECT_ID= os.environ.get("PROJECT_ID", "")
OUTPUT_BUCKET  = os.environ.get("OUTPUT_BUCKET", "video-working-bucket-2f60")
SPLIT_BY_FEATURES  = os.environ.get("SPLIT_BY_FEATURES", "0")


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

    if contentType == "video/mp4" :


        input_uri =  "gs://" + bucket + "/" + name
        
        file_system = name.split(".")[0].split("/")[-1]
        #directory = name.split("/")[-2]


        
        
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
        

    else:
        print("Unsupported file type: ", contentType)

    print("end.") 

def annotate_video(input_uri, file_system, language_code):
    
    output_uri = f"gs://{OUTPUT_BUCKET}/{language_code}/{file_system} - {time.time()}.json"
        
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

        output_uri = f"gs://{OUTPUT_BUCKET}/{language_code}/{featureId(feature)}/{file_system} - {time.time()}.json"
            
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


    
import json
import pandas as pd
from google.cloud import storage

def read_json_from_gcs(bucket_name, file_name):
    """Reads a JSON file from a Google Cloud Storage bucket.

    Args:
        bucket_name (str): The name of the bucket containing the file.
        file_name (str): The name of the JSON file to read.

    Returns:
        dict: The parsed JSON data, or None if an error occurs.
    """

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)

    try:
        contents = blob.download_as_string()
        data = json.loads(contents)
        df = pd.json_normalize(data)
        data_json = df.to_json( orient="records")
        #data_str = data_json.dumps(orient="records")
        bucket.blob(file_name + "_flattened.json").upload_from_string(data_json, 'text/json')

        return data
    except Exception as e:
        print(f"Error reading JSON file: {e}")
        return None


from datetime import timedelta
from typing import Optional, Sequence, cast

import base64
import vertexai
from vertexai.preview.generative_models import GenerativeModel, Part
import vertexai.preview.generative_models as generative_models

from moviepy.editor import VideoFileClip
from google.cloud import videointelligence_v1 as vi
import vertexai

vertexai.init(project=PROJECT_ID, location=LOCATION)

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



def content_moderation_gemini(video_input : Part):
    model_vision = GenerativeModel("gemini-pro-vision")

    responses = model_vision.generate_content(
    ["""You are an expert in content moderation. 
Explain evidence with the CSA rule and without offensive quote.

You classify text with CSA rules. Answer short JSON results like an API without quote with the following format:""", """{""", """\"csa_rules\": {
    \"violence\": 0,
    \"violence_evidence\":  \"\",

    \"hate_speech\": 0,
    \"hate_evidence\":  \"\",

    \"sexual_content\": 0,
    \"sexual_evidence\":  \"\",

    \"drugs_and_alcohol\": 0,
    \"drugs_and_alcohol_evidence\":  \"\",

    \"profanity\": 0
    \"profanity_evidence\":  \"\",
  }
}

Evaluate CSA rules based on this video part and output them in JSON."""
         , video_input],
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
    
    return "".join(answer)



def get_video_text(results: vi.VideoAnnotationResults, min_frames: int = 15):
    annotations = results.text_annotations

    allText = []

    print(" Detected text ".center(80, "-"))
    for annotation in annotations:
        for text_segment in annotation.segments:
            frames = len(text_segment.frames)
            # if frames < min_frames:
            #     continue
            text = annotation.text
            allText.append(text)
            confidence = text_segment.confidence
            start = text_segment.segment.start_time_offset
            seconds = segment_seconds(text_segment.segment)
            print(text)
            print(f"  {confidence:4.0%} | {start} + {seconds:.1f}s | {frames} fr.")
    return allText

def print_video_text(results: vi.VideoAnnotationResults, min_frames: int = 15):
    annotations = sorted_by_first_segment_end(results.text_annotations)

    print(" Detected text ".center(80, "-"))
    for annotation in annotations:
        for text_segment in annotation.segments:
            frames = len(text_segment.frames)
            if frames < min_frames:
                continue
            text = annotation.text
            confidence = text_segment.confidence
            start = text_segment.segment.start_time_offset
            seconds = segment_seconds(text_segment.segment)
            print(text)
            print(f"  {confidence:4.0%} | {start} + {seconds:.1f}s | {frames} fr.")


def sorted_by_first_segment_end(
    annotations: Sequence[vi.TextAnnotation],
) -> Sequence[vi.TextAnnotation]:
    def first_segment_end(annotation: vi.TextAnnotation) -> int:
        return annotation.segments[0].segment.end_time_offset.total_seconds()

    return sorted(annotations, key=first_segment_end)


def segment_seconds(segment: vi.VideoSegment) -> float:
    t1 = segment.start_time_offset.total_seconds()
    t2 = segment.end_time_offset.total_seconds()
    return t2 - t1

def split_video(input_video, output_video, start : int, end: int):

    clip = VideoFileClip(input_video).subclip(start,end)
    clip.write_videofile(output_video)

def split_video_shots(input_video, results: vi.VideoAnnotationResults):
    shots = results.shot_annotations
    print(f" Video shots: {len(shots)} ".center(40, "-"))
    for i, shot in enumerate(shots):
        t1 = shot.start_time_offset.total_seconds()
        t2 = shot.end_time_offset.total_seconds()
        print(f"{i+1:>3} | {t1:7.3f} | {t2:7.3f}")
        output_video = f"{input_video } - {i} - {t1} - {t2}.mp4"
        
        split_video(input_video=input_video, output_video=output_video, start=t1, end=t2)
        



def print_frames(results: vi.VideoAnnotationResults, likelihood: vi.Likelihood):
    frames = results.explicit_annotation.frames
    frames = [f for f in frames if f.pornography_likelihood == likelihood]

    print(f" {likelihood.name} frames: {len(frames)} ".center(40, "-"))
    for frame in frames:
        print(frame.time_offset)
        
def print_video_shots(results: vi.VideoAnnotationResults):
    shots = results.shot_annotations
    print(f" Video shots: {len(shots)} ".center(40, "-"))
    for i, shot in enumerate(shots):
        t1 = shot.start_time_offset.total_seconds()
        t2 = shot.end_time_offset.total_seconds()
        print(f"{i+1:>3} | {t1:7.3f} | {t2:7.3f}")
        

        
def print_video_labels(results: vi.VideoAnnotationResults):
    labels = sorted_by_first_segment_confidence(results.segment_label_annotations)

    print(f" Video labels: {len(labels)} ".center(80, "-"))
    for label in labels:
        categories = category_entities_to_str(label.category_entities)
        for segment in label.segments:
            confidence = segment.confidence
            t1 = segment.segment.start_time_offset.total_seconds()
            t2 = segment.segment.end_time_offset.total_seconds()
            print(
                f"{confidence:4.0%}",
                f"{t1:7.3f}",
                f"{t2:7.3f}",
                f"{label.entity.description}{categories}",
                sep=" | ",
            )


def sorted_by_first_segment_confidence(
    labels: Sequence[vi.LabelAnnotation],
) -> Sequence[vi.LabelAnnotation]:
    def first_segment_confidence(label: vi.LabelAnnotation) -> float:
        return label.segments[0].confidence

    return sorted(labels, key=first_segment_confidence, reverse=True)


def category_entities_to_str(category_entities: Sequence[vi.Entity]) -> str:
    if not category_entities:
        return ""
    entities = ", ".join([e.description for e in category_entities])
    return f" ({entities})"
    