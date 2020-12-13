

from flask import Flask, render_template, session
import pandas as pd
from Scripts.EmailData.mail_analyzer import Mail_analyzer
import pandas as pd
from Scripts.IntentClassifier.intent import Intent
from Scripts.Prioritizer.prioritizer import Prioritizer


app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html.j2")

@app.route("/prioritize")
def prioritize():
    richards_file = 'richard_mails.csv'
    prioritizer = Prioritizer(richards_file)
    prioritized_mails = prioritizer.prioritize()
    print('Finished prioritization')
    return render_template("df.html.j2", length=len(prioritized_mails), dataframe=prioritized_mails.to_html())

@app.route("/extract_mail", methods=['GET', 'POST'])
def extract():
    update_df = pd.read_csv('hque_mail.csv')   
    return render_template("df.html.j2", length=len(update_df), dataframe=update_df.to_html())

@app.route("/update_mail", methods=['GET', 'POST'])
def update_mail():
    mail_analyzer.get_search(intent, intent_df)
    update_df = pd.read_csv('hque_mail.csv')
    return render_template("df.html.j2", length=len(update_df), dataframe=update_df.to_html())

if __name__ == "__main__":
    username = 'hqueue.haq@gmail.com'
    password = '********'
    mail_analyzer = Mail_analyzer(username, password)
    intent = Intent()
    df = mail_analyzer.get_extract()
    length = len(df)
    print('extraction finished')
    intent_df = mail_analyzer.get_intent(df, intent)
    intent_df.to_csv('hque_mail.csv')
    print('intent prediction finished')
    app.run(debug=True, port=5957)
