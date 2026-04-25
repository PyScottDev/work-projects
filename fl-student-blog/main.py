from datetime import date
from flask import Flask, abort, render_template, redirect, url_for, flash, session
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, ForeignKey
from functools import wraps
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
import os
import cloudinary
import cloudinary.uploader
import cloudinary.utils
import time
from datetime import timedelta
from forms import CreatePostForm, CommentForm

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(
    __name__,
    instance_path=os.path.join(BASE_DIR, "instance"),
    instance_relative_config=True
)
db_path = os.path.join(app.instance_path, "posts.db")

app.config['SECRET_KEY'] = os.getenv("FLASK_SECRET_KEY")

oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

cloudinary.config(
  cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME"),
  api_key = os.getenv("CLOUDINARY_API_KEY"),
  api_secret = os.getenv("CLOUDINARY_API_SECRET"),
  secure = True
)

def get_signed_url(public_id):
    if public_id:
        signed_url, options = cloudinary.utils.cloudinary_url(
            public_id, 
            sign_url=True, 
            type="authenticated", 
            expires_at=int(time.time() + 3600),
            
            fetch_format="auto",  
            quality="auto",       
            width=1000,           
            crop="limit"          
        )
        return signed_url
    return None

@app.context_processor
def utility_processor():
    return dict(get_signed_url=get_signed_url)

app.config['CKEDITOR_SERVE_LOCAL'] = False # Ensure it uses CDN
app.config['CKEDITOR_PKG_TYPE'] = 'classic'
ckeditor = CKEditor(app)
Bootstrap5(app)



class Base(DeclarativeBase):
    pass



db_url = os.getenv("DATABASE_URL", f"postgresql://postgres:{os.getenv('DB_PASSWORD')}@localhost:5432/blog_db")
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
db = SQLAlchemy(model_class=Base)
db.init_app(app)


class User(UserMixin, db.Model):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    google_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)    
    name: Mapped[str] = mapped_column(String(100), nullable=False) 
    img_url: Mapped[str] = mapped_column(String(500), nullable=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=True)
    posts = relationship("BlogPost", back_populates="author")
    comments = relationship("Comment", back_populates="comment_author")
    

class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True) 
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("user.id"), nullable=False)
    author = relationship("User", back_populates="posts")
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)
    topic: Mapped[str] = mapped_column(String(100), nullable=True)
    level: Mapped[str] = mapped_column(String(100), nullable=True)
    cloudinary_public_id: Mapped[str] = mapped_column(String(500), nullable=True)
    comments = relationship("Comment", back_populates="parent_post")


class Comment(db.Model):
    __tablename__ = "comment"
    id: Mapped[int] = mapped_column(Integer, primary_key=True) 
    text: Mapped[str] = mapped_column(String(500), nullable=False)
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("user.id"), nullable=False)
    comment_author = relationship("User", back_populates="comments")
    post_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("blog_posts.id"), nullable=False)
    parent_post = relationship("BlogPost", back_populates="comments")



with app.app_context():
    db.create_all()

login_manager = LoginManager()
login_manager.init_app(app)

app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
login_manager.session_protection = "strong"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.email != "scottsomerville@flireland.com":
            return abort(403)
        return f(*args, **kwargs)
    return decorated_function


@app.route('/login')
def login():
    redirect_uri = url_for('auth_callback', _external=True)
    return google.authorize_redirect(redirect_uri)
    
@app.route('/auth/callback')
def auth_callback():
    # 1. The Exchange
    token = google.authorize_access_token()
    user_info = token.get('userinfo')
    
    # 2. The Gatekeeper (Domain Check)
    email = user_info.get('email')
    SCHOOL_DOMAIN = "flireland.com" # Replace with yours!
    if not email.endswith(f"@{SCHOOL_DOMAIN}"):
        flash(f"Access Denied. You must use a @{SCHOOL_DOMAIN} account.", "danger")
        return redirect(url_for("get_all_posts"))

    # 3. The Database Lookup
    google_id = user_info.get('sub')
    user = db.session.execute(db.select(User).where(User.google_id == google_id)).scalar()

    # 4. Just-In-Time Registration
    if not user:
        full_name = user_info.get('name', 'student')
        base_slug = full_name.lower().strip().replace(" ", "-")
        
        #Slug counter#
        new_slug = base_slug
        counter = 1
        
        #Slug search#
        while db.session.execute(db.select(User).where(User.slug == new_slug)).scalar():
            new_slug = f"{base_slug}-{counter}"
            counter += 1
        
        user = User(
            email=email,
            name=user_info.get('name'),
            google_id=google_id,
            img_url=user_info.get('picture'),
            slug=new_slug
        )
        db.session.add(user)
        db.session.commit()

    # 5. The Session Hand-off
    session.permanent = True
    login_user(user)
    flash(f"Welcome, {user.name}!", "success")
    return redirect(url_for("get_all_posts"))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route('/')
