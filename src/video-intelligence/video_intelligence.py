from typing import MutableSequence
import gcs as gcs
import bq as bq
import videoedit as videoedit
import config as config

import pandas as pd
import time


from google.cloud import videointelligence_v1 as vi

video_client = vi.VideoIntelligenceServiceClient()

features = [
    # vi.Feature.OBJECT_TRACKING,
    vi.Feature.LABEL_DETECTION,
    vi.Feature.SHOT_CHANGE_DETECTION,
    vi.Feature.SPEECH_TRANSCRIPTION,
    # vi.Feature.LOGO_RECOGNITION,
    vi.Feature.EXPLICIT_CONTENT_DETECTION,
    vi.Feature.TEXT_DETECTION,
    vi.Feature.FACE_DETECTION,
    # vi.Feature.PERSON_DETECTION,
]
 

def featureId(feature):
    if feature == vi.Feature.OBJECT_TRACKING:
        return "OBJECT_TRACKING"
    if feature == vi.Feature.LABEL_DETECTION:
        return "LABEL_DETECTION"
    if feature == vi.Feature.SHOT_CHANGE_DETECTION:
        return "SHOT_CHANGE_DETECTION"
    if feature == vi.Feature.SPEECH_TRANSCRIPTION:
        return "SPEECH_TRANSCRIPTION"
    if feature == vi.Feature.LOGO_RECOGNITION:
        return "LOGO_RECOGNITION"
    if feature == vi.Feature.EXPLICIT_CONTENT_DETECTION:
        return "EXPLICIT_CONTENT_DETECTION"
    if feature == vi.Feature.TEXT_DETECTION:
        return "TEXT_DETECTION"
    if feature == vi.Feature.FACE_DETECTION:
        return "FACE_DETECTION"
    if feature == vi.Feature.PERSON_DETECTION:
        return "PERSON_DETECTION"
    
    return "UNKNOWN"


def storeVideoIntelligenceData(data):

    annotation = vi.AnnotateVideoResponse(data)
    try:
        df = ExplicitContentToDF(annotation)
        bq.save_bq(df,config.BQ_TABLE_VIDEO_INTELLIGENCE_EXPLICIT_CONTENT, project_id=config.PROJECT_ID )
    except Exception as e:
        print(f"storeVideoIntelligenceData ExplicitContentToDF Exception = {e}")

    try:
        df = TextToDF(annotation)
        bq.save_bq(df,config.BQ_TABLE_VIDEO_INTELLIGENCE_TEXT, project_id=config.PROJECT_ID )
    except Exception as e:
        print(f"storeVideoIntelligenceData TextToDF Exception = {e}")


    try:
        df = LabelsToDF(annotation)
        bq.save_bq(df,config.BQ_TABLE_VIDEO_INTELLIGENCE_LABEL, project_id=config.PROJECT_ID )
    except Exception as e:
        print(f"storeVideoIntelligenceData TextContentToDF Exception = {e}")


    # for annotation_result in annotation.annotation_results:
    #     print(f"Finished processing input: {annotation_result.input_uri}" ) 
    #     uri  = "gs:/"+annotation_result.input_uri
        
    #     print(f"full uri = {uri}")
    #     # gs://video-input-bucket-2f60/fr-FR/cdanslair.mp4

    #     # if len(annotation_result.explicit_annotation.frames) > 0:# is not None:
    #     #     print("processing explicit_annotation")
    #     #     process_shots(annotation_result.explicit_annotation.frames, index, uri, video_blobname, video_input)
        
    #     if len(annotation_result.shot_annotations) > 0:# is not None:
    #         print("processing shot_annotations")
    #         process_shots(annotation_result.shot_annotations, index, uri, video_blobname, video_input)
        
    #     if len(annotation_result.text_annotations) > 0:# is not None:
    #         print("processing text_annotations")
    #         process_shots(annotation_result.text_annotations, index, uri, video_blobname, video_input)



