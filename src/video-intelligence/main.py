import io
import json
import functions_framework

import json
import os

import time
import pandas as pd
import numpy as np

import video_intelligence as gvi
import gcs as gcs 
import videoedit as videoedit
import config as config
import gemini as gemini
import utils as utils
import bq as bq
import stt as stt
import embedding as embedding

def main(cloud_event):
    dump_event(cloud_event)
    

# Triggered by a change in a storage bucket
@functions_framework.cloud_event
def process_event_classify_video(cloud_event):
    bucket, name, contentType = dump_event(cloud_event)

    if contentType == "video/mp4" :
        print(f"Processing video file with gemini: {name}")

        uri = "gs://" + bucket + "/" + name
        tags = moderate_video(uri)
        
        #TODO: call embedding
        # https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/multimodal-embeddings#aiplatform_sdk_text_image_embedding-python_vertex_ai_sdk
        if tags:
            context = tags['description']
            embeddings = embedding.get_image_video_text_embeddings(config.PROJECT_ID,config.REGION,uri, context)

            df = pd.DataFrame(embeddings)

            df['embeddings'] = df['embeddings'].apply(np.array)  # Assuming embeddings are lists/tuples of numbers

            bq.save_embeddings_df_bq(df,config.BQ_TABLE_EMBEDDINGS)
            
        #export_audio(uri)

    print("End - process_event_classify_video")

    if contentType == "audio/mp3" :
        languageCode = getLanguageCode(uri)
        stt.convert(uri, languageCode)


def export_audio(uri):
    bucketname, video_blobname = gcs.split_gcs_uri(uri)
    localfile = video_blobname.replace("/", "_") # -{index}
    print(f"localfile = {localfile}")
    video_input = gcs.store_temp_video_from_gcs(bucketname, video_blobname, localfile= localfile)
    mp3_file = videoedit.export_audio(video_input)
    
    gcs_file_name = video_blobname[0:-1] + "3" # mp3
    tags = {
        "video_source": uri,                    
        "video_blobname": video_blobname        
    }

    blob = gcs.write_file_to_gcs(config.OUTPUT_BUCKET, 
                                gcs_file_name=gcs_file_name, 
                                local_file_path=mp3_file, 
                                tags=tags)

    chunck_uri=  f"gs://{config.OUTPUT_BUCKET}/{blob.name}"

    print(80*"*" + f" MP3 AUDIO URI {chunck_uri}" + 80*"*")    

def moderate_video(uri):
    res = gemini.content_moderation_gemini(uri)
    print(f"moderation content done on chunck uri {uri} with res = {res}")
    # print(80*"*")
    # print(res)
    # print(80*"*")

    print("save json result in output bucket")
    bucketname, name = gcs.split_gcs_uri(uri)
    json_file_path = gcs.write_text_to_gcs(config.OUTPUT_BUCKET, utils.replace_extension(name, ".json"), res, "text/json")
    print(f"json_file_path = {json_file_path}")

    # dict= json.loads(res)
    # dict= dict["csa_rules"]

    print("read tags from source uri")
    #bucketname, video_blobname = gcs.split_gcs_uri(uri)
    tags = gcs.read_tags_from_gcs(bucketname, name)

    if tags is None:
        print("no tags found. WARNING do not save.")
    else:
        print(f"uri= {uri} - tags = {tags}")
        dict.update(tags)     
        tags["description"]       = res
        # generate time
        tags["update_time"]       = utils.get_date_time_string()

        tags["uri"] = uri
        df = pd.DataFrame([tags])

        print(df.to_json())
        bq.save_bq(df,config.BQ_TABLE_GEMINI_RESULT, project_id=config.PROJECT_ID )
        print("saved in bq")
    return tags


def moderate_video_old(uri, name):
    
    # try:
    res = gemini.content_moderation_gemini(uri)
    print(f"moderation content done on chunck uri {uri} with res = {res}")

    print("save json result in output bucket")
    json_file_path = gcs.write_text_to_gcs(config.OUTPUT_BUCKET, utils.replace_extension(name, ".json"), res, "text/json")
    print(f"json_file_path = {json_file_path}")

    dict= json.loads(res)
    dict= dict["csa_rules"]

    print("read tags from source uri")
    bucketname, video_blobname = gcs.split_gcs_uri(uri)
    tags = gcs.read_tags_from_gcs(bucketname, video_blobname)

    if tags is None:
        print("no tags found")
    else:
        print(f"uri= {uri} - tags = {tags}")
        dict.update(tags)            

    dict["uri"] = uri
    df = pd.DataFrame([dict])

    bq.save_bq(df,config.BQ_TABLE_GEMINI_RESULT, project_id=config.PROJECT_ID )
    # except Exception as e:
    #     print(f"ERROR in content_moderation(uri) = {uri}")
    #     print(e)




