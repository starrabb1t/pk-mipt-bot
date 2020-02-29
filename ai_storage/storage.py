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
        self.data_json = json_load(json_path)
        self.data = self.data_json[self.KEY_DATA]
        assert isinstance(self.data, dict)
        self.questions = list(self.data.keys())
        assert all((isinstance(x, str) for x in self.questions))

        self.model = gensim.models.KeyedVectors.load_word2vec_format(model_path, binary=True, encoding='utf-8')
        self.mystem = Mystem()

    def search(self, question: str):
        words = self.preprocess(question)
        vectors = np.array([self.model.get_vector(x) for x in words])

        answer = None
        return answer

    def preprocess(self, question):
        # TODO fix fused words
        analyzis = self.mystem.analyze(question)
        words = []
        for x in analyzis:
            if self.is_word(x['text']):
                w = x['analysis'][0]['lex']
                p = x['analysis'][0]['gr']
                p = p.split(',')[0]
                p = p.split('=')[0]
                p = self.posmap[p]
                w += '_'
                w += p
                words.append(w)

        return words

    def is_word(self, string):
        return string != ' ' and string != '\n'

    posmap = {
        'S': 'NOUN',
        'V': 'VERB',
        'A': 'ADJ',
        'ADV': 'ADV'
    }


def ut_0():
    """
    unit test 0
    """
    s = Storage('../data/data2.json', '../data/tayga_upos_skipgram_300_2_2019/model.bin')
    s.search('Красивая мама красиво мыла раму')
    # s.search('Красивая мамакрасиво мылараму')
    print()


ut_0()
