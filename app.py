import hashlib
import sqlite3
import os
import uuid

from flask import (
    Flask, g, render_template, redirect, url_for, request, flash,
    session, current_app, send_from_directory
)

from werkzeug.utils import secure_filename
                

app = Flask(__name__)
app.config['SECRET_KEY'] = "create-your-own"
app.config['MEDIA_DIR'] = os.path.join(app.instance_path, 'media') 
app.config['MAX_CONTENT_LENGTH'] = 200 * 1000 * 1000


try:
    os.makedirs(app.instance_path)
    os.makedirs(app.config['MEDIA_DIR'])
except OSError as e:
    # If the folders already exist do nothing
    pass


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            'database.sqlite',
            #current_app.config['DATABASE'],
        )
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


@app.route('/')
def index():
    db = get_db()
    cur = db.execute("SELECT * FROM post;")
    posts = cur.fetchall()

    return render_template('index.html', posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Log in user"""

    # If we receive form data try to log the user in
    if request.method == 'POST':

        # Connect to the database
        db = get_db()

        # Retrieve the users password from database (and check if user exist)
        cur = db.execute("SELECT * FROM user WHERE username=?", (request.form['username'],))
        user = cur.fetchone()
        
        # Check if a user was found
        if user is None:
            flash('User not found.')
            return render_template('login.html')

        # TODO: Check if the passwords match
        #print(user['password'])
        hashed_login_password = hashlib.sha256(request.form['password'].encode()).hexdigest()
        if hashed_login_password != user['password']:
            flash('Invalid password')
        else:

            # If everything is okay, log in the user 
            # TODO: See the previoius TODOs
            session.clear()
            session['user_id'] = user['id']
            flash('You were logged in.')

            return redirect(url_for('index'))

    return render_template('login.html')

@app.route('/upload', methods=['POST', 'GET'])
def upload():

    if not session.get('user_id'):
        flash("Login required.")
        return(redirect(url_for('login')))

    if request.method == 'POST':

        file = None
        type = None
        if request.files['videofile'].filename != '':
            file = request.files['videofile']
            type = 'video'

        elif request.files['imagefile'].filename != '':
            file = request.files['imagefile']
            type = 'image'

        if not file:
            # If no file was posted redirect back with error
            flash("No media file selected for upload.")
            return redirect(url_for('upload'))

        if file.filename == '':
            # If filename is empty redirect back with an error
            flash("Invalid file.")
            return redirect(url_for('upload'))
        
        else:
            # Everthing is fine, make the post 

            # Save the upload to disk 
            ## TODO Generate unique filenames ##
            filename = str(uuid.uuid4())
            #filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['MEDIA_DIR'], filename))

            # Save the post in the database
            ## TODO Check for empty title  ## 
            title = request.form['title']
            if title == '':
                flash("Invalid Title")
                return redirect(url_for('upload'))

            db = get_db()
            db.execute("INSERT INTO post (title, media, type) VALUES (?,?,?);", 
                       (title, filename, type)
                      )
            db.commit()
    
            flash('Your post was created!')
            # Redirect to show the new post
            return(redirect(url_for('index')))

    # If no data was posted show the form
    return(render_template('upload.html'))


@app.route('/register', methods=['POST', 'GET'])
def register():
    """Registers a new user"""

    # If we receive form data try to register the new user
    if request.method == 'POST':

        # TODO Check if username is available
        #flash("Username '{}' already taken".format(request.form['username']), 'error')

        # TODO Check if the two passwords match
        # flash("Passwords do not match, try again.", 'error')

        # TODO Maybe check if the password is a good one?
        # flash("Password is too weak, try again.", 'error')

        # If all is well create the user
        # TODO See previous TODOs
        hashed_password = hashlib.sha256(request.form['password1'].encode()).hexdigest()
        db=get_db()
        db.execute("INSERT INTO user (username, password) VALUES (?,?)",
                   (request.form['username'], hashed_password))
        db.commit()
        flash("User '{}' registered, you can now log in.".format(request.form['username']), 'info')
        
        return redirect(url_for('login'))


    # If we receive no data just show the registration form
    else:
        return render_template('register.html')


@app.route('/logout')
def logout():
    """Logs user out"""
    session.clear()
    flash('You were logged out.')
    return redirect(url_for('index'))


@app.before_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        db = get_db()
        cur = db.execute('SELECT * FROM user WHERE id = ?', (user_id,))
        g.user = cur.fetchone()


@app.route('/images/<path:filename>')
def media_file(filename):
    """ Serve user uploaded images during development. """
    return send_from_directory(current_app.config['MEDIA_DIR'], filename)


if __name__ == "__main__":
    app.run("0.0.0.0", debug=True)