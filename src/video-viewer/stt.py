from time import sleep
from grpc import StatusCode
import config as config
import json

import vertexai


from tenacity import retry, stop_after_attempt, wait_random_exponential

from pathlib import Path as p

import pandas as pd
import json

from google.cloud.speech_v2 import SpeechClient
from google.cloud.speech_v2.types import cloud_speech
from google.api_core.client_options import ClientOptions





def convert(uri, language_code= "en-US"):
    
    client = SpeechClient(
            client_options=ClientOptions(api_endpoint=f"{config.REGION}-speech.googleapis.com")
        )
    recognizer_id = f"chirp-{language_code.lower()}-test"

    try:
        recognizer_request = cloud_speech.CreateRecognizerRequest(
            parent=f"projects/{config.PROJECT_ID}/locations/{config.REGION}",
            recognizer_id=recognizer_id,
            recognizer=cloud_speech.Recognizer(
                language_codes=[language_code],
                model="chirp",
            ),
        )

        create_operation = client.create_recognizer(request=recognizer_request)
        recognizer = create_operation.result()
    except Exception as e:
        print(e)

    long_audio_config = cloud_speech.RecognitionConfig(
        features=cloud_speech.RecognitionFeatures(
            enable_automatic_punctuation=True, enable_word_time_offsets=True
        ),
        auto_decoding_config={},
    )

    long_audio_request = cloud_speech.BatchRecognizeRequest(
        recognizer=recognizer.name,
        recognition_output_config={
            "gcs_output_config": {"uri": f"{config.WORKING_BUCKET}/transcriptions"}
        },
        files=[{"config": long_audio_config, "uri": uri}],
    )


    long_audio_operation = client.batch_recognize(request=long_audio_request)
    long_audio_result = long_audio_operation.result()
    print(long_audio_result)