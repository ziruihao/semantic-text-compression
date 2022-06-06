import os
import re
import json
import numpy as np
import gensim.downloader
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize, TreebankWordDetokenizer

class Engine:
    '''

    '''
    def __init__(self, shorthand_file_path):
        with open(shorthand_file_path, 'r', encoding = 'utf-8') as file:
            self.shorthand_dict = json.load(file)
        self.model = gensim.downloader.load('glove-wiki-gigaword-50')
        self.context_vector = np.zeros(self.model.vector_size)

    def compress(self, input_file_path, output_file_path, opts):
        '''
        Compress a file using the given options.
        '''
        original_file_size, compressed_file_size = 0, 0
        with open(input_file_path, 'r', encoding = 'utf-8') as file:
            original_file_size = os.path.getsize(input_file_path)
            text = file.read()
        compressed_text = ''
        total_words, compressed_words = 0, 0
        sentences = sent_tokenize(text)
        for sentence in sentences:
            if opts['verbose']: print('sentence:', sentence)
            compressed_sentence = []
            words = word_tokenize(sentence)
            for _, word in enumerate(words):
                total_words += 1
                compressed_word = word
                shorthand = self.shorten_word(word)
                if opts['verbose']: print('\t', word, '->', shorthand)
                if shorthand in self.shorthand_dict:
                    candidates = list(filter(lambda w: w in self.model.key_to_index, self.shorthand_dict[shorthand]))
                    if len(candidates) > 0:
                        if opts['verbose']: print('\t\tcandidates:', ', '.join(candidates[:10]))
                        if opts['lossless']:
                            top_candidate = self.determine_top_candidate(candidates, words)
                            if opts['verbose']: print('\t\ttop_candidate:', top_candidate)
                            if top_candidate == word:
                                compressed_word = shorthand
                                compressed_words += 1
                        else:
                            compressed_word = shorthand
                            compressed_words += 1
                compressed_sentence.append(compressed_word)
            compressed_text += ' ' + TreebankWordDetokenizer().detokenize(compressed_sentence)
        with open(output_file_path, 'w', encoding = 'utf-8') as file:
            file.write(compressed_text)
        compressed_file_size = os.path.getsize(output_file_path)
        return compressed_words, total_words, compressed_file_size, original_file_size
        

    def determine_top_candidate(self, candidates, context_sentence):
        if len(context_sentence) == 0:
            return ''
        for word in context_sentence:
            try:
                self.context_vector = np.add(self.context_vector, self.model.get_vector(word))
            except KeyError:
                pass
        candidates_ranked = sorted([
            (cosine_similarity([self.context_vector], [self.model.get_vector(candidate)])[0][0], candidate) for candidate in candidates
            ], reverse = True)
        return candidates_ranked[0][1]

    @staticmethod
    def shorten_word(word):
        return re.sub('[aeiou]', '', word.lower())

    @staticmethod
    def generate_shorthand_dict(english_words_file_path, shorthand_file_path):
        '''
        Generate a dictionary of shorthand abbreviations (vowel removal) for the English language.
        Saves abbreviations to a JSON file.
        '''
        with open(english_words_file_path, 'r', encoding = 'utf-8') as file:
            english_words = file.read().splitlines()
        shorthand_dict = {}
        for word in english_words:
            shorthand = Engine.shorten_word(word)
            if shorthand not in shorthand_dict:
                shorthand_dict[shorthand] = []
            shorthand_dict[shorthand].append(word)
        with open(shorthand_file_path, 'w', encoding = 'utf-8') as file:
            json.dump(shorthand_dict, file)