import sys
sys.path.append('../')
from ai_storage.json_utils import *

import gensim
from pymystem3 import Mystem
import numpy as np
import os
import pickle


class Storage:

    VERSION = '0.1'

    __KEY_DATA = 'data'
    __KEY_INFO = 'info'

    def __init__(self, data_json_path: str, model_bin_path: str):
        json_dirname = os.path.dirname(data_json_path)
        self.__questions_vectors_filepath = os.path.join(json_dirname, self.__questions_vectors_filename)

        self.data = json_load(data_json_path)[self.__KEY_DATA]
        assert isinstance(self.data, dict)
        self.questions = list(self.data.keys())
        assert all((isinstance(x, str) for x in self.questions))

        self.__model = gensim.models.KeyedVectors.load_word2vec_format(model_bin_path, binary=True, encoding='utf-8')
        self.__mystem = Mystem()

        self.__load_questions_vectors()

    def search(self, question: str):
        vectors = self.get_vectors(question)

        vector = np.sum(vectors, axis=0)

        dists = {}
        for k, v in self.questions_vectors.items():
            dist = self.cosine_dist(vector, v)
            dists[k] = dist

        answer = None
        answer = min(dists, key=dists.get)

        return answer

    def preprocess(self, question):
        # TODO fix fused words
        analyzis = self.__mystem.analyze(question)
        words = []
        for x in analyzis:
            try:
                w = x[self.__mystem_key_analysis][0][self.__mystem_key_analysis_key_lex]
                p = x[self.__mystem_key_analysis][0][self.__mystem_key_analysis_key_gr]
                p = p.split(',')[0]
                p = p.split('=')[0]
                if p in self.__posmap.keys():
                    p = self.__posmap[p]
                    w += '_'
                    w += p
                    words.append(w)
            except Exception:
                pass

        return words

    __posmap = {
        'S': 'NOUN',
        'V': 'VERB',
        'A': 'ADJ',
        'ADV': 'ADV'
    }

    __mystem_key_text = 'text'
    __mystem_key_analysis = 'analysis'
    __mystem_key_analysis_key_lex = 'lex'
    __mystem_key_analysis_key_gr = 'gr'

    __questions_vectors_filename = 'questions_vectors.p'

    def get_vectors(self, sentence: str):
        words = self.preprocess(sentence)
        vectors = []
        for x in words:
            try:
                vector = self.__model.get_vector(x)
                vectors.append(vector)
            except KeyError:
                pass
        vectors = np.array(vectors)
        return vectors

    def __load_questions_vectors(self):
        calculate_vectors = True
        if os.path.isfile(self.__questions_vectors_filepath):
            self.questions_vectors = pickle.load(open(self.__questions_vectors_filepath, "rb"))
            # TODO assert
            calculate_vectors = False

        if calculate_vectors:
            self.questions_vectors = {}
            for question in self.questions:
                vectors = self.get_vectors(question)
                self.questions_vectors[question] = vectors
            pickle.dump(self.questions_vectors, open(self.__questions_vectors_filepath, "wb"))

        for k, v in self.questions_vectors.items():
            self.questions_vectors[k] = np.sum(v, axis=0)

    @staticmethod
    def cosine_dist(a, b):
        dist = 1 - np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
        return dist


def ut_0():
    """
    unit test 0
    """
    s = Storage('../data/data.json', '../data/tayga_upos_skipgram_300_2_2019/model.bin')
    # s.search('Красивая мама красиво мыла раму')
    # s.search('Красивая мамакрасиво мылараму')
    s.search('Какие документы необходимо иметь при себе?')
    print()