# Triggered by a change in a storage bucket
@functions_framework.cloud_event
def process_event_json(cloud_event):
    bucket, name, contentType = dump_event(cloud_event)

    if contentType == "application/octet-stream" or contentType == "text/json"  or contentType == "application/json":
        print("Processing json file: ", name)
        data = gcs.read_json_from_gcs(bucket, name)
        try:
            gvi.splitVideo(data)
        except Exception as e:
            print(f"ERROR in splitVideo(data) = {data}")
            print(e)

        try:
            print('Store json in BQ')
            gvi.storeVideoIntelligenceData(data)
        except Exception as e:
            print(f"ERROR in splitVideo(data) = {data}")
            print(e)

    else :
        print("Unsupported file type: ", contentType)

    print("end.") 

def dump_event(cloud_event):
    data = cloud_event.data

    event_id = cloud_event["id"]
    event_type = cloud_event["type"]

    bucket = data["bucket"]    
    name = data["name"]
    metageneration = data["metageneration"]
    timeCreated = data["timeCreated"]
    updated = data["updated"]
    contentType = data["contentType"]

    print(f"Event ID: {event_id} - Event type: {event_type} - Bucket: {bucket} - File: {name} - Metageneration: {metageneration} - ContentType: {contentType} - TimeCreated: {timeCreated} - Updated: {updated}")

    return bucket,name,contentType



# Triggered by a change in a storage bucket
@functions_framework.cloud_event
def process_event_video(cloud_event):
    bucket, name, contentType = dump_event(cloud_event)

    if contentType == "video/mp4" and ".mp4" in name:

        input_uri =  "gs://" + bucket + "/" + name
        
        file_system = name.split(".")[0].split("/")[-1]
        
        language_code = getLanguageCode(input_uri)

        if config.SPLIT_BY_FEATURES == "1" :
            gvi.annotate_video_split_by_features(input_uri, file_system, language_code)
        else:
            gvi.annotate_video(input_uri, file_system, language_code)
        

    elif contentType == "application/octet-stream" or contentType == "text/json"  or contentType == "application/json":
        print("Processing json file: ", name)
        data = gcs.read_json_from_gcs(bucket, name)

        from google.cloud import videointelligence_v1 as vi
        annotation = vi.AnnotateVideoResponse(data)
        
        content_moderation_text_based = None
        texts = None
        index = 0
        for annotation_result in annotation.annotation_results:

            print(f"Finished processing input: {annotation_result.input_uri}" ) 
            uri  = "gs:/"+annotation_result.input_uri
            
            print(f"full uri = {uri}")

            bucketname, video_blobname = gcs.split_gcs_uri(uri)
            print(f"bucketname = {bucketname} - blobname = {video_blobname}")

            localfile = video_blobname.replace("/", "_") # -{index}
            print(f"localfile = {localfile}")

            video_input = gcs.store_temp_video_from_gcs(bucketname, video_blobname, localfile= localfile)
            
            print(f"video_input = {video_input}")

            for input_part, t1,t2 in videoedit.split_video_shots_time_min(video_input,annotation_result , config.MIN_SHOT_DURATION_SECONDS):
                print(f"split_video_shots input_part = {input_part}")
                index = index + 1

                gcs_file_name = f"{config.TAG_TO_ANALYZE}/{video_blobname}/chunks - {index} - {t1} - {t2}.mp4"
                print(f"write in output bucket chunck file gcs_file_name = {gcs_file_name}")
                tags = {
                    "video_source": uri,                    
                    "video_blobname": video_blobname,
                    "index": index,
                    "time_start": t1,
                    "time_stop": t2                    
                }

                # write in output bucket chunck file                
                blob = gcs.write_file_to_gcs(config.OUTPUT_BUCKET, 
                                             gcs_file_name=gcs_file_name, 
                                             local_file_path=input_part, 
                                             tags=tags)
                
                chunck_uri=  f"gs://{config.OUTPUT_BUCKET}/{blob.name}"

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

def getLanguageCode(input_uri):
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
    return language_code





# Triggered by a change in a storage bucket
@functions_framework.cloud_event
def process_event_embedding(cloud_event):
    bucket, name, contentType = dump_event(cloud_event)
    