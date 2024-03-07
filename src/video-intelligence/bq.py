def save_bq(df, table_id, project_id):
    import pandas
    import pandas_gbq

    print(f"save_bq  {table_id} {project_id}")

    # check if dataframe is empty
    if df is None or df.empty:
        print("empty dataframe")
        return
    
    df = df.astype(str)
    print(df.to_json(orient='records'))

    pandas_gbq.to_gbq(df, table_id, project_id=project_id , if_exists='append', verbose= True)

