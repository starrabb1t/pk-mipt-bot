import sys
sys.path.append('../')
from ai_storage.json_utils import *

import gensim
from pymystem3 import Mystem
import numpy as np


class Storage:

    KEY_DATA = 'data'
    KEY_INFO = 'info'

    def __init__(self, json_path: str, model_path: str):
        self.data = json_load(json_path)[self.KEY_DATA]
        assert isinstance(self.data, dict)
        self.questions = list(self.data.keys())
        assert all((isinstance(x, str) for x in self.questions))

        self.model = gensim.models.KeyedVectors.load_word2vec_format(model_path, binary=True, encoding='utf-8')
        self.mystem = Mystem()

        self.__load_questions_vectors()

    def search(self, question: str):
        vectors = self.get_vectors(question)

        answer = None
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

    # def __mystem_is_word(self, mystem_item: dict):
    #     is_word = self.mystem_key_analysis in mystem_item.keys()
    #     if is_word:
    #         is_word = {self.mystem_key_analysis_key_lex, self.mystem_key_analysis_key_gr} - set(mystem_item[self.mystem_key_analysis][0].keys()) == set()
    #     return is_word

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
        if calculate_vectors:
            self.questions_vectors = []
            for question in self.questions:
                vectors = self.get_vectors(question)
                self.questions_vectors.append(vectors)


def ut_0():
    """
    unit test 0
    """
    s = Storage('../data/data.json', '../data/tayga_upos_skipgram_300_2_2019/model.bin')
    s.search('Красивая мама красиво мыла раму')
    # s.search('Красивая мамакрасиво мылараму')
    print()


ut_0()