def splitVideo(data):
    
    annotation = vi.AnnotateVideoResponse(data)
    
    content_moderation_text_based = None
    texts = None
    for annotation_result in annotation.annotation_results:
        # ex: input_bucket     "input_uri": "/video-input-bucket-2f60/fr-FR/cdanslair.mp4",
        index = 0

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

        # if len(annotation_result.explicit_annotation.frames) > 0:# is not None:
        #     print("processing explicit_annotation")
        #     process_shots(annotation_result.explicit_annotation.frames, index, uri, video_blobname, video_input)
        
        if len(annotation_result.shot_annotations) > 0:# is not None:
            print("processing shot_annotations")
            process_shots(annotation_result.shot_annotations, index, uri, video_blobname, video_input)
        
        if len(annotation_result.text_annotations) > 0:# is not None:
            print("processing text_annotations")
            process_shots(annotation_result.text_annotations, index, uri, video_blobname, video_input)



def process_shots(shots, index, uri, video_blobname, video_input):
    for input_part, t1,t2 in videoedit.split_video_shots(video_input,shots ):
        print(f"split_video_shots input_part = {input_part}")
        index = index + 1
            # remove file extention
            #video_blobname = os.path.splitext(video_blobname)[0]

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


def annotate_video(input_uri, file_system, language_code):
    
    output_uri = f"gs://{config.WORKING_BUCKET}/{language_code}/{file_system} - {time.time()}.json"
        
    print(f"input_uri = {input_uri} - output_uri = {output_uri} file_sytem = {file_system}")

    person_config = vi.PersonDetectionConfig(
            include_bounding_boxes=True,
            include_attributes=True,
            include_pose_landmarks=True,
        )
        
    face_config = vi.FaceDetectionConfig(
            include_bounding_boxes=True,
            include_attributes=True,
        )
    speech_config = vi.SpeechTranscriptionConfig(
            language_code=language_code,
            enable_automatic_punctuation=True,
            enable_speaker_diarization=True,
            #diarization_speaker_count=2,
        )

    video_context = vi.VideoContext(
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

        output_uri = f"gs://{config.WORKING_BUCKET}/{language_code}/{featureId(feature)}/{file_system} - {time.time()}.json"
            
        print(f"input_uri = {input_uri} - output_uri = {output_uri} file_sytem = {file_system}")

        person_config = vi.PersonDetectionConfig(
                include_bounding_boxes=True,
                include_attributes=True,
                include_pose_landmarks=True,
            )
            
        face_config = vi.FaceDetectionConfig(
                include_bounding_boxes=True,
                include_attributes=True,
            )
        speech_config = vi.SpeechTranscriptionConfig(
                language_code=language_code,
                enable_automatic_punctuation=True,
                enable_speaker_diarization=True,
                #diarization_speaker_count=2,
            )

        video_context = vi.VideoContext(
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


def ExplicitContentToDF(annotation):
    rows = []

    for annotation_result in annotation.annotation_results:
        print(f"Finished processing input: {annotation_result.input_uri}" ) 
        
        
        # Retrieve first result because a single video was processed
        for frame in annotation_result.explicit_annotation.frames:
            row = []
            row.append(annotation_result.input_uri)
            #start = frame.time_offset.seconds
            frame_time = frame.time_offset.seconds + frame.time_offset.microseconds / 1e6
            start = frame_time
            #stop = None
            likelihood = vi.Likelihood(frame.pornography_likelihood)

            row.append(start)
            #row.append(stop)
            row.append(likelihood.name)
            rows.append(row)

            
            #print(f"Time: {frame_time}s \texplicit content: {likelihood.name}")
    
    if rows.count == 0:
        print("No explicit content found")
        return None
    
    df = pd.DataFrame(rows, columns=["uri","start",  "explicit_content"])
    return df


def TextToDF(annotation):
    rows = []

    for annotation_result in annotation.annotation_results:
        print(f"Processing json text results from input: {annotation_result.input_uri}" ) 
                
        for text_annotation in annotation_result.text_annotations:
            row = []

            text = text_annotation.text            
            row.append(annotation_result.input_uri)

            # Get the first text segment
            text_segment = text_annotation.segments[0]
 
            start_time = text_segment.segment.start_time_offset.seconds + text_segment.segment.start_time_offset.microseconds * 1e-6
            end_time = text_segment.segment.end_time_offset.seconds + text_segment.segment.end_time_offset.microseconds * 1e-6
            
            if text_segment.confidence > 0.3:
                row.append(start_time)
                row.append(end_time)
                row.append(text)
                rows.append(row)

    if rows.count == 0:
        print("No text found")
        return None
    
    df = pd.DataFrame(rows, columns=["uri","start", "stop", "text_segment"])
    return df





def LabelsToDF(annotation):
    rows = []

    for annotation_result in annotation.annotation_results:
        print(f"Finished processing input: {annotation_result.input_uri}" ) 
        

        # Process video/segment level label annotations
        segment_labels = annotation_result.segment_label_annotations
        for i, segment_label in enumerate(segment_labels):
            print("Video label description: {}".format(segment_label.entity.description))
            segment_label.entity
            for category_entity in segment_label.category_entities:

                row = []

                text_segment = category_entity.description                

                for index, segment in enumerate(segment_label.segments):
                    
                    start_time = (
                        segment.segment.start_time_offset.seconds
                        + segment.segment.start_time_offset.microseconds / 1e6
                    )
                    end_time = (
                        segment.segment.end_time_offset.seconds
                        + segment.segment.end_time_offset.microseconds / 1e6
                    )
                    positions = "{}s to {}s".format(start_time, end_time)
                    confidence = segment.confidence
                    # print("\tSegment {}: {}".format(i, positions))
                    # print("\tConfidence: {}".format(confidence))
                    # print("\n")

                    # # Process shot level label annotations
                    # shot_labels = annotation_result.shot_label_annotations
                    # for i, shot_label in enumerate(shot_labels):
                    #     print("Shot label description: {}".format(shot_label.entity.description))
                    #     for category_entity in shot_label.category_entities:
                    #         print(
                    #             "\tLabel category description: {}".format(category_entity.description)
                    #         )

                    #     for i, shot in enumerate(shot_label.segments):
                    #         start_time = (
                    #             shot.segment.start_time_offset.seconds
                    #             + shot.segment.start_time_offset.microseconds / 1e6
                    #         )
                    #         end_time = (
                    #             shot.segment.end_time_offset.seconds
                    #             + shot.segment.end_time_offset.microseconds / 1e6
                    #         )
                    #         positions = "{}s to {}s".format(start_time, end_time)
                    #         confidence = shot.confidence
                    #         print("\tSegment {}: {}".format(i, positions))
                    #         print("\tConfidence: {}".format(confidence))
                    #     print("\n")

                    # # Process frame level label annotations
                    # frame_labels = result.annotation_results[0].frame_label_annotations
                    # for i, frame_label in enumerate(frame_labels):
                    #     print("Frame label description: {}".format(frame_label.entity.description))
                    #     for category_entity in frame_label.category_entities:
                    #         print(
                    #             "\tLabel category description: {}".format(category_entity.description)
                    #         )

                    # # Each frame_label_annotation has many frames,
                    # # here we print information only about the first frame.
                    # frame = frame_label.frames[0]
                    # time_offset = frame.time_offset.seconds + frame.time_offset.microseconds / 1e6
                    # print("\tFirst frame time offset: {}s".format(time_offset))
                    # print("\tFirst frame confidence: {}".format(frame.confidence))
                    # print("\n")
                    if confidence> 0.3:
                        row.append(annotation_result.input_uri)
        
                        row.append(start_time)
                        row.append(end_time)
                        row.append(text_segment)
                        rows.append(row)

                    
                    #print(f"Time: {frame_time}s \tpornography: {likelihood.name}")
    if rows.count == 0:
        print("No labels found")
        return None

    df = pd.DataFrame(rows, columns=["uri","start", "stop", "text_segment"])
    return df
