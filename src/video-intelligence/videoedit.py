
from datetime import timedelta
from typing import Optional, Sequence, cast

import base64
import vertexai
from vertexai.preview.generative_models import GenerativeModel, Part
import vertexai.preview.generative_models as generative_models

from moviepy.editor import VideoFileClip
from google.cloud import videointelligence_v1 as vi
from moviepy.editor import VideoFileClip

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
    if results is None:
        return

    if results.shot_annotations is None:
        return

    shots = results.shot_annotations
    if len(shots) == 0:
        return
    
    # if len(shots) == 1:
    #     yield input_video
    #     return
    

    print(f" Video shots: {len(shots)} ".center(40, "-"))
    for i, shot in enumerate(shots):
        t1 = shot.start_time_offset.total_seconds()
        t2 = shot.end_time_offset.total_seconds()
        print(f"{i+1:>3} | {t1:7.3f} | {t2:7.3f}")
        output_video = f"{input_video } - {i} - {t1} - {t2}.mp4"
        
        split_video(input_video=input_video, output_video=output_video, start=t1, end=t2)
        yield output_video


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
    