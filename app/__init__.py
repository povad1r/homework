from datetime import datetime

from flask import Flask, render_template, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


app = Flask(__name__)
app.config['SECRET_KEY'] = '<KEY>'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'

db = SQLAlchemy(app)
migrate = Migrate(app, db)


"""
flask db init 
flask db migrate
flaks db upgrade
"""
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(80), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    post = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)


@app.route('/')
def index():
    posts = Post.query.all()
    return render_template('index.html', posts=posts)


@app.route('/add-post', methods=['GET', 'POST'])
def add_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        image_file = request.files['image']

        if image_file:
            image_path = 'static/uploads/' + title
            image_file.save(image_path)

            post = Post(title=title, content=content, image=image_path)
            db.session.add(post)
            db.session.commit()

            return {'status': 'success'}, 200
        else:
            return {'status': 'error', 'message': 'Image is required'}, 400

    return render_template('add-post.html')


@app.route('/post/<int:post_id>')
def post(post_id):
    post = Post.query.get(post_id)
    comments = Comment.query.filter_by(post=post_id)
    return render_template('post-detail.html', post=post, comments=comments)


@app.route('/post/<int:post_id>/add-comment', methods=['POST'])
def add_comment(post_id):
    content = request.form['content']
    comment = Comment(content=content, post=post_id)
    db.session.add(comment)
    db.session.commit()
    return jsonify({"new_comment": comment.content})


if __name__ == '__main__':
    app.run(debug=True)
