import sqlite3
import logging
import sys
import os

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

conn_counter=0

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    global conn_counter
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    conn_counter +=1
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      logging.info('Article does not exist!')
      return render_template('404.html'), 404
    else:
      logging.info("%s Article retrieved, post" %post["title"])
      return render_template('post.html', post=post)

# Define the Healthcheck endpoint 
# The endpoint should return HTTP 200 status code and a JSON response containing
# the result: OK - healthy message
@app.route('/healthz')
def healthz():
    connection = get_db_connection()
    response = app.response_class(
            response=json.dumps({"result":"OK - healthy"}),
            status=200,
            mimetype='application/json'
    )
    connection.close()
    return response

# Define the Metrics endpoint
# The endpoint should return HTTP 200 status code
# JSON response with the following metrics:
# - Total aount of posts in the database
# - Total amount of connections to the database. E.g., accessing an article will query the database, hence will count as connection.
@app.route('/metrics')
def metrics():
    connection=get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()

    response = app.response_class(
            response=json.dumps({"status":"success","code":0,"data":{"db_connection_count":conn_counter,"post_count":len(posts)}}),
            status=200,
            mimetype='application/json'
    )
    connection.close()
    return response

# Define the About Us page
@app.route('/about')
def about():
    logging.info('About us page')
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            logging.info("%s Article retrieved, post" %title)
            return redirect(url_for('index'))

    return render_template('create.html')

# start the application on port 3111
if __name__ == "__main__":
   ## stream logs to app.log file
   
   loglevel = os.getenv("LOGLEVEL", "DEBUG").upper()
   loglevel = (
     getattr(logging, loglevel)
     if loglevel in ["CRITICAL", "DEBUG", "ERROR", "INFO", "WARNING",]
     else logging.DEBUG
   )
   
   # Record the Techtrends application logs to STDOUT and STDERR
   stdout_handler = logging.StreamHandler(sys.stdout) # STDOUT handler
   stderr_handler = logging.StreamHandler(sys.stderr) # STDERR handler
   handlers = [stderr_handler, stdout_handler]

   # format output
   logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=loglevel, handlers=handlers)

   app.run(host='0.0.0.0', port='3111')
