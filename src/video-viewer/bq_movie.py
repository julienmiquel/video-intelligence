import gcs as gcs
import config as config
import bq as bq

DATASET = "video_analytics_4293"
TABLE = "results"

def get_movies_list():
    query = "SELECT distinct video_blobname FROM video_analytics_4293.results"
    print(query)
    queryJob = bq.client.query(query, project=config.PROJECT_ID, location=config.BQ_REGION)
    result = queryJob.result()
    # for row in result:
    #     print(row)
    

    df = result.to_dataframe()
    return df


def get_movie_description(filter):
    query = f"SELECT index,time_start as start,time_stop as stop, description, uri, MODEL_MULTIMODAL as llm_model  FROM `{DATASET}.{TABLE}` where video_blobname = '{filter}' and description != 'ERROR'   order by  CAST(index AS INT64)  asc"
    print(query)
    print("PROJECT_ID = " + config.PROJECT_ID)
    queryJob = bq.client.query(query, project=config.PROJECT_ID, location=config.BQ_REGION)
    result = queryJob.result()

    df = result.to_dataframe()
    return df




from google.cloud import bigquery
import vertexai


# Initialize Vertex AI SDK
vertexai.init(project=config.PROJECT_ID, location=config.BQ_REGION)

def get_access_token():
    import google.auth
    import google.auth.transport.requests

    # Getting the auth token via SDK
    creds, project = google.auth.default(quota_project_id=config.PROJECT_ID)

    auth_req = google.auth.transport.requests.Request()
    creds.refresh(auth_req)
    ACCESS_TOKEN = creds.token
    print(f"project = {project}")

    return ACCESS_TOKEN, creds

# ACCESS_TOKEN, creds = get_access_token()


client = bigquery.Client(#credentials=creds, 
                         project=config.PROJECT_ID, location=config.BQ_REGION)

def get_movies_list2():
    
    print("get_movies_list()")
    # Perform a query.
    QUERY = (
        'SELECT name FROM `bigquery-public-data.usa_names.usa_1910_2013` '
        'WHERE state = "TX" '
        'LIMIT 100')
    query_job = client.query(QUERY)  # API request
    rows = query_job.result()  # Waits for query to finish

    # for row in rows:
    #     print(row.name)

    return rows.to_dataframe()