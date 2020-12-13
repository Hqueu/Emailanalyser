import email
import numpy as np
import pandas as pd
import re
from datetime import datetime
import time, sys
from IPython.display import clear_output
from sklearn.feature_extraction.text import CountVectorizer
import nltk

class Prioritizer:
    def __init__(self, file_name):
        self.priority_test = pd.read_csv(file_name).dropna()
        print('**************************************')
        print('Test emails data with {} mails'.format(self.priority_test.shape[0]))
        print('**************************************')
        self.thread_weights = pd.read_pickle("Scripts/Prioritizer/thread_weights.pkl")
        self.thread_term_weights =pd.read_pickle("Scripts/Prioritizer/thread_term_weights.pkl")
        self.from_weight =pd.read_pickle("Scripts/Prioritizer/from_weight.pkl")
        self.senders_weight =pd.read_pickle("Scripts/Prioritizer/senders_weight.pkl")

    def rank_message(self, msg):
        # First, using the from weights
        from_wt = self.from_weight[self.from_weight['from_username']==msg['from_username']]
        if len(from_wt)>0:
            msg_from_wt = from_wt.weight
        else:
            msg_from_wt = 1
        
        # Second, using senders weights from threads
        senders_wt = self.senders_weight[self.senders_weight['From']==msg['from_username']]
        if len(senders_wt)>0:
            msg_thread_from_wt = senders_wt.weight
        else:
            msg_thread_from_wt = 1
            
        # Then, from thread activity
        is_thread = len(msg.Subject.split('re: ')) > 1
        if is_thread:
            subject = msg.Subject.split('re: ')[1]
            msg_thread_activity_wt = self.get_weights(subject, self.thread_weights, term=False)
        else:
            msg_thread_activity_wt = 1
            
        # Then, weights based on terms in threads
        try:
            sub_vec = vec.fit_transform([msg['Subject']])
            msg_thread_terms = vec.get_feature_names()
            msg_thread_term_wt = self.get_weights(msg_thread_terms, self.thread_term_weights)
        except:
            # Some subjects from the test set result in empty vocabulary
            msg_thread_term_wt = 1
        
        # Then, weights based on terms in message
        try:
            msg_vec = vec.fit_transform([msg['content']])
            msg_terms = vec.get_feature_names()
            msg_terms_wt = (msg_terms, self.msg_term_weights)
        except:
            # Some subjects from the test set result in empty vocabulary
            msg_terms_wt = 1
        
        # Calculating Rank
        rank = float(msg_from_wt) * float(msg_thread_from_wt) * float(msg_thread_activity_wt) * float(msg_thread_term_wt) * float(msg_terms_wt)
        
        return [msg.name, msg['from_username'], msg['content'],msg['Subject'], rank]


    def get_weights(self, search_term, weight_df, term=True):
        search_term = str(search_term)
        if (len(search_term)>0):
            if term:
                term_match = False
                for search_item in search_term:
                    match = weight_df.term.str.contains(search_item, regex=False)
                    term_match = term_match | match
            else:
                term_match = weight_df.thread.str.contains(search_term, regex=False)
            
            match_weights = weight_df.weight[term_match]
            if len(match_weights)<1:
                return 1
            else:
                return match_weights.mean()
        else:
            return 1


    def update_progress(self, progress):
        bar_length = 20
        if isinstance(progress, int):
            progress = float(progress)
        if not isinstance(progress, float):
            progress = 0
        if progress < 0:
            progress = 0
        if progress >= 1:
            progress = 1
        block = int(round(bar_length * progress))
        clear_output(wait = True)
        # text = "Progress: [{0}] {1:.1f}%".format( "#" * block + "-" * (bar_length - block), progress * 100)
        # print(text)


    def prioritize(self):
        test_rank_dict = {'date': [], 'from': [], 'content':[], 'subject': [], 'rank': []}
        for i in range(self.priority_test.shape[0]):
            result = self.rank_message(self.priority_test.iloc[i, :])
            test_rank_dict['date'].append(result[0])
            test_rank_dict['from'].append(result[1])
            test_rank_dict['content'].append(result[2])
            test_rank_dict['subject'].append(result[3])
            test_rank_dict['rank'].append(result[4])
            self.update_progress(self.priority_test.shape[0])
        test_rank_df = pd.DataFrame.from_dict(test_rank_dict)
        priority_threshold = test_rank_df['rank'].median()
        test_rank_df['priority'] = test_rank_df['rank']>priority_threshold
        prioritized_mails = test_rank_df[test_rank_df['priority']==True]
        prioritized_mails = prioritized_mails.drop('priority',axis=1)
        prioritized_mails = prioritized_mails.sort_values(by = 'rank', ascending = False)
        prioritized_mails.to_csv('priority_result.csv')
        return prioritized_mails