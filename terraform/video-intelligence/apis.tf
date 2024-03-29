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

module "project_services" {
  source  = "terraform-google-modules/project-factory/google//modules/project_services"
  version = "13.0.0"

  project_id = var.project_id

  activate_apis = [
    "notebooks.googleapis.com",
    "artifactregistry.googleapis.com",
    "dataform.googleapis.com",
    "dataflow.googleapis.com",
    "storage-component.googleapis.com",
    "visionai.googleapis.com",
    "aiplatform.googleapis.com",
    "iam.googleapis.com",
    "serviceusage.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "run.googleapis.com",
    "cloudbuild.googleapis.com",
    "cloudfunctions.googleapis.com",
    "videointelligence.googleapis.com",
    "bigquery.googleapis.com",
    # "dlp.googleapis.com",
    # "workflows.googleapis.com",
    "eventarc.googleapis.com",
    "pubsub.googleapis.com",
  ]

  disable_services_on_destroy = false
}
