from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextAreaField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditorField


# WTForm for creating a blog post
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    topic = SelectField("Topic", choices=[
        ("Coming to Ireland", "Coming to Ireland"), 
        ("Life in Ireland", "Life in Ireland"), 
        ("Future plans", "Future plans"),
        ("Other thoughts", "Other thoughts")
    ])
    level = SelectField("Level", choices=[
        ("Beginner", "Beginner"), 
        ("Foundation", "Foundation"), 
        ("Stage 1", "Stage 1"),
        ("Stage 2", "Stage 2"),
        ("Stage 3", "Stage 3"),
        ("Stage 4", "Stage 4")
    ])
    img_url = StringField("Blog Image URL (Optional)")
    upload = FileField("Upload Image File", validators=[
        FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')
    ])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


# TODO: Create a CommentForm so users can leave comments below posts
class CommentForm(FlaskForm):
    comment = TextAreaField("Comment", validators=[DataRequired()])
    submit = SubmitField("Submit")

