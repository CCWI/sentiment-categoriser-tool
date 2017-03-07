import os
import random
import re
from flask import Flask, render_template, redirect, url_for, request
import mysql.connector as mariadb

from config import db_host, db_user, db_password, db_name
from config import db_port

app = Flask(__name__)


@app.route('/')
def main():
    mariadb_connection = get_db_connection()
    cursor = mariadb_connection.cursor(buffered=True)
    cursor.execute('SELECT id FROM comment_sentiment.comments_07_03 WHERE sentiment IS NULL')
    rows = cursor.fetchall()
    mariadb_connection.close()
    if cursor.rowcount == 0:
        return render_template('alldone.html')
    else:
        commentid = random.choice(rows)[0]
        return redirect(url_for('getcomment', commentid=commentid))


@app.route('/comments/<commentid>')
def getcomment(commentid):
    # open database connection
    mariadb_connection = get_db_connection()

    # get post info from the database
    cursor = mariadb_connection.cursor(buffered=True)
    cursor.execute(
        'SELECT comment_text FROM comment_sentiment.comments_07_03 WHERE id = "' + str(commentid) + '"')
    if cursor.rowcount == 0 or cursor.rowcount > 1:
        raise ValueError

    text = cursor.fetchall()[0][0]
    # do some padding to the punctuation elements
    text = re.sub('([.,!?():])', r' \1 ', text)
    text = re.sub('\s{2,}', ' ', text)
    comment = {'text': text, 'id': commentid}
    mariadb_connection.close()

    return render_template('index.html', comment=comment)


@app.route('/save', methods=["POST"])
def save():
    mariadb_connection = get_db_connection()
    cursor = mariadb_connection.cursor(buffered=True)
    if request.form['sentiment'] == 'spam':
        stmt = 'UPDATE comment_sentiment.comments_07_03 SET spam = 1 WHERE id = %s'
        cursor.execute(stmt, request.form['id'])
    else:
        stmt = 'UPDATE comment_sentiment.comments_07_03 SET sentiment = %s WHERE id = %s'
        print stmt
        cursor.execute(stmt, request.form['sentiment'], request.form['id'])

    stmt2 = "UPDATE comment_sentiment.comments_07_03 SET comment_text = %s WHERE id = %s"
    cursor.execute(stmt2, request.form['text'], request.form['id'])
    mariadb_connection.commit()
    mariadb_connection.close()
    return main()


def get_db_connection():
    return mariadb.connect(host=db_host, port=db_port, user=db_user, password=db_password,
                           database=db_name)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)  # NOSONAR
