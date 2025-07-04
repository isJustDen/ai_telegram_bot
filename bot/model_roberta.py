#model_roberta.py
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from scipy.special import softmax
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
async def analyze_en(text: str) -> str:
	text = preprocess(text)
	tokens = tokenizer(text, return_tensors="pt")
	result = model(**tokens)
	scores = result.logits.detach().numpy()[0]
	probs = softmax(scores)

	labels = ['негативная', 'нейтральная', 'позитивная']
	top = np.argmax(probs)
	return f'(EN) Тональность: {labels[top]}'