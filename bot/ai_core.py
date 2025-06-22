#ai_core.py
from langdetect import detect, LangDetectException
from bot.model_roberta import analyze_en
from bot.model_rubert import analyze_ru
import re

def contains_cyrillic(text: str) -> bool:
	return bool(re.search('[а-яА-ЯёЁ]', text))

def analyze_sentiment(text: str) -> str:
	if not text.strip():
		return "Пустое сообщение"

	if contains_cyrillic(text):
		return analyze_ru(text)

	try:
		lang = detect(text)

		if lang == 'en' or not contains_cyrillic(text):
			return analyze_en(text)
		else:
			return analyze_ru(text)

	except LangDetectException:
	# Если не удалось определить - пробуем английскую модель
		return analyze_en(text)