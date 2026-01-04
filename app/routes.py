from flask import Blueprint, render_template, request, session, redirect, url_for, make_response
from app.database import get_db
import os

main_bp = Blueprint('main', __name__)
api_bp = Blueprint('api', __name__, url_prefix='/api')

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


@main_bp.route('/')
def index():
	return render_template('index.html')

@main_bp.route('/signin', methods=['GET'])
def signin_page():
	return render_template('signin.html')

@main_bp.route('/signin', methods=['POST'])
def signin():
	username = request.form.get('username', '')
	password = request.form.get('password', '')
	
	db = get_db()
	
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
	
	return render_template('signin.html', error='Invalid username or password')

@main_bp.route('/signup', methods=['GET'])
def signup_page():
	return render_template('signup.html')

@main_bp.route('/signup', methods=['POST'])
def signup():
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
	session.clear()
	resp = make_response(redirect(url_for('main.index')))
	resp.set_cookie('user_id', '', expires=0)
	resp.set_cookie('access_token', '', expires=0)
	resp.set_cookie('refresh_token', '', expires=0)
	return resp

@main_bp.route('/todos')
def todos():
	if not session.get('user_id'):
		return redirect(url_for('main.signin_page'))
	
	db = get_db()
	todos = db.execute('SELECT * FROM todos ORDER BY created_at DESC').fetchall()
	return render_template('todos.html', todos=todos)

@main_bp.route('/todos/add', methods=['POST'])
def add_todo():
	if not session.get('user_id'):
		return redirect(url_for('main.signin_page'))
	
	title = request.form.get('title', '')
	description = request.form.get('description', '')
	due_date = request.form.get('due_date', '')
	
	db = get_db()
	query = f'INSERT INTO todos (title, description, due_date) VALUES ("{title}", "{description}", "{due_date}")'
	db.execute(query)
	db.commit()
	
	return redirect(url_for('main.todos'))

@main_bp.route('/todos/delete/<int:todo_id>')
def delete_todo(todo_id):
	if not session.get('user_id'):
		return redirect(url_for('main.signin_page'))
	
	db = get_db()
	query = f"DELETE FROM todos WHERE id = {todo_id}"
	db.execute(query)
	db.commit()
	
	return redirect(url_for('main.todos'))

@main_bp.route('/todos/search')
def search_todos():
	if not session.get('user_id'):
		return redirect(url_for('main.signin_page'))
	
	search = request.args.get('q', '')
	db = get_db()
	
	if search:
		query = "SELECT * FROM todos WHERE title LIKE '" + search + "' OR description LIKE '" + search +"'"
		print(f"DEBUG - Search query: {query}")
		todos = db.execute(query).fetchall()
		print(f"DEBUG - Query results: {len(todos)} rows returned")
		for i, todo in enumerate(todos):
			print(f"DEBUG - Row {i}: {dict(todo)}")
	else:
		todos = db.execute('SELECT * FROM todos ORDER BY created_at DESC').fetchall()
	
	return render_template('todos.html', todos=todos, search=search)

@main_bp.route('/notes')
def notes():
	if not session.get('user_id'):
		return redirect(url_for('main.signin_page'))
	
	filename = os.path.join(BASE_DIR, "shared_notes.txt")
	output = ""
	error = ""
	
	try:
		with os.popen("cat " + filename) as f:
			output = f.read()
	except Exception as e:
		error = str(e)
	
	return render_template('notes.html', filename=filename, output=output, error=error)

@main_bp.route('/notes/search', methods=['POST'])
def search_notes():
	if not session.get('user_id'):
		return redirect(url_for('main.signin_page'))
	
	filename = os.path.join(BASE_DIR, "shared_notes.txt")
	search_term = request.form.get('search_term', '').strip()
	output = ""
	error = ""
	
	if search_term:
		try:
			with os.popen(f"grep '{search_term}' {filename}") as f:
				output = f.read()
		except Exception as e:
			error = str(e)
		return render_template('notes.html', filename=filename, search_term=search_term, output=output, error=error, is_search=True)
	else:
		try:
			with os.popen("cat " + filename) as f:
				output = f.read()
		except Exception as e:
			error = str(e)
		return render_template('notes.html', filename=filename, output=output, error=error)

@main_bp.route('/notes/clear')
def clear_search():
	if not session.get('user_id'):
		return redirect(url_for('main.signin_page'))
	
	return redirect(url_for('main.notes'))
