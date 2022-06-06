import nltk
from engine import Engine

nltk.download('punkt')
Engine.generate_shorthand_dict('data/english_words.txt', 'data/shorthand_dict.json')