from flask import Blueprint, render_template, request, session, redirect, url_for, make_response
from app.database import get_db

main_bp = Blueprint('main', __name__)
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Basic routes to render templates

@main_bp.route('/')
def index():
	return render_template('index.html')

@main_bp.route('/signin', methods=['GET'])
def signin_page():
	return render_template('signin.html')

@main_bp.route('/signin', methods=['POST'])
def signin():
	"""Vulnerable login endpoint - intentionally uses string concatenation SQL for boolean-based SQL injection."""
	username = request.form.get('username', '')
	password = request.form.get('password', '')
	
	db = get_db()
	
	# INTENTIONALLY VULNERABLE: String concatenation allows SQL injection
	query = (
		"SELECT * FROM users "
		"WHERE username = '" + username + "' "
		"AND password = '" + password + "'"
	)
	user = db.execute(query).fetchone()
	
	if user:
		session.clear()
		session['user_id'] = user['id']
		session['username'] = user['username']
		resp = make_response(redirect(url_for('main.index')))
		resp.set_cookie('user_id', str(user['id']))
		resp.set_cookie('access_token', 'example-access-token')
		resp.set_cookie('refresh_token', 'example-refresh-token')
		return resp
	
	# Return to signin page with error
	return render_template('signin.html', error='Invalid username or password')

@main_bp.route('/signup', methods=['GET'])
def signup_page():
	return render_template('signup.html')

@main_bp.route('/signup', methods=['POST'])
def signup():
	"""Register new user - stores plaintext password."""
	username = request.form.get('username', '')
	email = request.form.get('email', '')
	password = request.form.get('password', '')
	confirm = request.form.get('confirm', '')
	
	error = None
	
	if not username:
		error = 'Username is required.'
	elif not email:
		error = 'Email is required.'
	elif not password:
		error = 'Password is required.'
	elif password != confirm:
		error = 'Passwords do not match.'
	
	if error is None:
		db = get_db()
		try:
			# Insert user with plaintext password (intentionally insecure)
			db.execute(
				'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
				(username, email, password)
			)
			db.commit()
			return redirect(url_for('main.signin_page'))
		except db.IntegrityError:
			error = 'Email already registered.'
	
	return render_template('signup.html', error=error)

@main_bp.route('/logout')
def logout():
	"""Clear session and logout user."""
	session.clear()
	return redirect(url_for('main.index'))
