from flask import jsonify, request
from models import *
from utils import *

@app.route('/api/v1/posts/all', methods=['GET'])
def handle_get_all_posts():
    posts = get_all_posts()
    post_list = [format_response(post) for post in posts]
    return jsonify(post_list)

@app.route('/api/v1/posts/<int:post_id>', methods=['GET'])
def handle_view_post(post_id):
    post = find_post_by_id(post_id)
    if not post:
        return jsonify({'message': 'Post not found!'}), 404
    post_dict = format_response(post, show_replies=True)
    return jsonify(post_dict)

@app.route('/api/v1/posts/create', methods=['POST'])
@validate_token
def handle_create_post(user):
    post_body = get_post_body(request)
    if not post_body:
        return jsonify({'error': 'No post body found in the request'}), 400
    new_post = create_post(user,post_body)
    add_post(new_post)
    return jsonify({'message': 'Post created successfully!'})

@app.route('/api/v1/posts/<int:post_id>/reply', methods=['POST'])
@validate_token
def handle_create_reply(user, post_id):
    if not post_exists(post_id):
        return jsonify({'message': 'Post not found!'}), 404
    reply_body = get_post_body(request)
    if not reply_body:
        return jsonify({'error': 'No post body found in the request'}), 400
    new_reply = create_reply(user,reply_body,post_id)
    add_post(new_reply)
    return jsonify({'message': 'Reply added successfully!'})

@app.route('/api/v1/posts/like/<int:post_id>', methods=['POST'])
@validate_token
def handle_like_post(user, post_id):
    post = find_post_by_id(post_id)
    if not post:
        return jsonify({'message': 'Post not found!'}), 404
    db.session.refresh(user)
    like_post(user, post, db.session)
    return jsonify({'message': 'Post liked successfully!'})

@app.route('/api/v1/posts/unlike/<int:post_id>', methods=['POST'])
@validate_token
def handle_unlike_post(user, post_id):
    post = find_post_by_id(post_id)
    if not post:
        return jsonify({'message': 'Post not found!'}), 404
    db.session.refresh(user)
    unlike_post(user, post, db.session)
    return jsonify({'message': 'Post unliked successfully!'})

@app.route('/api/v1/posts/edit/<post_id>', methods=['PUT'])
@validate_token
def handle_edit_post(user, post_id):
    post = find_post_by_id(post_id)
    if not post:
        return jsonify({'message': 'Post not found!'}), 404
    if not is_admin_or_post_owner(user, post):
        return jsonify({'message': "Cannot edit others post!"}), 401
    new_body = get_post_body(request)
    if not new_body:
        return jsonify({'error': 'No post body found in the request'}), 400
    edit_post(post, new_body)
    return jsonify({'message': 'Post updated successfully!'})

@app.route("/api/v1/posts/delete/<post_id>", methods=['DELETE'])
@validate_token
def handle_delete_post(user, post_id):
    post = find_post_by_id(post_id)
    if not post:
        return jsonify({'message': 'Post not found!'}), 404
    if not is_admin_or_post_owner(user, post):
        return jsonify({'message': 'Cannot delete others post!'}), 401
    delete_post(post)
    return jsonify({'message': 'Post deleted successfully!'})

@app.route('/api/v1/create-user', methods=['POST'])
def handle_create_user():
    username = request.json.get('name')
    if not username:
        return jsonify({'error': 'Username is required!'}), 400
    if len(username) > 100:
        return jsonify({'error': 'Username too long'}), 400
    result = create_user(username)
    return jsonify(result)

@app.route('/api/v1/posts/<int:post_id>/likes', methods=['GET'])
def see_liked_users(post_id):
    like_list = get_like_list(post_id)
    return jsonify(like_list)

if __name__ == '__main__':
    app.run(debug=True)