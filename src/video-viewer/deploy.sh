export GCP_PROJECT='media-414316'  # Change this
export GCP_REGION='europe-west4'             # If you change this, make sure region is supported by Model Garden. When in 


export AR_REPO='dev-repo'  # Change this
export SERVICE_NAME='video-viewer2' # This is the name of our Application and Cloud Run service. Change it if you'd like. 
gcloud artifacts repositories create "$AR_REPO" --location="$GCP_REGION" --repository-format=Docker
gcloud auth configure-docker "$GCP_REGION-docker.pkg.dev"
gcloud builds submit --project=$GCP_PROJECT --tag "$GCP_REGION-docker.pkg.dev/$GCP_PROJECT/$AR_REPO/$SERVICE_NAME"

gcloud run deploy "$SERVICE_NAME" \
    --port=8080 \
    --image="$GCP_REGION-docker.pkg.dev/$GCP_PROJECT/$AR_REPO/$SERVICE_NAME" \
    --allow-unauthenticated \
    --region=$GCP_REGION \
    --platform=managed  \
    --project=$GCP_PROJECT \
    --set-env-vars=PROJECT_ID=$GCP_PROJECT,REGION=$GCP_REGION
