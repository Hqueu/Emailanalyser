import pickle
import re
import regex as regex
from stemming.porter2 import stem

class Intent:
    def __init__(self):
        with open('Scripts/IntentClassifier/tfid_vector.pkl', 'rb') as f:
            self.vectorizer = pickle.load(f)
        with open('Scripts/IntentClassifier/intent.pkl', 'rb') as f:
            self.intent_model = pickle.load(f)


    def cleanData(self, sentence):
        trainData = [" ".join([stem(word) for word in sentence.split(" ")])]
        trainData = [re.sub(r"(<?)http:\S+", "$LINK", i) for i in trainData]
        trainData = [re.sub(r"\$\d+", "$MONEY", i) for i in trainData]
        trainData = [re.sub(r'[\w\.-]+@[\w\.-]+', "$EMAILID", i) for i in trainData]
        trainData = [i.lower() for i in trainData]
        trainData = [regex.sub(r"[^\P{P}$]+", " ", i) for i in trainData]
        trainData = [re.sub(r"[^0-9A-Za-z/$' ]", " ", i) for i in trainData]
        regString = r'monday|tuesday|wednesday|thursday|friday|saturday|sunday'
        trainData = [re.sub(regString, "$days", i) for i in trainData]
        regString = r'january|jan|february|feb|march|mar|april|june|july|august|aug|september|sept|october|oct|november|nov|december|dec'
        trainData = [re.sub(regString, "$month", i) for i in trainData]
        regString = r'after|before|during'
        trainData = [re.sub(regString, "$time", i) for i in trainData]
        trainData = [re.sub(r'\b\d+\b', "$number", i) for i in trainData]
        trainData = [re.sub(r'\b(me|her|him|us|them|you)\b', "$me", i) for i in trainData]
        trainData = [i.strip() for i in trainData]
        return trainData

    def feedback_intent(self, sentence):
        testData = self.cleanData(sentence)
        x_test = self.vectorizer.transform(testData)
        pred = self.intent_model.predict(x_test)
        return pred


