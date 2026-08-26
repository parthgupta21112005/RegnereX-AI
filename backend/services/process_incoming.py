import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import joblib
import requests


def create_embedding(text_list):
    r = requests.post("http://localhost:11434/api/embed", json={
        "model": "bge-m3",
        "input": text_list
    })
    embedding = r.json()["embeddings"]
    return embedding

def inference(prompt):
    r = requests.post("http://localhost:11434/api/generate", json={
        # "model": "deepseek-r1",
        "model": "qwen3:8b",
        "prompt": prompt,
        "stream": False
    })

    response = r.json()
    return response

def response(income_query):
    question_embedding = create_embedding([income_query])[0]
    df = joblib.load("embeddings.joblib")


    similarity = cosine_similarity(np.vstack(df["embedding"]), [question_embedding]).flatten()
    top_results = 3
    max_indx = similarity.argsort()[::-1][0:top_results]

    new_df = df.loc[max_indx]

    prompt = f'''I am teaching web development and artificial intelligence course. Here are video subtitle chunks containing video title, video number, start time in seconds, end time in seconds, the text at that time:

    {new_df[["title", "number", "start", "end", "text"]].to_json(orient="records")}
    ---------------------------------
    "{income_query}"
    User asked this question related to the video chunks, you have to answer in a human way (dont mention the above format, its just for you) where and how much content is taught in which video (in which video and at what timestamp) and guide the user to go to that particular video. If user asks unrelated question, tell him that you can only answer questions related to the course
    '''

    response = inference(prompt)["response"]

    with open("response.txt", "w") as f:
        f.write(response)
        
    return response