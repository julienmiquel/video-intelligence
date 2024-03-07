


resource "google_storage_bucket" "gcf_source_vi" {
  name                        = "${var.suffix}-gcf-source" # Every bucket name must be globally unique
  location                    = var.region
  uniform_bucket_level_access = true
}

data "archive_file" "source_vi" {
  type        = "zip"
  output_path = "/tmp/function-source.zip"
  source_dir  = "../src/video-intelligence/"
}
resource "google_storage_bucket_object" "object" {
  name   = "vi-function-source.zip"
  bucket = google_storage_bucket.gcf_source_vi.name
  source = data.archive_file.source_vi.output_path # Add path to the zipped function source code
  
  depends_on = [
    module.project_services,
  ]
}  


resource "google_cloudfunctions2_function" "video_intelligence_function" {
  name        = "video_intelligence_processing_videos"
  location    = var.region
  description = "video intelligence cloud function V2"

  build_config {
    runtime     = "python310"
    entry_point = "process_event_video" # Set the entry point
    source {
      storage_source {
        bucket = google_storage_bucket.gcf_source_vi.name
        object = google_storage_bucket_object.object.name
      }
    }
  
  }
  

 service_config {
    available_cpu = "1"
    max_instance_count = 20
    max_instance_request_concurrency = 20

    available_memory   = "512M"
    timeout_seconds    = 500

    ingress_settings = "ALLOW_INTERNAL_ONLY"
    service_account_email = google_service_account.video_trigger.email

    environment_variables = {
        OUTPUT_BUCKET = google_storage_bucket.video_output_bucket.name
        INPUT_BUCKET = google_storage_bucket.video_input_bucket.name
        WORKING_BUCKET = google_storage_bucket.working_bucket.name
        PROJECT_ID = var.project_id
        REGION = var.region
        BQ_DATASET = google_bigquery_dataset.video_analytics.dataset_id
    }

  }

 event_trigger {
      event_type     = "google.cloud.storage.object.v1.finalized"
      trigger_region = var.region
      retry_policy   = "RETRY_POLICY_DO_NOT_RETRY"
      service_account_email = google_service_account.video_trigger.email

      event_filters {
        attribute = "bucket"
        value     = google_storage_bucket.video_input_bucket.name
        
    }

  }

  depends_on = [
    module.project_services,
  ]
}



resource "google_cloudfunctions2_function" "video_intelligence_function_2_json" {
  name        = "video_intelligence_processing_json_results"
  location    = var.region
  description = "video intelligence cloud function json processing"

  build_config {
    runtime     = "python310"
    entry_point = "process_event_json" # Set the entry point
    source {
      storage_source {
        bucket = google_storage_bucket.gcf_source_vi.name
        object = google_storage_bucket_object.object.name
      }
    }
  
  }
  

 service_config {
    available_cpu = "4"
    max_instance_count = 100
    max_instance_request_concurrency = 1

    available_memory   = "16Gi"
    timeout_seconds    = 500

    ingress_settings = "ALLOW_INTERNAL_ONLY"
    service_account_email = google_service_account.video_trigger.email

    environment_variables = {
        OUTPUT_BUCKET = google_storage_bucket.video_output_bucket.name
        INPUT_BUCKET = google_storage_bucket.video_input_bucket.name
        WORKING_BUCKET = google_storage_bucket.working_bucket.name
        PROJECT_ID = var.project_id
        REGION = var.region
        BQ_DATASET = google_bigquery_dataset.video_analytics.dataset_id

    }

  }

 event_trigger {
      event_type     = "google.cloud.storage.object.v1.finalized"
      trigger_region = var.region
      retry_policy   = "RETRY_POLICY_DO_NOT_RETRY"
      service_account_email = google_service_account.video_trigger.email

      event_filters {
        attribute = "bucket"
        value     = google_storage_bucket.working_bucket.name
        
    }

  }

  depends_on = [
    module.project_services,
  ]
}




resource "google_cloudfunctions2_function" "gemini_classification" {
  name        = "video_intelligence_processing_gemini_classification"
  location    = var.region
  description = "classify video using gemini"

  build_config {
    runtime     = "python310"
    entry_point = "process_event_classify_video" # Set the entry point
    source {
      storage_source {
        bucket = google_storage_bucket.gcf_source_vi.name
        object = google_storage_bucket_object.object.name
      }
    }
  
  }
  

 service_config {
    available_cpu = "4"
    max_instance_count = 10
    max_instance_request_concurrency = 10
    available_memory   = "2Gi"
    timeout_seconds    = 500

    ingress_settings = "ALLOW_INTERNAL_ONLY"
    service_account_email = google_service_account.video_trigger.email

    environment_variables = {
        OUTPUT_BUCKET = google_storage_bucket.video_output_bucket.name
        INPUT_BUCKET = google_storage_bucket.video_input_bucket.name
        WORKING_BUCKET = google_storage_bucket.working_bucket.name
        PROJECT_ID = var.project_id
        REGION = var.region
        BQ_DATASET = google_bigquery_dataset.video_analytics.dataset_id

    }

  }

 event_trigger {
      event_type     = "google.cloud.storage.object.v1.finalized"
      trigger_region = var.region
      retry_policy   = "RETRY_POLICY_DO_NOT_RETRY"
      service_account_email = google_service_account.video_trigger.email

      event_filters {
        attribute = "bucket"
        value     = google_storage_bucket.video_output_bucket.name
        
    }

  }

  depends_on = [
    module.project_services,
  ]
}

