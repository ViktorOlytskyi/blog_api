from flask import request, jsonify
from flask_jwt_extended import (
    JWTManager, create_access_token,
    jwt_required, get_jwt_identity
)
from flask_bcrypt import Bcrypt
from app import app, db
from models.models import User, Category, Article, Comment, Like, Dislike

bcrypt = Bcrypt(app)
jwt = JWTManager(app)

@app.route('/register', methods=['POST'])
def register():
    username = request.json.get('username')
    password = request.json.get('password')

    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({"message": "Такий користувач вже існує"}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "Реєстрація пройшла успішно"}), 201

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')

    user = User.query.filter_by(username=username).first()
    if not user or not bcrypt.check_password_hash(user.password, password):
        return jsonify({"message": "Неправильні дані для входу"}), 401

    access_token = create_access_token(identity=user.id)
    return jsonify({"access_token": access_token}), 200

@app.route('/change_password', methods=['POST'])
@jwt_required()
def change_password():
    current_user_id = get_jwt_identity()
    user = User.query.filter_by(id=current_user_id).first()

    if not user:
        return jsonify({"message": "Користувача не знайдено"}), 404

    current_password = request.json.get('current_password')
    new_password = request.json.get('new_password')

    if not bcrypt.check_password_hash(user.password, current_password):
        return jsonify({"message": "Поточний пароль невірний"}), 401

    hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
    user.password = hashed_password
    db.session.commit()

    return jsonify({"message": "Пароль змінено успішно"}), 200

@app.route('/api/articles', methods=['GET'])
def get_articles():
    articles = Article.query.all()
    article_list = []
    for article in articles:
        article_list.append({
            'id': article.id,
            'title': article.title,
            'content': article.content,
            'category': article.category.name if article.category else None,
            'created_at': article.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'likes': article.likes.count(),
            'dislikes': article.dislikes.count()
        })
    return jsonify({'articles': article_list})

@app.route('/api/articles/<int:article_id>', methods=['GET'])
def get_article(article_id):
    article = Article.query.get(article_id)
    if not article:
        return jsonify({'message': 'Стаття не знайдена'}), 404
    return jsonify({
        'id': article.id,
        'title': article.title,
        'content': article.content,
        'category': article.category.name if article.category else None,
        'created_at': article.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'likes': article.likes.count(),
        'dislikes': article.dislikes.count()
    })

@app.route('/articles', methods=['POST'])
@jwt_required()
def create_article():
    user_id = get_jwt_identity()
    data = request.json
    title = data.get('title')
    content = data.get('content')
    category_id = data.get('category_id')

    category = Category.query.get(category_id) if category_id else None

    new_article = Article(title=title, content=content, category=category, user_id=user_id)
    db.session.add(new_article)
    db.session.commit()
    return jsonify({'message': 'Стаття успішно створена'}), 201

@app.route('/articles/<int:article_id>', methods=['PUT'])
@jwt_required()
def update_article(article_id):
    user_id = get_jwt_identity()
    article = Article.query.get(article_id)
    if not article:
        return jsonify({'message': 'Стаття не знайдена'}), 404
    if article.user_id != user_id:
        return jsonify({'message': 'Ви не маєте прав на редагування цієї статті'}), 403

    data = request.json
    article.title = data.get('title', article.title)
    article.content = data.get('content', article.content)
    article.category_id = data.get('category_id', article.category_id)

    db.session.commit()
    return jsonify({'message': 'Стаття успішно оновлена'}), 200

@app.route('/articles/<int:article_id>', methods=['DELETE'])
@jwt_required()
def delete_article(article_id):
    user_id = get_jwt_identity()
    article = Article.query.get(article_id)
    if not article:
        return jsonify({'message': 'Стаття не знайдена'}), 404
    if article.user_id != user_id:
        return jsonify({'message': 'Ви не маєте прав на видалення цієї статті'}), 403

    db.session.delete(article)
    db.session.commit()
    return jsonify({'message': 'Стаття успішно видалена'}), 200

@app.route('/articles/<int:article_id>/like', methods=['POST'])
@jwt_required()
def like_article(article_id):
    user_id = get_jwt_identity()
    article = Article.query.get(article_id)
    if not article:
        return jsonify({'message': 'Стаття не знайдена'}), 404

    if user_id in [like.user_id for like in article.likes]:
        return jsonify({'message': 'Ви вже лайкнули цю статтю'}), 400

    like = Like(user_id=user_id, article_id=article_id)
    db.session.add(like)
    article.likes.append(like)
    db.session.commit()
    return jsonify({'message': 'Лайк доданий'}), 201

@app.route('/articles/<int:article_id>/dislike', methods=['POST'])
@jwt_required()
def dislike_article(article_id):
    user_id = get_jwt_identity()
    article = Article.query.get(article_id)
    if not article:
        return jsonify({'message': 'Стаття не знайдена'}), 404

    if user_id in [dislike.user_id for dislike in article.dislikes]:
        return jsonify({'message': 'Ви вже дізлайкнули цю статтю'}), 400

    dislike = Dislike(user_id=user_id, article_id=article_id)
    db.session.add(dislike)
    article.dislikes.append(dislike)
    db.session.commit()
    return jsonify({'message': 'Дізлайк доданий'}), 201

@app.route('/articles/<int:article_id>/comments', methods=['GET'])
def get_comments(article_id):
    article = Article.query.get(article_id)
    if not article:
        return jsonify({'message': 'Стаття не знайдена'}), 404

    comments = Comment.query.filter_by(article_id=article_id)
    comment_list = []
    for comment in comments:
        comment_list.append({
            'id': comment.id,
            'content': comment.content,
            'user_id': comment.user_id,
            'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    return jsonify({'comments': comment_list})

@app.route('/articles/<int:article_id>/comments', methods=['POST'])
@jwt_required()
def create_comment(article_id):
    user_id = get_jwt_identity()
    article = Article.query.get(article_id)
    if not article:
        return jsonify({'message': 'Стаття не знайдена'}), 404

    data = request.json
    content = data.get('content')

    new_comment = Comment(content=content, user_id=user_id, article_id=article_id)
    db.session.add(new_comment)
    db.session.commit()
    return jsonify({'message': 'Коментар успішно доданий'}), 201