def get_all_posts():
    result = db.session.execute(db.select(BlogPost).order_by(BlogPost.id.desc()))
    posts = result.scalars().all()
    return render_template("index.html", all_posts=posts)

@app.route("/user/<username_slug>")
def user_stories(username_slug):
    user = db.session.execute(db.select(User).where(User.slug == username_slug)).scalar()
    if not user:
        return abort(404)
    return render_template("index.html", all_posts=user.posts, profile_user=user)

@app.route("/topic/<topic_name>")
def show_topic(topic_name):
    result = db.session.execute(db.select(BlogPost).where(BlogPost.topic == topic_name))
    posts = result.scalars().all()
    return render_template("index.html", all_posts=posts, category_name=topic_name)

@app.route("/level/<level_name>")
def show_level(level_name):
    result = db.session.execute(db.select(BlogPost).where(BlogPost.level == level_name))
    posts = result.scalars().all()
    return render_template("index.html", all_posts=posts, category_name=level_name)

@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    requested_post = db.get_or_404(BlogPost, post_id)
    display_image = get_signed_url(requested_post.cloudinary_public_id) or requested_post.img_url
    comment_form = CommentForm()
    if comment_form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You need to login or register to comment.")
            return redirect(url_for("login"))

        new_comment = Comment(
            text=comment_form.comment.data,
            comment_author=current_user,
            parent_post=requested_post
        )
        db.session.add(new_comment)
        db.session.commit()
    requested_post = db.get_or_404(BlogPost, post_id)
    return render_template("post.html", post=requested_post, image=display_image, form=comment_form)


@app.route("/new-post", methods=["GET", "POST"])
@login_required
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        image_file = form.upload.data
        img_url = form.img_url.data or "https://images.unsplash.com/photo-1432821596592-e2c18b78144f"
        public_id = None
        
        if image_file:
            upload_result = cloudinary.uploader.upload(
                image_file, 
                type="authenticated",
                folder="student_blog_uploads/"
            )
            img_url = upload_result['secure_url']
            public_id = upload_result['public_id']
            
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=img_url,
            cloudinary_public_id=public_id,
            author=current_user,
            date=date.today().strftime("%B %d, %Y"),
            topic=form.topic.data, 
            level=form.level.data
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)


@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@login_required
def edit_post(post_id):
    post = db.get_or_404(BlogPost, post_id)
    if current_user.id != post.author_id and current_user.email != "scottsomerville@flireland.com":
        return abort(403)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        topic=post.topic,
        level=post.level,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        image_file = edit_form.upload.data
        if image_file:
            if post.cloudinary_public_id:
                cloudinary.uploader.destroy(post.cloudinary_public_id, type="authenticated")
            upload_result = cloudinary.uploader.upload(image_file, type="authenticated", folder="student_blog_uploads/")
            post.img_url = upload_result['secure_url']
            post.cloudinary_public_id = upload_result['public_id']
        else:
            post.img_url = edit_form.img_url.data
        
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.topic = edit_form.topic.data 
        post.level = edit_form.level.data 
        post.body = edit_form.body.data
        
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))
    return render_template("make-post.html", form=edit_form, is_edit=True)


@app.route("/delete/<int:post_id>")
@login_required
def delete_post(post_id):
    post_to_delete = db.get_or_404(BlogPost, post_id)
    if current_user.id != post.author_id and current_user.email != "scottsomerville@flireland.com":
        return abort(403)
    if post_to_delete.cloudinary_public_id:
        cloudinary.uploader.destroy(
            post_to_delete.cloudinary_public_id, 
            type="authenticated"
        )
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=False, port=5002)
