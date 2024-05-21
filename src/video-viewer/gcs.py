    
import json
import pandas as pd
from google.cloud import storage

import config as config

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
        return data

    except Exception as e:
        print(f"Error reading JSON file: {e}")
        return None
    
def read_tags_from_gcs(bucket_name, blob_name):

    """Retrieves the metadata of a GCS blob."""
    client = storage.Client()
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.reload()  # Ensure metadata is up-to-date

    return blob.metadata

def write_text_to_gcs(bucket_name, file_name, text, mime_type="text/plain"):
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
        bucket.blob(file_name).upload_from_string(text, mime_type)

        return bucket.path
    except Exception as e:
        print(f"Error writing gcs text: {e}")
        return None
        

import re

def split_gcs_uri(gcs_uri):
  """Splits a GCS URI into bucket name and blob path variables.

  Args:
    gcs_uri: The GCS URI to split.

  Returns:
    A tuple containing the bucket name and blob path.
  """

  match = re.match(r"gs://([^/]+)/(.+)", gcs_uri)
  if match:
    return match.groups()
  else:
    raise ValueError("Invalid GCS URI: {}".format(gcs_uri))


def store_temp_video_from_gcs(bucket_name, file_name, localfile):
    import tempfile
    import os

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)

    # try:        
    bytes_data = blob.download_as_bytes()
    
    # Create a temporary file.
    # tempDir = tempfile.gettempdir()
    tempDir = os.getcwd()

    temp_path = os.path.join(tempDir, localfile)
    # f, temp_path = tempfile.mkstemp()
    fp = open(temp_path, 'bw')
    fp.write(bytes_data)
    fp.seek(0)

    # with tempfile.NamedTemporaryFile(delete_on_close=False, mode='rb') as fp:
    #     fp.write(bytes_data)
    #     fp.close()
    #     return fp.name

        # # Write the file's contents to the temporary file.
        # f.w.write(bytes_data)

    # Close the temporary file.
    # f.close()
    return temp_path
                
    # except Exception as e:
    #     print(f"Error reading video file: {e}")
    #     return None

def write_file_to_gcs(gcs_bucket_name,  gcs_file_name, local_file_path, tags = None):
    """Writes a local file to GCS.

    Args:
    local_file_path: The path to the local file to write to GCS.
    gcs_bucket_name: The name of the GCS bucket to write the file to.
    gcs_file_name: The name of the GCS file to write the file to.

    Returns:
    The GCS file path.
    """
    print(f"local_file_path = {local_file_path} - gcs_bucket_name = {gcs_bucket_name} - gcs_file_name = {gcs_file_name}")
    storage_client = storage.Client()
    bucket = storage_client.bucket(gcs_bucket_name)
    blob = bucket.blob(gcs_file_name)
    if tags is not None:
        blob.metadata = tags

    print(f"upload_from_filename : local_file_path = {local_file_path}")
    blob.upload_from_filename(local_file_path, ) 

    return blob


import datetime

from google.cloud import storage
from google.auth import compute_engine
import google.auth

def generate_download_signed_url(uri):
    bucket_name, blob_name = split_gcs_uri(uri)
    return generate_download_signed_url_v4(bucket_name, blob_name)

def generate_download_signed_url_v4(bucket_name, blob_name):
    """Generates a v4 signed URL for downloading a blob.

    Note that this method requires a service account key file. You can not use
    this if you are using Application Default Credentials from Google Compute
    Engine or from the Google Cloud SDK.
    """
    # bucket_name = 'your-bucket-name'
    # blob_name = 'your-object-name'

    storage_client = storage.Client.from_service_account_json("/Users/julienmiquel/dev/vi-dev2/video-intelligence/credentials.json")

    #storage_client = storage.Client(project=config.PROJECT_ID)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)


    # auth_request = google.auth.transport.requests.Request()
    # credentials, project = google.auth.default()


    # signing_credentials = compute_engine.IDTokenCredentials(
    #     auth_request,
    #     "",
    #     service_account_email=credentials.external_account_id
    # )

    from google.auth.transport import requests
    from google.auth import default, compute_engine, load_credentials_from_file
    
    #credentials = load_credentials_from_file("/Users/julienmiquel/dev/vi-dev2/video-intelligence/credentials.json")
    #credentials, project = default()
    
    # then within your abstraction
    #auth_request = requests.Request()
    #credentials.refresh(auth_request)
    
    # signing_credentials = compute_engine.IDTokenCredentials(
    #     auth_request,
    #     "",
    #     service_account_email=credentials.service_account_email
    # )

    url = blob.generate_signed_url(
        version="v4",
        #credentials=credentials,
        # This URL is valid for 15 minutes
        expiration=datetime.timedelta(days=6),
        #expiration=datetime.timedelta(minutes=15),
        
        # Allow GET requests using this URL.
        method="GET",
        
    )

    print("Generated GET signed URL:")
    print(url)
    print("You can use this URL with any user agent, for example:")
    print(f"curl '{url}'")
    return url