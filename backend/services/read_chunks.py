import requests
import os
import json
import pandas as pd
import joblib


def create_embedding(text_list):
    r = requests.post("http://localhost:11434/api/embed", json={
        "model": "bge-m3",
        "input": text_list
    })
    embedding = r.json()["embeddings"]
    return embedding

def ai_assistant(file_text):
    jsons = os.listdir(file_text)
    chunk_id = 0
    my_dict = []
    for json_list in jsons:
        with open(f"jsons/{json_list}") as f:
            data = json.load(f)
        embeddings = create_embedding([c["text"] for c in data["chunk"]])
        
        for i, chunk in enumerate(data["chunk"]):
            chunk['chunk_id'] = chunk_id
            chunk["embedding"] = embeddings[i]
            chunk_id += 1
            my_dict.append(chunk)

    df = pd.DataFrame.from_records(my_dict)

    joblib.dump(df, "embeddings.joblib")
