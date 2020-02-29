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

    top_answers = 4

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

    def search(self, question: str, debug=True):
        keys, dists = self.__search_get_dists(question)
        answers = []
        for k in keys:
            answers.append(self.data[k]['answer'])
        if debug:
            print(answers)
        return answers

    def search_debug(self, question: str):
        keys, dists = self.__search_get_dists(question)
        return keys, dists

    def __search_get_dists(self, question: str):
        vectors = self.get_vectors(question)

        vector = np.sum(vectors, axis=0)

        keys = []
        dists = []
        for k, v in self.questions_vectors.items():
            dist = self.cosine_dist(vector, v)
            keys.append(k)
            dists.append(dist)
        keys = np.array(keys)
        dists = np.array(dists)

        top_ids = np.argsort(dists)[:self.top_answers]

        keys = keys[top_ids]
        dists = dists[top_ids]

        return keys, dists

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
        'ADV': 'ADV',
        # '': 'PROPN'
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
            print('Data vectors loaded')

        if calculate_vectors:
            print('Calculating data vectors...')
            self.questions_vectors = {}
            for question in self.questions:
                vectors = self.get_vectors(question)
                self.questions_vectors[question] = vectors
            pickle.dump(self.questions_vectors, open(self.__questions_vectors_filepath, "wb"))
            print('Data vectors calculated and saved')

        for k, v in self.questions_vectors.items():
            self.questions_vectors[k] = np.sum(v, axis=0)

    @staticmethod
    def cosine_dist(a, b):
        dist = 1 - np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
        return dist

    def benchmark_eval(self, benchmark_json_filepath):
        stat_1 = []
        stat_4 = []
        benchmark_json = json_load(benchmark_json_filepath)
        gt_keys = set(benchmark_json.keys())
        for gt_key in gt_keys:
            # gt_vector = self.questions_vectors[gt_key]
            for q in benchmark_json[gt_key]:
                pred_keys, scores = self.search_debug(q)
                if gt_key in pred_keys:
                    stat_4.append(1)
                    if gt_key == pred_keys[0]:
                        stat_1.append(1)
                    else:
                        stat_1.append(0)
                else:
                    stat_4.append(0)
        stat_1 = np.array(stat_1)
        ones = np.where(stat_1==1)[0]
        ones = ones.shape[0]
        acc_1 = ones/len(stat_1)
        print('benchmark acc_1: ', acc_1)

        stat_4 = np.array(stat_4)
        ones = np.where(stat_4 == 1)[0]
        ones = ones.shape[0]
        acc_4 = ones / len(stat_4)
        print('benchmark acc_4: ', acc_4)


def ut_0():
    """
    unit test 0
    """
    s = Storage('../data/data.json', '../data/tayga_upos_skipgram_300_2_2019/model.bin')
    # s.search('Красивая мама красиво мыла раму')
    # s.search('Красивая мамакрасиво мылараму')
    # print(s.search('подготовиться к работе'))
    print(s.search('военная'))
    print()
    print(s.search('Какие документы необходимо иметь при себе?'))
    print()
    print(s.search('собес'))
    print()
    print(s.search('собеседование'))
    print()
    print(s.search('военная кафедра'))
    print()


def ut_1():
    """
    benchmark
    """
    s = Storage('../data/data.json', '../data/tayga_upos_skipgram_300_2_2019/model.bin')
    s.benchmark_eval('../data/benchmark.json')
