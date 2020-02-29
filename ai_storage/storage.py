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

    KEY_DATA = 'data'
    KEY_INFO = 'info'

    def __init__(self, json_path: str, model_path: str):
        json_dirname = os.path.dirname(json_path)
        self.questions_vectors_filepath = os.path.join(json_dirname, self.questions_vectors_filename)

        self.data = json_load(json_path)[self.KEY_DATA]
        assert isinstance(self.data, dict)
        self.questions = list(self.data.keys())
        assert all((isinstance(x, str) for x in self.questions))

        self.model = gensim.models.KeyedVectors.load_word2vec_format(model_path, binary=True, encoding='utf-8')
        self.mystem = Mystem()

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
        analyzis = self.mystem.analyze(question)
        words = []
        for x in analyzis:
            try:
                w = x[self.mystem_key_analysis][0][self.mystem_key_analysis_key_lex]
                p = x[self.mystem_key_analysis][0][self.mystem_key_analysis_key_gr]
                p = p.split(',')[0]
                p = p.split('=')[0]
                if p in self.posmap.keys():
                    p = self.posmap[p]
                    w += '_'
                    w += p
                    words.append(w)
            except Exception:
                pass

        return words

    posmap = {
        'S': 'NOUN',
        'V': 'VERB',
        'A': 'ADJ',
        'ADV': 'ADV'
    }

    mystem_key_text = 'text'
    mystem_key_analysis = 'analysis'
    mystem_key_analysis_key_lex = 'lex'
    mystem_key_analysis_key_gr = 'gr'

    questions_vectors_filename = 'questions_vectors.p'

    def get_vectors(self, sentence: str):
        words = self.preprocess(sentence)
        vectors = []
        for x in words:
            try:
                vector = self.model.get_vector(x)
                vectors.append(vector)
            except KeyError:
                pass
        vectors = np.array(vectors)
        return vectors

    def __load_questions_vectors(self):
        calculate_vectors = True
        if os.path.isfile(self.questions_vectors_filepath):
            # self.questions_vectors = np.load(self.questions_vectors_filepath, allow_pickle=True)
            self.questions_vectors = pickle.load(open(self.questions_vectors_filepath, "rb"))
            # TODO assert
            calculate_vectors = False

        if calculate_vectors:
            self.questions_vectors = {}
            for question in self.questions:
                vectors = self.get_vectors(question)
                self.questions_vectors[question] = vectors
            # np.save(self.questions_vectors_filepath, self.questions_vectors)
            pickle.dump(self.questions_vectors, open(self.questions_vectors_filepath, "wb"))

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


ut_0()
