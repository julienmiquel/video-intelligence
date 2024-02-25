def save_bq(df, table_id, project_id):
    import pandas
    import pandas_gbq

    print("save_bq")
    df = df.astype(str)

    pandas_gbq.to_gbq(df, table_id, project_id=project_id , if_exists='append', verbose= True)

