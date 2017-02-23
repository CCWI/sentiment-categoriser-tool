from flask import Flask, render_template
import mysql.connector as mariadb

from config import db_host, db_user, db_password, db_name
from config import db_port

app = Flask(__name__)


@app.route('/')
def main():
    return render_template('index.html')




if __name__ == '__main__':
    app.run()


def get_db_connection():
    return mariadb.connect(host=db_host, port=db_port, user=db_user, password=db_password,
                           database=db_name)