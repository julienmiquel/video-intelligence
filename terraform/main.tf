# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

resource "random_id" "video_intelligence" {
  byte_length = 2
}

module "video_intelligence" {
  source = "./video-intelligence"

  project_id            = var.project_id
  region                = var.region
  # wf_region             = var.wf_region
  suffix                = random_id.video_intelligence.hex
  # image_dlp_runner      = "gcr.io/${var.project_id}/dlp-runner"
  # image_findings_writer = "gcr.io/${var.project_id}/findings-writer"
  # image_video_merger      = "gcr.io/${var.project_id}/video-merger"
  # image_video_splitter    = "gcr.io/${var.project_id}/video-splitter"
}
