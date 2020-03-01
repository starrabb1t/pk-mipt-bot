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

    def __init__(self, data_json_path: str, model_bin_path: str, setup_data_vectors=False):
        json_dirname = os.path.dirname(data_json_path)
        self.__questions_vectors_filepath = os.path.join(json_dirname, self.__questions_vectors_filename)

        self.data = json_load(data_json_path)[self.__KEY_DATA]
        assert isinstance(self.data, dict)
        self.questions = list(self.data.keys())
        assert all((isinstance(x, str) for x in self.questions))

        self.__model = gensim.models.KeyedVectors.load_word2vec_format(model_bin_path, binary=True, encoding='utf-8')
        self.__mystem = Mystem()

        if setup_data_vectors:
            self.setup_data_vectors()
            print('WARNING: dont use this instance of Storage class, recreate new!')
            return

        self.__load_questions_vectors()

    def search(self, question: str, debug=True):
        # try:
            out = self.__search_get_dists(question)
            if out is not None:
                keys, dists = out
                answers = []
                for k in keys:
                    answers.append(self.data[k]['answer'])
                if debug:
                    print('search answer:', answers)

                assert isinstance(answers, list)
                assert len(answers) <= self.top_answers
                assert all([isinstance(x, str) for x in answers])
                return answers
            else:
                if debug:
                    print('search answer:', None)
                return None
        # except Exception:
        #     return None

    def search_debug(self, question: str):
        out = self.__search_get_dists(question)
        if out is not None:
            keys, dists = out
            return keys, dists
        return None

    def __search_get_dists(self, question: str):
        vectors = self.get_vectors(question)

        vector = self.__define_sentence_type(vectors)  # TODO now None or shape(300,)
        if vector is None:
            return vector
        keys = []
        dists = []
        for k, v in self.questions_vectors.items():
            v = self.__define_sentence_type(v)
            if v is not None:
                dist = self.cosine_dist(vector, v)
                keys.append(k)
                assert 0 <= dist <= 2
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
        if len(words) == 0:
            return None  # None is garbage
        vectors = []
        for x in words:
            try:
                vector = self.__model.get_vector(x)
                vectors.append(vector)
            except KeyError:
                pass
        vectors = np.array(vectors)
        if len(vectors) == 0:
            # TODO exact match search should be completed from here
            # (vectors are empty and words are not here)
            return words
        return vectors

    def __load_questions_vectors(self):
        assert os.path.isfile(self.__questions_vectors_filepath)
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
            self.questions_vectors[k] = self.__define_sentence_type(v)
                #np.sum(v, axis=0)

    def setup_data_vectors(self):
        assert not os.path.isfile(self.__questions_vectors_filepath)

        print('Calculating data vectors...')
        questions_vectors = {}
        for question in self.questions:
            vectors = self.get_vectors(question)
            questions_vectors[question] = vectors
        pickle.dump(questions_vectors, open(self.__questions_vectors_filepath, "wb"))
        print('Data vectors calculated and saved')

    @staticmethod
    def cosine_dist(a, b):
        denom = np.linalg.norm(a) * np.linalg.norm(b)
        assert denom != 0
        dist = 1 - np.dot(a, b) / denom
        return dist

    def benchmark_eval(self, benchmark_json_filepath, thr):
        benchmark_key_garbage = 'Мусор'
        stat_1 = []
        stat_4 = []
        benchmark_json = json_load(benchmark_json_filepath)
        gt_keys = set(benchmark_json.keys())
        for gt_key in gt_keys:
            # gt_vector = self.questions_vectors[gt_key]
            for q in benchmark_json[gt_key]:
                out = self.search_debug(q)
                if out is not None:
                    pred_keys, scores = out
                    if gt_key in pred_keys:
                        stat_4.append(1)
                        if gt_key == pred_keys[0]:
                            stat_1.append(1)
                        else:
                            stat_1.append(0)
                    else:
                        stat_4.append(0)
                        stat_1.append(0)
                else:
                    if gt_key == benchmark_key_garbage:
                        stat_1.append(1)
                        stat_4.append(1)
                    else:
                        stat_1.append(0)
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

    def __define_sentence_type(self, sentence_vectors):
        """
        sentence_vector could be:
        np.ndarray.shape == (300,)
        None - garbage
        list of words - for exact match search
        """
        if sentence_vectors is None:  # TODO the same check for vector variable
            # garbage
            pass
        elif isinstance(sentence_vectors, np.ndarray):
            assert sentence_vectors.shape[-1] == 300
            if len(sentence_vectors.shape) == 2:
                sentence_vectors = np.sum(sentence_vectors, axis=0)
            else:
                assert len(sentence_vectors.shape) == 1
        elif isinstance(sentence_vectors, list):
            # exact math search here
            assert all([isinstance(x, str) for x in sentence_vectors])
            sentence_vectors = None  # TODO
        else:
            raise Exception
        return sentence_vectors


def ut_0():
    """
    unit test 0
    """
    s = Storage('../data/data.json', '../data/tayga_upos_skipgram_300_2_2019/model.bin')
    # s.search('Красивая мама красиво мыла раму')
    # s.search('Красивая мамакрасиво мылараму')
    # print(s.search('подготовиться к работе'))
    print(s.search('Что такое задавальник?'))
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


def setup_data_vectors():
    s = Storage('../data/data.json', '../data/tayga_upos_skipgram_300_2_2019/model.bin', setup_data_vectors=True)
