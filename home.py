from flask import Blueprint,render_template
from flask import request, jsonify
import pandas as pd
from io import StringIO
import tempfile
import os
from pathlib import Path

from backend.preprocessing import clean_text, srt_to_csv
from backend.inference import predict_batch_emotions


home = Blueprint('home',__name__)

@home.route("/", methods=["GET"])
def root():
    return render_template('index.html')
@home.route("/upload", methods=["POST"])
def upload_subtitle():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file part in the request."}), 400

        file = request.files['file']
        filename = file.filename
        if filename == "":
            return jsonify({"error": "No selected file."}), 400

        ext = Path(filename).suffix.lower()

        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            file.save(tmp.name)
            tmp_path = tmp.name

        if ext == ".srt":
            csv_path = tmp_path.replace(".srt", ".csv")
            srt_to_csv(tmp_path, csv_path)
            df = pd.read_csv(csv_path)
            os.remove(csv_path)
        elif ext == ".csv":
            content = file.read().decode("utf-8")
            df = pd.read_csv(StringIO(content))
        else:
            return jsonify({"error": "Only .srt and .csv files are supported."}), 400

        os.remove(tmp_path)

        df['cleaned_text'] = df['text'].apply(clean_text).fillna("").astype(str)
        df = df[df['cleaned_text'].str.strip() != ""]

        emotions = predict_batch_emotions(df['cleaned_text'].tolist())
        df['emotion'] = emotions

        emotion_counts = df['emotion'].value_counts().to_dict()

        chunk_size = 10
        chunks = [df['emotion'][i:i+chunk_size] for i in range(0, len(df), chunk_size)]
        timeline = []
        for i, chunk in enumerate(chunks):
            counts = chunk.value_counts().to_dict()
            counts['chunk'] = f'{i*chunk_size}-{min((i+1)*chunk_size, len(df))}'
            timeline.append(counts)

        return jsonify({
            "total_lines": len(df),
            "emotion_counts": emotion_counts,
            "preview": df[['cleaned_text', 'emotion']].head(5).to_dict(orient='records'),
            "timeline": timeline
        })

    except Exception as e:
        print("❌ BACKEND ERROR:", str(e))
        return jsonify({"error": "Backend error: " + str(e)}), 500
