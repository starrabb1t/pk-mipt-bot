import json
#import gensim
#import pymystem3

class storage():

    def __init__(self, json_path):
        self.data = {}

        self.json_path = "data/data.json"

        try:
            with open(self.json_path, 'r') as j:
                self.data = json.load(j)
        except Exception as ex:
            print()

    def search(self, question_str):
        answer_str = None
        #TODO: some magic here

        return answer_str
