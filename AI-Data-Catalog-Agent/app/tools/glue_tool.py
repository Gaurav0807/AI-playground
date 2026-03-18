import boto3
import os

glue_client = boto3.client("glue", region_name=os.getenv("AWS_REGION"))

def get_glue_table(database_name:str):

    response = glue_client.get_tables(DatabaseName=database_name)
    tables = []
    for table in response["TableList"]:
        table_name = table["Name"]

        columns = []
        if "StorageDescriptor" in table:
            columns = [
                col["Name"]
                for col in table["StorageDescriptor"].get("Columns",[])
            ]
        
        tables.append({
            "table_name": table_name,
            "columns": columns
        })
    print("Tables Info :- ",tables)

    
       

    return tables