import os

REGION_BACKUP_2  = os.environ.get("REGION", "europe-west4")
REGION_BACKUP  = os.environ.get("REGION", "europe-west3")
REGION  = os.environ.get("REGION", "europe-west1")

REGIONS = [REGION, REGION_BACKUP, REGION_BACKUP_2]

PROJECT_ID= os.environ.get("PROJECT_ID", "")
OUTPUT_BUCKET  = os.environ.get("OUTPUT_BUCKET", "")
SPLIT_BY_FEATURES  = os.environ.get("SPLIT_BY_FEATURES", "1")

INPUT_BUCKET  = os.environ.get("INPUT_BUCKET", "")
WORKING_BUCKET  = os.environ.get("WORKING_BUCKET", "")

BQ_DATASET = os.environ.get("BQ_DATASET", "media")

BQ_TABLE_EMBEDDINGS = os.environ.get("BQ_TABLE_EMBEDDINGS", f"{PROJECT_ID}.{BQ_DATASET}.video_embeddings")
BQ_TABLE_GEMINI_RESULT = os.environ.get("BQ_TABLE_GEMINI_RESULT", f"{BQ_DATASET}.results")
BQ_TABLE_VIDEO_INTELLIGENCE_EXPLICIT_CONTENT = os.environ.get("BQ_TABLE_VIDEO_INTELLIGENCE_EXPLICIT_CONTENT", f"{BQ_DATASET}.video_intelligence_explicit_content")
BQ_TABLE_VIDEO_INTELLIGENCE_TEXT = os.environ.get("BQ_TABLE_VIDEO_INTELLIGENCE_TEXT", f"{BQ_DATASET}.video_intelligence_ocr")
BQ_TABLE_VIDEO_INTELLIGENCE_LABEL = os.environ.get("BQ_TABLE_VIDEO_INTELLIGENCE_LABEL", f"{BQ_DATASET}.video_intelligence_labels")

BQ_TABLE_VIDEO_INTELLIGENCE = os.environ.get("BQ_TABLE_VIDEO_INTELLIGENCE", f"{BQ_DATASET}.video_intelligence")

TAG_TO_ANALYZE = "CSA"

VIDEO_SHOT_MIN_DURATION = os.environ.get("VIDEO_SHOT_MIN_DURATION", 5)

MODEL_MULTIMODAL = os.environ.get("MODEL_MULTIMODAL", "gemini-1.0-pro-vision-001")