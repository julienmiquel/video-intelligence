# # Copyright 2021 Google LLC
# #
# # Licensed under the Apache License, Version 2.0 (the "License");
# # you may not use this file except in compliance with the License.
# # You may obtain a copy of the License at
# #
# #      https://www.apache.org/licenses/LICENSE-2.0
# #
# # Unless required by applicable law or agreed to in writing, software
# # distributed under the License is distributed on an "AS IS" BASIS,
# # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# # See the License for the specific language governing permissions and
# # limitations under the License.

resource "google_bigquery_dataset" "video_analytics" {
  dataset_id    = "video_analytics${local.app_suffix_underscore}"
  friendly_name = "video analytics Dataset"
  description   = "This dataset contains data related to the video application"
  location      = var.region

  depends_on = [
    module.project_services,
  ]
}

# resource "google_bigquery_connection" "connection" {
#    connection_id = "gcp-cloud-ai-connection"
#    location      = var.region
#    friendly_name = "ai-connection"
#    description   = "access to cloud ai services"

#    cloud_resource {}

# }



# resource "google_bigquery_table" "findings" {
#   dataset_id          = google_bigquery_dataset.video_redaction.dataset_id
#   table_id            = "findings"
#   deletion_protection = false
#   schema              = templatefile("${path.module}/templates/bq-table-findings.json", {})

#   depends_on = [
#     module.project_services,
#   ]
# }




# CREATE OR REPLACE EXTERNAL TABLE `1_raw.retail_images_files`
# WITH CONNECTION `ml-demo-384110.us.conn_cloud_ai`
# OPTIONS (
#     object_metadata="DIRECTORY",
#     uris = ['gs://ml-demo-us-central1/dataset/retail/*.jpg',
#             'gs://ml-demo-us-central1/dataset/retail/*.jpeg'],
#     max_staleness=INTERVAL 24 HOUR
#    , metadata_cache_mode="MANUAL"    
#     ); 




# resource "google_bigquery_routine" "create_external_table_json_files" {
#   dataset_id = google_bigquery_dataset.video_analytics.dataset_id
#   routine_id     = "create_external_table_json_files"
#   routine_type = "PROCEDURE"
#   language = "SQL"
#   definition_body = " CREATE OR REPLACE EXTERNAL TABLE `" + google_bigquery_dataset.video_analytics.dataset_id + " customer-demo-01.video_analytics_2f60.files` WITH CONNECTION `customer-demo-01.europe-west1.gcp-cloud-ai-connection`  OPTIONS (    object_metadata='DIRECTORY',    uris = ['gs://video-output-bucket-2f60/*'],    max_staleness=INTERVAL 24 HOUR   , metadata_cache_mode='MANUAL'        ); "
# }

# resource "google_bigquery_table" "json_annotes_files" {
#   dataset_id          = google_bigquery_dataset.video_analytics.dataset_id
#   table_id            = "json_annotes_files"
#   deletion_protection = false
#   schema              = templatefile("${path.module}/templates/bq-table-json-annotes-files.json", {})

#   depends_on = [
#     module.project_services,
#   ]

# #   object_metadata     = "DIRECTORY"
# #   uris                = ["gs://video-output-bucket-2f60/*"]
# #   max_staleness        = "24h"
# #   metadata_cache_mode = "MANUAL"
# }


# resource "google_bigquery_job" "job" {
#   job_id     = "job_query" 
#   project    = var.project_id
#   location   = var.region

#   query {
#   query = " CREATE OR REPLACE EXTERNAL TABLE `customer-demo-01.video_analytics_2f60.files` WITH CONNECTION `customer-demo-01.europe-west1.gcp-cloud-ai-connection`  OPTIONS (    object_metadata='DIRECTORY',    uris = ['gs://video-output-bucket-2f60/*'],    max_staleness=INTERVAL 24 HOUR   , metadata_cache_mode='MANUAL'        ); "

    
#   }
# }