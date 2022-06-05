import re
import json
import numpy as np
import gensim.downloader
from sklearn.metrics.pairwise import cosine_similarity
from nltk.tokenize import word_tokenize, sent_tokenize, TreebankWordDetokenizer

class Engine:
    def __init__(self, shorthand_file_path):
        with open(shorthand_file_path) as f:
            self.shorthand_dict = json.load(f)
        self.model = gensim.downloader.load('glove-wiki-gigaword-50').wv

    def compress(self, input_file_path, output_file_path, opts):
        with open(input_file_path, 'r') as f:
            text = f.read()
        compressed_text = ''
        sentences = sent_tokenize(text)
        for idx, sentence in enumerate(sentences):
            compressed_sentence = []
            words = word_tokenize(sentence)
            for word in words:
                compressed_word = word
                shorthand = self.shorten_word(word)
                if shorthand in self.shorthand_dict:
                    candidates = self.shorthand_dict[word]
                    if opts.lossless:
                        top_candidate = self.determine_top_candidate(candidates, sentence[:idx])
                        if top_candidate == word:
                            compressed_word = shorthand
                compressed_sentence.append(compressed_word)
            compressed_text += TreebankWordDetokenizer.detokenize(compressed_sentence)
        with open(output_file_path, 'w') as f:
            f.write(compressed_text)

    def determine_top_candidate(self, candidates, context_sentence):
        context_vector = np.zeros(self.model.vector_size)
        for word in context_sentence:
            context_vector = np.add(context_vector, self.model.get_vector(word))
        candidates_ranked = sorted([(cosine_similarity([context_vector], [self.model.get_vector(candidate)])[0][0], candidate) for candidate in candidates], reversed = True)
        return candidates_ranked[0][1]

    @staticmethod
    def shorten_word(word):
        return re.sub('[aeiou]', '', word)

    @staticmethod
    def generate_shorthand_dict(english_words_file_path, shorthand_file_path):
        '''
        Generate a dictionary of shorthand abbreviations (vowel removal) for the English language.
        Saves abbreviations to a JSON file.
        '''
        with open(english_words_file_path, 'r') as f:
            english_words = f.read().splitlines()
        shorthand_dict = {}
        for word in english_words:
            shorthand = Engine.shorten_word(word)
            if shorthand not in shorthand_dict:
                shorthand_dict[shorthand] = []
            shorthand_dict[shorthand].append(word)
        with open(shorthand_file_path, 'w') as f:
            json.dump(shorthand_dict, f)