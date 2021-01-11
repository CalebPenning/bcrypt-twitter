from flask import Flask, flash, redirect, render_template, session, jsonify, request
from flask_debugtoolbar import DebugToolbarExtension
from models import db, User, connect_db, Tweet
from forms import UserForm, TweetForm
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///social_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'ILOVEKITTYCATS420'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

connect_db(app)
db.create_all()

@app.route('/')
def placeholder():
    return render_template('index.html')

@app.route('/tweets', methods=['GET', 'POST'])
def show_tweets():
    if "user_id" not in session:
        flash("Please log in first!", "danger")
        return redirect('/login')
    form = TweetForm()
    tweets = Tweet.query.all()
    
    if form.validate_on_submit():
        text = form.text.data
        user_id = session['user_id']
        new_tweet = Tweet(text=text, user_id=user_id)
        db.session.add(new_tweet)
        db.session.commit()
        flash("Tweet Sent.", "success")
        return redirect('/tweets')

    return render_template('tweets.html', form=form, tweets=tweets)

@app.route('/tweets/<int:id>', methods=["POST"])
def delete_tweet(id):
    """Delete Tweet"""
    if 'user_id' not in session:
        flash("Please login first", "danger")
        return redirect('/login')
    
    tweet = Tweet.query.get_or_404(id)
    if tweet.user_id == session['user_id']:
        db.session.delete(tweet)
        db.session.commit()
        flash('Tweet deleted', "info")
        return redirect('/tweets')
    flash("You don't have permission for that action.", "danger")
    return redirect('/tweets')

@app.route('/signup', methods=['GET', 'POST'])
def sign_up_user():
    form = UserForm()
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        new_user = User.sign_up_user(username, password)
        
        db.session.add(new_user)
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append('Username is taken. Please choose another username.')
            return render_template('signup.html')
        
        session['user_id'] = new_user.id
        flash("Excellent! Successfully Created Your Account!", "success")
        return redirect('/tweets')
    
    return render_template('signup.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_user():
    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.username.data
        
        user = User.authenticate(username, password)
        
        if user:
            flash(f"Welcome back, {user.username}.", "info")
            session['user_id'] = user.id 
            return redirect('/tweets')
        else:
            form.username.errors = ['Invalid username/password.']
        
    return render_template('login.html', form=form)

@app.route('/logout')
def logout_user():
    session.pop('user_id')
    flash('Goodbye!', "primary")
    return redirect('/')