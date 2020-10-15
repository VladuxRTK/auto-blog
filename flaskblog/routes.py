import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from flaskblog import app, db, bcrypt

from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm
from flaskblog.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
from sqlalchemy.sql import text
from sqlalchemy.exc import ArgumentError


"""class CustomException(Exception,ArgumentError):
    def __init__(self):
        render_template("no_results.html")"""


@app.route("/")
@app.route("/home")
def home():
    categories=[]
    postsCategory=Post.query.all()
    page =request.args.get('page',1     ,type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page,per_page=5)
   
    for post in postsCategory:
        if post.category not in categories:
            categories.append(post.category)
    return render_template('home.html', posts=posts,categories=categories)


@app.route("/about")
def about():
    categories=[]
  
    posts = Post.query.all()
    for post in posts:
        if post.category not in categories:
            categories.append(post.category)
    return render_template('about.html', title='About',categories=categories)


@app.route("/register", methods=['GET', 'POST'])
def register():

    categories=[]
    postsCategory=Post.query.all()
   
    posts = Post.query.all()
   
    for post in postsCategory:
        if post.category not in categories:
            categories.append(post.category)
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form,categories=categories)


@app.route("/login", methods=['GET', 'POST'])
def login():
    categories=[]
    postsCategory=Post.query.all()
   
    posts = Post.query.all()
   
    for post in postsCategory:
        if post.category not in categories:
            categories.append(post.category)
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form,categories=categories)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    categories=[]
    postsCategory=Post.query.all()
   
    posts = Post.query.all()
   
    for post in postsCategory:
        if post.category not in categories:
            categories.append(post.category)
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form,categories=categories)


@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    categories=[]
    postsCategory=Post.query.all()
   
    posts = Post.query.all()
   
    for post in postsCategory:
        if post.category not in categories:
            categories.append(post.category)
    form = PostForm()

   
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user,category=form.select.data)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Post',
                           form=form, legend='New Post',categories=categories)


@app.route("/post/<int:post_id>")
def post(post_id):
    categories=[]
    postsCategory=Post.query.all()
   
    posts = Post.query.all()
   
    for post in postsCategory:
        if post.category not in categories:
            categories.append(post.category)
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post,categories=categories)


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    categories=[]
    postsCategory=Post.query.all()
   
    posts = Post.query.all()
   
    for post in postsCategory:
        if post.category not in categories:
            categories.append(post.category)
    post = Post.query.get_or_404(post_id)
    if current_user.username == "Admin":
        form = PostForm()
        if form.validate_on_submit():
            post.title = form.title.data
            post.content = form.content.data
            post.category = form.select.data
            db.session.commit()
            flash('Your post has been updated!', 'success')
       
            return redirect(url_for('post', post_id=post.id,categories=categories))
        elif request.method == 'GET':
            form.title.data = post.title
            form.content.data = post.content
            form.select.data = post.category
    
        return render_template('create_post.html', title='Update Post',
                           form=form, legend='Update Post',categories=categories)
    elif current_user==post.author:
        form = PostForm()
        if form.validate_on_submit():
            post.title = form.title.data
            post.content = form.content.data
            post.category = form.select.data
            db.session.commit()
            flash('Your post has been updated!', 'success')
       
            return redirect(url_for('post', post_id=post.id,categories=categories))
        elif request.method == 'GET':
            form.title.data = post.title
            form.content.data = post.content
            form.select.data = post.category
    
        return render_template('create_post.html', title='Update Post',
                           form=form, legend='Update Post')
    else:
        abort(403)



@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    categories=[]
    postsCategory=Post.query.all()
   
    posts = Post.query.all()
   
    for post in postsCategory:
        if post.category not in categories:
            categories.append(post.category)
    post = Post.query.get_or_404(post_id)
    if current_user.username == 'Admin':
        db.session.delete(post)
        db.session.commit()
        flash('Your post has been deleted!', 'success')
        return redirect(url_for('home'))
    elif current_user == post.author:
        db.session.delete(post)
        db.session.commit()
        flash('Your post has been deleted!', 'success')
        return redirect(url_for('home'))
    else:
        abort(403)




@app.route("/user/<string:username>")
def user_posts(username):
    categories=[]
    postsCategory=Post.query.all()
   
    posts = Post.query.all()
   
    for post in postsCategory:
        if post.category not in categories:
            categories.append(post.category)
    page =request.args.get('page',1,type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(page=page,per_page=5)
    return render_template('user_posts.html', posts=posts,user = user,categories=categories)



"""@app.route("/search",methods = ["GET","POST"])
def search():
    posts = Post.query.whoosh_search(text(request.args.get("query"))).all()
    if posts!="null":
        return render_template("test.html",posts=posts)
    return redirect(url_for('home'))"""

@app.route("/post/search")
@app.route("/search",methods = ["GET","POST"])
def search():
    categories=[]
    postsCategory=Post.query.all()
   
    posts = Post.query.all()
   
    for post in postsCategory:
        if post.category not in categories:
            categories.append(post.category)
    try:
        posts = Post.query.whoosh_search(text(request.args.get("query"))).all()
        return render_template("test.html",posts=posts,categories=categories)
    except ArgumentError:
        return render_template("no_results.html",categories=categories)

@app.route("/post/auto_news")
def auto_news():
    page =request.args.get('page',1,type=int)
    posts = Post.query.filter_by(category="Auto News").order_by(Post.date_posted.desc()).paginate(page=page,per_page=5)
    return render_template("auto_news.html",posts=posts)

@app.route("/post/reviews")
def reviews():
    page =request.args.get('page',1,type=int)
    posts = Post.query.filter_by(category="Review").order_by(Post.date_posted.desc()).paginate(page=page,per_page=5)
    return render_template("reviews.html",posts=posts)

@app.route("/post/tutorials")
def tutorials():
    page =request.args.get('page',1,type=int)
    posts = Post.query.filter_by(category="Tutorials").order_by(Post.date_posted.desc()).paginate(page=page,per_page=5)
    return render_template("tutorials.html",posts=posts)

@app.route("/latest_posts")
def latest_posts():
    posts = Post.query.order_by(Post.date_posted.desc()).limit(3)
    return render_template('latest_posts.html', posts=posts)

@app.route("/post/<string:category>")
def dropdown(category):
    categories=[]
    postsCategory=Post.query.all()
   
    posts = Post.query.all()
   
    for post in postsCategory:
        if post.category not in categories:
            categories.append(post.category)
    page =request.args.get('page',1,type=int)
    posts = Post.query.filter_by(category=category).order_by(Post.date_posted.desc()).paginate(page=page,per_page=5)
    return render_template("category_results.html",posts=posts,categories=categories)

