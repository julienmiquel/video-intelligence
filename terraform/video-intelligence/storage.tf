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

resource "google_storage_bucket" "video_input_bucket" {
  name          = "video-input-bucket${local.app_suffix}"
  uniform_bucket_level_access = true
  location      = var.region
  force_destroy = true
}

resource "google_storage_bucket" "working_bucket" {
  name          = "video-working-bucket${local.app_suffix}"
  uniform_bucket_level_access = true
  location      = var.region
  force_destroy = true
  lifecycle_rule {
    condition {
      age = 1
    }
    action {
      type = "Delete"
    }
  }
}

resource "google_storage_bucket" "video_output_bucket" {
  uniform_bucket_level_access = true
  name          = "video-output-bucket${local.app_suffix}"
  location      = var.region
  force_destroy = true
}


## static website for video output viewer
resource "google_storage_bucket" "video_output_viewer_bucket" {
  uniform_bucket_level_access = true
  name          = "video_output_viewer_bucket${local.app_suffix}"
  location      = var.region
  force_destroy = true
  public_access_prevention = "inherited"
  website {
    main_page_suffix = "index.html"
    not_found_page   = "404.html"
  }
  
}

# Upload a simple index.html page to the bucket
resource "google_storage_bucket_object" "indexpage" {
  name         = "index.html"  
  source = "../src/video_view_static_site/index.html"
  content_type = "text/html"
  
  bucket       = google_storage_bucket.video_output_viewer_bucket.id
}

# Upload a simple 404 / error page to the bucket
resource "google_storage_bucket_object" "errorpage" {
  name         = "404.html"
  content      = "<html><body>404!</body></html>"
  content_type = "text/html"
  bucket       = google_storage_bucket.video_output_viewer_bucket.id
}

# Make bucket public by granting allUsers READER access
# resource "google_storage_bucket_access_control" "public_rule" {
#   bucket = google_storage_bucket.video_output_viewer_bucket.id
#   role   = "READER"
#   entity = "allUsers"
# }