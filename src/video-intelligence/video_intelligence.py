from typing import MutableSequence
import gcs as gcs
import videoedit as videoedit
import config as config



from google.cloud import videointelligence_v1 as vi

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