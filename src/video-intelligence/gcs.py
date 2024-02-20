    
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
        #df = pd.json_normalize(data)
        #data_json = df.to_json( orient="records")
        #data_str = data_json.dumps(orient="records")
        #bucket.blob(file_name + "_flattened.json").upload_from_string(data_json, 'text/json')

        return data
    except Exception as e:
        print(f"Error reading JSON file: {e}")
        return None

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


def store_temp_video_from_gcs(bucket_name, file_name):
    import tempfile

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)

    try:        
        bytes_data = blob.download_as_bytes()
        # Create a temporary file.
        f, temp_path = tempfile.mkstemp()

        # Write the file's contents to the temporary file.
        f.write(bytes_data)

        # Close the temporary file.
        f.close()
        return temp_path
                
    except Exception as e:
        print(f"Error reading video file: {e}")
        return None

def write_file_to_gcs(local_file_path, gcs_bucket_name, gcs_file_name):
  """Writes a local file to GCS.

  Args:
    local_file_path: The path to the local file to write to GCS.
    gcs_bucket_name: The name of the GCS bucket to write the file to.
    gcs_file_name: The name of the GCS file to write the file to.

  Returns:
    The GCS file path.
  """

  storage_client = storage.Client()
  bucket = storage_client.bucket(gcs_bucket_name)
  blob = bucket.blob(gcs_file_name)



  blob.upload_from_filename(local_file_path) 

  return blob.path