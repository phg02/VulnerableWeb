from flask import Blueprint, render_template, request, session, redirect, url_for, make_response, send_file, current_app
from werkzeug.utils import secure_filename
from app.database import get_db
import os
import requests

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
		session['role'] = user['role']
		session.permanent = True
		resp_redirect = url_for('main.admin_users') if user['role'] == 'admin' else url_for('main.index')
		resp = make_response(redirect(resp_redirect))
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
				'INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)',
				(username, email, password, 'user')
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
	
	if session.get('role') == 'admin':
		return render_template('index.html', error='Notes feature is not available for admin users.')
	
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
	
	if session.get('role') == 'admin':
		return render_template('index.html', error='Notes feature is not available for admin users.')
	
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

@main_bp.route('/admin/users')
def admin_users():
	if request.remote_addr in ['127.0.0.1', '::1', 'localhost']:
		db = get_db()
		users = db.execute('SELECT id, username, email, role, created_at FROM users ORDER BY created_at DESC').fetchall()
		return render_template('admin_users.html', users=users)
        
	if not session.get('user_id'):
		return redirect(url_for('main.signin_page'))
	
	if session.get('role') != 'admin':
		return redirect(url_for('main.todos'))
	
	db = get_db()
	users = db.execute('SELECT id, username, email, role, created_at FROM users ORDER BY created_at DESC').fetchall()
	return render_template('admin_users.html', users=users)

@main_bp.route('/admin/users/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
	if not session.get('user_id'):
		return redirect(url_for('main.signin_page'))
	
	if session.get('role') != 'admin':
		return render_template('index.html', error='Access denied. Admin only.')
	
	# Prevent admin from deleting themselves
	if user_id == session.get('user_id'):
		return render_template('admin_users.html', error='Cannot delete your own account.')
	
	db = get_db()
	db.execute('DELETE FROM users WHERE id = ?', (user_id,))
	db.commit()
	
	return redirect(url_for('main.admin_users'))

@main_bp.route('/file/<path:filename>')
def unsafe_static(filename):
	return send_file(filename)

@main_bp.route('/upload', methods=['GET', 'POST'])
def upload_file():
	if not session.get('user_id'):
		return redirect(url_for('main.signin_page'))
	
	if request.method == 'POST':
		# Check if file is in request
		if 'file' not in request.files:
			return render_template('files.html', error='No file selected', uploaded_files=get_uploaded_files())
		
		f = request.files['file']
		
		if f.filename == '':
			return render_template('files.html', error='No file selected', uploaded_files=get_uploaded_files())
		
		if f:
			filename = secure_filename(f.filename)
			f.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
			return render_template('files.html', success='File uploaded successfully', uploaded_files=get_uploaded_files())
	
	return render_template('files.html', uploaded_files=get_uploaded_files())

@main_bp.route('/files', methods=['GET'])
def read_file():
	if not session.get('user_id'):
		return redirect(url_for('main.signin_page'))
	
	file = request.args.get('file')
	
	if not file:
		return redirect(url_for('main.upload_file'))
	
	try:
		# If file doesn't start with /, try uploads folder first
		if not file.startswith('/'):
			filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], file)
		else:
			filepath = file
		
		f = open(filepath, 'r')
		content = f.read()
		f.close()
		return render_template('view_file.html', filename=file, content=content)
	except Exception as e:
		return render_template('files.html', error=f'Error reading file: {str(e)}', uploaded_files=get_uploaded_files())

def get_uploaded_files():
	"""Get list of uploaded files"""
	upload_folder = current_app.config['UPLOAD_FOLDER']
	if not os.path.exists(upload_folder):
		return []
	return os.listdir(upload_folder)

@main_bp.route('/ssrf', methods=['GET', 'POST'])
def follow_url():
	if not session.get('user_id'):
		return redirect(url_for('main.signin_page'))
	
	url = request.args.get('url', '')
	content = ''
	error = ''
	
	if request.method == 'POST':
		url = request.form.get('url', '')
	
	if url:
		try:
			response = requests.get(url, timeout=5)
			content = response.text
		except Exception as e:
			error = f'Error fetching URL: {str(e)}'
	else:
		if request.method == 'POST' or request.method == 'GET' and 'url' in request.args:
			error = 'No URL parameter provided'
	
	return render_template('ssrf.html', url=url, content=content, error=error)
