import base64
import time
import typing

from google.cloud import aiplatform
from google.protobuf import struct_pb2
import requests
import config as config


class EmbeddingResponse(typing.NamedTuple):
    text_embedding: typing.Sequence[float]
    image_embedding: typing.Sequence[float]


def load_image_bytes(image_uri: str) -> bytes:
    """Load image bytes from a remote or local URI."""
    image_bytes = None
    if image_uri.startswith("http://") or image_uri.startswith("https://"):
        response = requests.get(image_uri, stream=True)
        if response.status_code == 200:
            image_bytes = response.content
    else:
        image_bytes = open(image_uri, "rb").read()
    return image_bytes


class EmbeddingPredictionClient:
    """Wrapper around Prediction Service Client."""

    def __init__(
        self,
        project: str,
        location: str = config.REGION,
        api_regional_endpoint: str = f"{config.REGION}-aiplatform.googleapis.com",
    ):
        client_options = {"api_endpoint": api_regional_endpoint}
        # Initialize client that will be used to create and send requests.
        # This client only needs to be created once, and can be reused for multiple requests.
        self.client = aiplatform.gapic.PredictionServiceClient(
            client_options=client_options
        )
        self.location = location
        self.project = project

    def get_embedding(self, text: str = None, image_file: str = None):
        if not text and not image_file:
            raise ValueError("At least one of text or image_file must be specified.")

        # Load image file
        image_bytes = None
        if image_file:
            image_bytes = load_image_bytes(image_file)

        instance = struct_pb2.Struct()
        if text:
            instance.fields["text"].string_value = text

        if image_bytes:
            encoded_content = base64.b64encode(image_bytes).decode("utf-8")
            image_struct = instance.fields["image"].struct_value
            image_struct.fields["bytesBase64Encoded"].string_value = encoded_content

        instances = [instance]
        endpoint = (
            f"projects/{self.project}/locations/{self.location}"
            "/publishers/google/models/multimodalembedding@001"
        )
        response = self.client.predict(endpoint=endpoint, instances=instances)

        text_embedding = None
        if text:
            text_emb_value = response.predictions[0]["textEmbedding"]
            text_embedding = [v for v in text_emb_value]

        image_embedding = None
        if image_bytes:
            image_emb_value = response.predictions[0]["imageEmbedding"]
            image_embedding = [v for v in image_emb_value]

        return EmbeddingResponse(
            text_embedding=text_embedding, image_embedding=image_embedding
        )
    

from typing import Optional

import vertexai
from vertexai.vision_models import (
    Image,
    MultiModalEmbeddingModel,
    MultiModalEmbeddingResponse,
    Video,
    VideoSegmentConfig,
)

from tenacity import retry, stop_after_attempt, wait_random_exponential

#TODO: retry if pandas_gbq.exceptions.GenericGBQException  Reason: 403 Exceeded rate limits

class EmbeddingVideo(typing.NamedTuple):
    video_source:str
    start:float
    stop: float
    text_embedding: typing.Sequence[float]
    #image_embedding: typing.Sequence[float]

@retry(wait=wait_random_exponential(min=10, max=60), stop=stop_after_attempt(100) )
def get_image_video_text_embeddings(
    project_id: str,
    location: str,
#    image_path: str,
    video_path: str,
    contextual_text: Optional[str] = None,
    dimension: Optional[int] = 1408,
    video_segment_config: Optional[VideoSegmentConfig] = None,
) -> MultiModalEmbeddingResponse:
    """Example of how to generate multimodal embeddings from image, video, and text.

    Args:
        project_id: Google Cloud Project ID, used to initialize vertexai
        location: Google Cloud Region, used to initialize vertexai
        image_path: Path to image (local or Google Cloud Storage) to generate embeddings for.
        video_path: Path to video (local or Google Cloud Storage) to generate embeddings for.
        contextual_text: Text to generate embeddings for.
        dimension: Dimension for the returned embeddings.
            https://cloud.google.com/vertex-ai/docs/generative-ai/embeddings/get-multimodal-embeddings#low-dimension
        video_segment_config: Define specific segments to generate embeddings for.
            https://cloud.google.com/vertex-ai/docs/generative-ai/embeddings/get-multimodal-embeddings#video-best-practices
    """

    vertexai.init(project=project_id, location=location)

    model = MultiModalEmbeddingModel.from_pretrained("multimodalembedding")
    #image = Image.load_from_file(image_path)
    video = Video(gcs_uri=video_path)

    contextual_text_input = contextual_text
    if len(contextual_text_input) > 1024:
        #TODO: Find better way to truncate
        contextual_text_input = contextual_text_input[0:1000]

    embeddings = model.get_embeddings(
        #image=image,
        video=video,
        video_segment_config=video_segment_config,
        contextual_text=contextual_text_input,
        dimension=dimension,
    )

    print(f"Image Embedding: {embeddings.image_embedding}")

    # Video Embeddings are segmented based on the video_segment_config.
    print("Video Embeddings:")
    arr = []
    for video_embedding in embeddings.video_embeddings:
        print(
            f"Video Segment: {video_embedding.start_offset_sec} - {video_embedding.end_offset_sec}"
        )
        print(f"Embedding: {video_embedding.embedding}")

        arr.append(
            {
                'video_source':video_path,
                'description':contextual_text,
                'start':video_embedding.start_offset_sec,
                'stop': video_embedding.end_offset_sec,
                'embeddings': video_embedding.embedding ,
            }
        )

    print(f"Text Embedding: {embeddings.text_embedding}")    

    return arr