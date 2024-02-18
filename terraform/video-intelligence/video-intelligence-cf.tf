


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
    entry_point = "process_event" # Set the entry point
    source {
      storage_source {
        bucket = google_storage_bucket.gcf_source_vi.name
        object = google_storage_bucket_object.object.name
      }
    }
  
  }
  

 service_config {
    max_instance_count = 3
    available_memory   = "512M"
    timeout_seconds    = 600

    ingress_settings = "ALLOW_INTERNAL_ONLY"
    service_account_email = google_service_account.video_trigger.email

    environment_variables = {
        OUTPUT_BUCKET = google_storage_bucket.video_output_bucket.name
        INPUT_BUCKET = google_storage_bucket.video_input_bucket.name
        WORKING_BUCKET = google_storage_bucket.working_bucket.name
        PROJECT_ID = var.project_id
        REGION = var.region
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
    entry_point = "process_event" # Set the entry point
    source {
      storage_source {
        bucket = google_storage_bucket.gcf_source_vi.name
        object = google_storage_bucket_object.object.name
      }
    }
  
  }
  

 service_config {
    max_instance_count = 3
    available_memory   = "512M"
    timeout_seconds    = 600

    ingress_settings = "ALLOW_INTERNAL_ONLY"
    service_account_email = google_service_account.video_trigger.email

    environment_variables = {
        OUTPUT_BUCKET = google_storage_bucket.video_output_bucket.name
        INPUT_BUCKET = google_storage_bucket.video_input_bucket.name
        WORKING_BUCKET = google_storage_bucket.working_bucket.name
        PROJECT_ID = var.project_id
        REGION = var.region
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
