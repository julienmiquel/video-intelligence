import gcs as gcs 
import videoedit as videoedit
import videoedit as gemini

from google.cloud import videointelligence_v1 as vi

WORKING_BUCKET = "gs://video-output-bucket-2f60"
bucket = "video-working-bucket-2f60"
name ="fr-FR/SHOT_CHANGE_DETECTION/Copy of De la France aux Etats-Unis, l’explosion des actes antisémites - Reportage #cdanslair 13 - 1708432565.7205172.json"

def test2():
    uri = "gs://video-input-bucket-2f60/fr-FR/De la France aux Etats-Unis, l’explosion des actes antisémites - Reportage #cdanslair 13.02.2024.mp4 - 43 - 192.28 - 206.6.mp4"
    bucketname, blobname = gcs.split_gcs_uri(uri)
    print(bucketname, blobname)
    video_input = gcs.store_temp_video_from_gcs(bucketname, blobname)
    print(video_input)




def test1():
    print("Processing json file: ", name)
    data = gcs.read_json_from_gcs(bucket, name)

    from google.cloud import videointelligence_v1 as vi
    annotation = vi.AnnotateVideoResponse(data)

    content_moderation_text_based = None
    texts = None
    for annotation_result in annotation.annotation_results:
        print(f"Finished processing input: {annotation_result.input_uri}" ) 
        uri  = "gs:/"+annotation_result.input_uri
        print(f"uri = {uri}")

        bucketname, blobname = gcs.split_gcs_uri(uri)
        print(bucketname, blobname)

        print(80*"-")
        video_input = gcs.store_temp_video_from_gcs(bucketname, blobname, annotation_result.input_uri)
        for input_part in videoedit.split_video_shots(video_input,annotation_result ):
            print(80*"*")
            print(f"input_part = {input_part}")
            file_name = f"/chunk/{input_part}"

            uri = gcs.write_file_to_gcs(gcs_file_name=file_name, 
                gcs_bucket_name=WORKING_BUCKET, 
                local_file_path= input_part)
            
            print(uri)
            res = gemini.content_moderation_gemini(uri)
            print(res)
            gcs.write_text_to_gcs(WORKING_BUCKET, file_name.replace(".mp4", ".json"), res, "text/json")


def test3():
    local_file_path = "/Users/julienmiquel/dev/vi-dev2/video-intelligence/temp.mp4" 
    gcs_bucket_name = "video-output-bucket-2f60" 
    gcs_file_name = "temp.mp4"
    uri = gcs.write_file_to_gcs(gcs_file_name=gcs_file_name, 
        gcs_bucket_name=WORKING_BUCKET, 
        local_file_path= local_file_path)

    print(uri)

test1()


