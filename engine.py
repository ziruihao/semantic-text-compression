import os
import re
import json
import time
import numpy as np
import gensim.downloader
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize, TreebankWordDetokenizer

class Engine:
    '''

    '''
    def __init__(self, shorthand_file_path, lang = 'en'):
        with open(shorthand_file_path, 'r', encoding = 'utf-8') as file:
            self.shorthand_dict = json.load(file)
        if lang == 'en':
            self.model = gensim.downloader.load('glove-wiki-gigaword-50')
        elif lang == 'es':
            self.model = gensim.downloader.load('glove-twitter-25')
        self.context_vector = None
        

    def compress(self, text, opts):
        '''
        Compress a file using the given options.
        '''
        
        start_time = time.time()
        self.context_vector = np.zeros(self.model.vector_size)
        compressed_text = ''
        total_words, compressed_words = 0, 0
        sentences = sent_tokenize(text)
        for sentence in sentences:
            if opts['verbose']: print('sentence:', sentence)
            compressed_sentence = []
            words = word_tokenize(sentence)
            for _, word in enumerate(words):
                if total_words == 0:
                    pass
                total_words += 1
                compressed_word = word
                self.add_to_context(word)
                shorthand = self.shorten_word(word)
                if opts['verbose']: print('\t', word, '->', shorthand)
                if shorthand in self.shorthand_dict:
                    candidates = list(filter(lambda w: w in self.model.key_to_index, self.shorthand_dict[shorthand]))
                    if len(candidates) > 0:
                        if opts['verbose']: print('\t\tcandidates:', ', '.join(candidates[:10]))
                        if opts['lossless']:
                            top_candidate = self.determine_top_candidate(candidates)
                            if opts['verbose']: print('\t\ttop_candidate:', top_candidate)
                            if top_candidate == word:
                                compressed_word = shorthand
                                compressed_words += 1
                        else:
                            compressed_word = shorthand
                            compressed_words += 1
                compressed_sentence.append(compressed_word)
            compressed_text += ' ' + TreebankWordDetokenizer().detokenize(compressed_sentence)
        return compressed_text, compressed_words, total_words, (time.time() - start_time)
        
    def decompress(self, input_file_path, output_file_path, opts):
        '''
        Decompress a file using the given options.
        '''
        self.context_vector = np.zeros(self.model.vector_size)
        with open(input_file_path, 'r', encoding = 'utf-8') as file:
            text = file.read()
        decompressed_text = ''
        sentences = sent_tokenize(text)
        for sentence in sentences:
            if opts['verbose']: print('sentence:', sentence)
            decompressed_sentence = []
            words = word_tokenize(sentence)
            for _, word in enumerate(words):
                decompressed_word = word
                if word in self.shorthand_dict:
                    candidates = list(filter(lambda w: w in self.model.key_to_index, self.shorthand_dict[word]))
                    if len(candidates) > 0:
                        if opts['verbose']: print('\t\tcandidates:', ', '.join(candidates[:10]))
                        top_candidate = self.determine_top_candidate(candidates)
                        if opts['verbose']: print('\t\ttop_candidate:', top_candidate)
                        decompressed_word = top_candidate
                decompressed_sentence.append(decompressed_word)
                self.add_to_context(decompressed_word)
                if opts['verbose']: print('\t', word, '->', decompressed_word)
            decompressed_text += ' ' + TreebankWordDetokenizer().detokenize(decompressed_sentence)
        with open(output_file_path, 'w', encoding = 'utf-8') as file:
            file.write(decompressed_text)
    
    def add_to_context(self, word):
        if self.context_vector is None:
            self.context_vector = np.zeros(self.model.vector_size)
        try:
            self.context_vector = np.add(self.context_vector, self.model.get_vector(word))
        except KeyError:
            pass
    
    def determine_top_candidate(self, candidates):
        if self.context_vector is None:
            return ''
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