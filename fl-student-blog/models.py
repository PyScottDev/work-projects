from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Text, ForeignKey


class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)


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
    marketplace_items = relationship("MarketplaceItem", back_populates="seller")
    marketplace_comments = relationship("MarketplaceComment", back_populates="comment_author")
    

class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True) 
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("user.id"), nullable=False)
    author = relationship("User", back_populates="posts")
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    img_url: Mapped[str] = mapped_column(Text, nullable=False)
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
    

class MarketplaceItem(db.Model):
    __tablename__ = "marketplace_items"

    id = mapped_column(Integer, primary_key=True)
    seller_id = mapped_column(Integer, db.ForeignKey("user.id"), nullable=False)
    seller = relationship("User", back_populates="marketplace_items")
    comments = relationship("MarketplaceComment", back_populates="parent_item")
    title = mapped_column(String(250), nullable=False)
    description = mapped_column(Text, nullable=False)
    price = mapped_column(Integer, nullable=True) 
    condition = mapped_column(String(100), nullable=True)
    category = mapped_column(String(100), nullable=True)
    available = mapped_column(db.Boolean, default=True)
    date = mapped_column(String(250), nullable=False)
    image_1_public_id = mapped_column(String(500), nullable=True)
    image_2_public_id = mapped_column(String(500), nullable=True)
    image_3_public_id = mapped_column(String(500), nullable=True)
    
    
class MarketplaceComment(db.Model):
    __tablename__ = "marketplace_comment"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(String(500), nullable=False)

    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("user.id"), nullable=False)
    item_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("marketplace_items.id"), nullable=False)
    comment_author = relationship("User", back_populates="marketplace_comments")
    parent_item = relationship("MarketplaceItem", back_populates="comments")