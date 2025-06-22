#model_rubert.py
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import numpy as np

MODEL = "cointegrated/rubert-tiny-sentiment-balanced"
tokenizer = AutoTokenizer.from_pretrained(MODEL)
model = AutoModelForSequenceClassification.from_pretrained(MODEL)

def analyze_ru(text: str) -> str:
	inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
	with torch.no_grad():
		outputs = model(**inputs)
		scores = torch.nn.functional.softmax(outputs.logits, dim= 1)[0]

	labels = ["негативная", "нейтральная", "позитивная"]
	top = torch.argmax(scores).item()
	return f'(RU) Тональность:{labels[top]}'