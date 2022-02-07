import os
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename

import redis
import socket
import sys

#default path
UPLOAD_FOLDER = '/path/to/the/uploads'

# maybe later add more extensions
ALLOWED_EXTENSIONS = {'txt', 'docx'}

app = Flask(__name__)

# Load configurations from environment or config file
app.config.from_pyfile('config_file.cfg')

if ("UPLOAD_FOLDER" in os.environ and os.environ['UPLOAD_FOLDER']):
    upload_folder = os.environ['UPLOAD_FOLDER']
else:
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    upload_folder = app.config['UPLOAD_FOLDER']

if ("TITLE" in os.environ and os.environ['TITLE']):
    title = os.environ['TITLE']
else:
    title = app.config['TITLE']

# Redis configurations
redis_server = os.environ['REDIS']

# Redis Connection
try:
    if "REDIS_PWD" in os.environ:
        r = redis.StrictRedis(host=redis_server,
                        port=6379,
                        password=os.environ['REDIS_PWD'])
    else:
        r = redis.Redis(redis_server)
    r.ping()
except redis.ConnectionError:
    exit('Failed to connect to Redis, terminating.')



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/files", methods=['GET'])
def profile():
    if request.method == 'GET':
        kvs = []
        for key in r.keys():
            kvs.append([key, r.get(key)])
        return render_template("files.html", title=title, your_list=kvs)

@app.route('/', methods=['GET', 'POST'])
def upload_file():

    if request.method == 'GET':

        # Return index with values
        return render_template("index.html", title=title, filename="none", word_count=0)

    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            word_count = 0
            for line in file.stream:
                word_count += len(line.split())
            r.set(filename, word_count)
            return render_template("index.html", title=title, filename=filename, word_count=word_count)
    return

if __name__ == "__main__":
    app.run()
