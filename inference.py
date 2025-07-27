from transformers import BertTokenizer, BertForSequenceClassification
import torch

# Load your pretrained BERT model & tokenizer here (make sure to download or put in 'models/' folder)
MODEL_PATH = "C:/projects/project imp/sentiment analysis on movie reviews/backend/models/bert-sentiment"

tokenizer = BertTokenizer.from_pretrained(MODEL_PATH)
model = BertForSequenceClassification.from_pretrained(MODEL_PATH)
model.eval()

EMOTION_LABELS = list(model.config.id2label.values())

def predict_emotion(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=128)
    with torch.no_grad():
        outputs = model(**inputs)
    logits = outputs.logits
    predicted_class_id = torch.argmax(logits).item()
    return EMOTION_LABELS[predicted_class_id]

def predict_batch_emotions(texts):
    results = []
    for text in texts:
        results.append(predict_emotion(text))
    return results
