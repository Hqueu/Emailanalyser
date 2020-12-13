import email
import imaplib
from email import policy
import pandas as pd
import time
from email.parser import BytesParser

class Mail_analyzer:
    def __init__(self, username, password):
        self.username = 'hqueue.haq@gmail.com'
        self.password = 'Ai@hqueue'
        self.mail = self.mail_login(self.username, self.password)
        print('login successfully')

    def mail_login(self, username, password):
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login(username, password)
        mail.select('inbox')
        return mail

    def get_extract(self):
        result, data = self.mail.uid('search', None, 'ALL')
        inbox_itemlist = data[0].split()
        df = pd.DataFrame(columns=['Date','from_username', 'Subject', 'content'])
        for num in inbox_itemlist:
            result2, email_data = self.mail.uid('fetch', num, '(RFC822)')
            raw_email = email_data[0][1].decode('utf-8')
            email_message = email.message_from_string(raw_email, policy = email.policy.default)
            subject = email_message['Subject']
            date = email_message['Date']
            from_user = email_message['From']
            if email_message.is_multipart():
                for part in email_message.walk():
                    if part.get_content_type() == 'text/plain':
                        content = part.get_payload(None, True).decode("utf-8")
            df = df.append({'Date':date, 'from_username':from_user, 'Subject':subject, 'content':content}, ignore_index=True)
        return df

    def get_intent(self, df, intent):
        df['FeedbackRequired'] = df['content'].map(lambda s: intent.feedback_intent(s)[0])
        return df

    def get_search(self, intent, df):
        timeout = time.time() + 30*1 
        while True:
            print('Searching... {} seconds'.format(int(timeout - time.time())))
            if time.time() > timeout:
                break
            self.mail.select('inbox')
            status, response = self.mail.search(None,'UnSeen')
            unread_msg_nums = response[0].split()
            if len(unread_msg_nums) > 0:
                print('new message is recieved')
                for e_id in unread_msg_nums:
                    _, response = self.mail.uid('fetch', e_id, '(RFC822)')
                    self.mail.uid("STORE", e_id, '+FLAGS', 'Seen')
                    raw_email = response[0][1].decode('utf-8')
                    email_message = email.message_from_string(raw_email, policy = email.policy.default)
                    subject = email_message['Subject']
                    date = email_message['Date']
                    from_user = email_message['From']
                    if email_message.is_multipart():
                        for part in email_message.walk():
                            if part.get_content_type() == 'text/plain':
                                content = part.get_payload(None, True).decode("utf-8")
                    intent_flag = intent.feedback_intent(content)[0]
                    # print(pd.DataFrame({'Date':date, 'from_username':from_user, 'Subject':subject, 'content':content, 'FeedbackRequired':intent_flag}))
                    df = df.append({'Date':date, 'from_username':from_user, 'Subject':subject, 'content':content, 'FeedbackRequired':intent_flag}, ignore_index=True)
                    df.to_csv('hque_mail.csv')

