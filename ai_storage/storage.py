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

    top_answers = 3

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
        #     out = self.search__private()
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

    def search__private(self, question: str, thr: float):
        assert 0 <= thr <= 2
        out = self.__search_get_dists(question)
        if out is not None:
            keys, dists = out

            if dists[0] < thr:
                return keys, dists, 1
            else:
                return keys, dists, self.top_answers
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
        if dist < 0:
            dist = 0
        return dist

    def benchmark_eval(self, benchmark_json_filepath, thr: float, beta: float):
        benchmark_key_garbage = 'Мусор'
        TP = 0
        FP = 0
        FN = 0
        TN = 0
        stat_3 = []
        benchmark_json = json_load(benchmark_json_filepath)
        gt_keys = set(benchmark_json.keys())
        assert gt_keys - set(self.questions) == set((benchmark_key_garbage,))
        for gt_key in gt_keys:
            for q in benchmark_json[gt_key]:
                out = self.search__private(q, thr)
                if out is not None:
                    pred_keys, scores, N = out
                    if N == 1:
                        if gt_key == pred_keys[0]:
                            TP += 1
                        else:
                            FP += 1
                    elif N > 1:
                        assert N == 3
                        if gt_key == benchmark_key_garbage:
                            TN += 1
                        else:
                            FN += 1
                    else:
                        raise Exception
                    assert len(pred_keys) == self.top_answers
                    if gt_key in pred_keys:
                        stat_3.append(1)
                    else:
                        stat_3.append(0)
                else:
                    if gt_key == benchmark_key_garbage:
                        TN += 1
                        stat_3.append(1)
                    else:
                        FN += 1
                        stat_3.append(0)
        full_recall = (TP+FP)/(TP+FN+TN+FP)
        precision = TP/(TP+FP)
        recall = TP/(TP+FN)
        F = (1+beta**2)*precision*recall/(beta**2*precision+recall)
        top1_acc = (TP+TN)/(TP+FN+TN+FP)

        stat_3 = np.array(stat_3)
        ones = np.where(stat_3 == 1)[0]
        ones = ones.shape[0]
        top3_acc = ones / len(stat_3)

        print('thr', thr)
        print('full_recall', round(full_recall, 2))
        print('precision', round(precision, 2))
        print('recall', round(recall, 2))
        print('F', round(F, 2))
        print('top1_acc', round(top1_acc, 2))
        print('top3_acc', round(top3_acc, 2))

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
    print(s.search('Где подготовиться к парам'))
    print(s.search('хуй'))
    print(s.search('Предоставляют ли на время приема документов общежитие?'))
    print(s.search('Что такое задавальник?'))
    print()
    print(s.search('военная'))
    print()
    print(s.search('Какие документы необходимо иметь при себе?'))
    print()
    print(s.search('Как проходят занятия по физической культуре?'))
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
    s.benchmark_eval('../data/benchmark.json', 0.4, 1.0)


def setup_data_vectors():
    s = Storage('../data/data.json', '../data/tayga_upos_skipgram_300_2_2019/model.bin', setup_data_vectors=True)
# ut_1()