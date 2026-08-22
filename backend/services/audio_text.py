import whisper
import os
import json

model = whisper.load_model("large-v2")

def audio_text(audio_file):
    l = os.listdir(audio_file)
    num = 1
    for file in l:
        result = model.transcribe(f"{audio_file}/{file}", language="hi", task="translate")
        os.makedirs("jsons", exist_ok=True)
        with open(f"jsons/{file.split(".")[0]}.json", "w") as f:
            chunk = []
            for seg in result["segments"]:
                chunk.append({"number": num, "title": file.split(".")[0][2:],"start": seg["start"], "end": seg["end"], "text": seg["text"]})
                num+=1

            text = {
                "chunk": chunk,
                "text": result["text"],

            }
            json.dump(text, f)
    return "Convert Text successfully"