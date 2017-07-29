from __future__ import division

import praw, pymysql.cursors, codecs, string, re, urllib, sys

sys.path.append('../')

import dogmeat_config as conf

from string import punctuation

saveToDatabase = 1
sub_param = 'all'
num_results = 1

def getAverage(values):
    sum = 0
    for val in values:
        sum = sum + val
    return sum/len(values)

r = praw.Reddit(client_id=conf.CLIENT_ID,
    client_secret=conf.CLIENT_SECRET,
    password=conf.PASSWORD,
    user_agent=conf.USER_AGENT,
    username=conf.USERNAME)

connection = pymysql.connect(host='localhost',
    user=conf.DB_USER,
    password=conf.DB_PASSWORD,
    db=conf.DB,
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor)

#Referenced this great beginner tutorial, will move to an original dictionary soon
#http://nealcaren.web.unc.edu/an-introduction-to-text-analysis-with-python-part-1/
files=['negative.txt','positive.txt']
path='http://www.unc.edu/~ncaren/haphazard/'

for file in files:
    urllib.urlretrieve(path+file,file)

pos_sent = open('positive.txt').read()
positive_words = pos_sent.split('\n')

neg_sent = open('negative.txt').read()
negative_words = neg_sent.split('\n')

positive_counts = []
negative_counts = []

comment_lengths = []

def collect(save_data, sub, num_res):

    subreddit = r.get_subreddit(sub)

    print "Analyzing top " + str(num_res) + " posts from r/" + sub

    try:
        with connection.cursor() as cursor:

            for submission in subreddit.get_top_from_week(limit=num_res):

                submission.replace_more_comments(limit=None, threshold=0)
                comments = praw.helpers.flatten_tree(submission.comments)

                for comment in comments:

                    positive_count = 0
                    negative_count = 0

                    lc = comment.body

                    for p in list(punctuation):
                      lc = lc.replace(p,'')

                    words = lc.split(' ')
                    word_count = len(words)

                    for word in words:
                        if word in positive_words:
                            positive_count = positive_count + 1
                        elif word in negative_words:
                            negative_count = negative_count + 1

                    positive_counts.append(positive_count/word_count)
                    negative_counts.append(negative_count/word_count)

                    comment_lengths.append(word_count)

                    cb = str(comment.body)
                    wc = str(word_count)
                    pc = str(positive_count)
                    nc = str(negative_count)
                    si = str(submission.id)

                    sql = "INSERT IGNORE INTO submission_comment(text,words,positives,negatives,submission_id) VALUES (%s,%s,%s,%s,%s);"
                    cursor.execute(sql, (cb,wc,pc,nc,si))
                    connection.commit()

                sub_url = None
                sub_text = None

                if submission.selftext != '':
                    sub_text = submission.selftext
                else:
                    sub_url = submission.url

                sql = "INSERT IGNORE INTO submission(title,submission_id,author,url,text) VALUES (%s,%s,%s,%s,%s);"
                cursor.execute(sql,(submission.title,submission.id,submission.author.name,sub_url,sub_text))

                connection.commit()

    finally:
        connection.close()
