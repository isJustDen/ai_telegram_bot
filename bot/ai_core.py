import os

from transformers import AutoModelForSequenceClassification, AutoTokenizer
from scipy.special import softmax
from huggingface_hub import login
import numpy as np
import emoji
import re



# Загрузка модели и токенизатора
MODEL = "cardiffnlp/twitter-roberta-base-sentiment"
tokenizer = AutoTokenizer.from_pretrained(MODEL)
model = AutoModelForSequenceClassification.from_pretrained(MODEL)

# Очистка текста от лишнего
def preprocess(text):
	text = emoji.demojize(text)
	text = re.sub(r"http\S+", "", text)
	return text

# Основная функция анализа эмоций
def analyze_sentiment(text: str) -> str:
	text = preprocess(text)
	tokens = tokenizer(text, return_tensors="pt")
	result = model(**tokens)
	scores = result.logits.detach().numpy()[0]
	probs = softmax(scores)

	labels = ['негативная', 'нейтральная', 'позитивная']
	top = np.argmax(probs)
	return f'Тональность: {labels[top]}'