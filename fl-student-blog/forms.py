from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextAreaField, FloatField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, URL, Optional, NumberRange
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


class CreateNewMarketplace(FlaskForm):
    title = StringField("Item Title", validators=[DataRequired()])
    description = CKEditorField("Description", validators=[DataRequired()])

    category = SelectField("Category", choices=[
    ("Free stuff", "Free stuff"),
    ("Furniture", "Furniture"),
    ("Kitchen", "Kitchen"),
    ("Electronics", "Electronics"),
    ("Books", "Books"),
    ("Clothes", "Clothes"),
    ("Bike", "Bike"),
    ("Bags and luggage", "Bags and luggage"),
    ("Homeware", "Homeware"),
    ("Other", "Other"),
    ])
    condition = SelectField("Condition", choices=[
    ("New", "New"),
    ("Like new", "Like new"),
    ("Good", "Good"),
    ("Ok", "Ok"),
    ("Needs repair", "Needs repair"),
    ("Not applicable", "Not applicable"),
    ])
    
    price = FloatField("Price", validators=[Optional(), NumberRange(min=0, message="Price cannot be negative.")])
    
    img_url = StringField("Blog Image URL (Optional)")
    image_1 = FileField("Main image", validators=[
        FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')
    ])
    image_2 = FileField("Main image", validators=[
        FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')
    ])
    image_3 = FileField("Main image", validators=[
        FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')
    ])
    submit = SubmitField("Submit Item")

class CreateProjectForm(FlaskForm):
    title = StringField("Project Title", validators=[DataRequired()])
    description = CKEditorField("Project Description", validators=[DataRequired()])

    category = SelectField("Category", choices=[
        ("Class project", "Class project"),
        ("Presentation", "Presentation"),
        ("Poster", "Poster"),
        ("Video", "Video"),
        ("Writing collection", "Writing collection"),
        ("Other", "Other"),
    ])

    level = SelectField("Level", choices=[
        ("Beginner", "Beginner"), 
        ("Foundation", "Foundation"), 
        ("Stage 1", "Stage 1"),
        ("Stage 2", "Stage 2"),
        ("Stage 3", "Stage 3"),
        ("Stage 4", "Stage 4")
    ])

    image_url = StringField("Project Image URL (Optional)")
    upload = FileField("Upload Project Image", validators=[
        FileAllowed(["jpg", "png", "jpeg"], "Images only!")
    ])
    embed_code = TextAreaField("Canva / Google Slides Embed Code")
    submit = SubmitField("Submit Project")