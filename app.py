"""
SecureVault – File Encryption & Digital Signature Platform
Main Flask application entry point.
"""

import os
from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, send_file, session
)
from flask_login import (
    login_user, logout_user, login_required, current_user
)
from werkzeug.utils import secure_filename

from extensions import db, login_manager
from modules.auth import User
from modules.encryption import encrypt_file, decrypt_file
from modules.signature import generate_key_pair, sign_file, verify_signature

# ── Configuration ────────────────────────────────────────────────────────────

BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
KEYS_FOLDER   = os.path.join(BASE_DIR, 'keys')
ALLOWED_EXT   = {'txt', 'pdf', 'png', 'jpg', 'docx', 'xlsx', 'zip', 'py', 'json', 'csv'}
MAX_FILE_MB   = 16


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY']          = os.urandom(32).hex()
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///securevault.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER']       = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH']  = MAX_FILE_MB * 1024 * 1024

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(KEYS_FOLDER,   exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view    = 'login'
    login_manager.login_message = 'Please log in to access SecureVault.'
    login_manager.login_message_category = 'warning'

    with app.app_context():
        db.create_all()

    return app


app = create_app()


# ── Helpers ──────────────────────────────────────────────────────────────────

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT


def user_upload_dir(username):
    path = os.path.join(UPLOAD_FOLDER, username)
    os.makedirs(path, exist_ok=True)
    return path


# ── Auth Routes ──────────────────────────────────────────────────────────────

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm  = request.form.get('confirm_password', '')

        if not all([username, email, password, confirm]):
            flash('All fields are required.', 'danger')
            return render_template('register.html')

        if password != confirm:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html')

        if len(password) < 8:
            flash('Password must be at least 8 characters.', 'danger')
            return render_template('register.html')

        if User.query.filter_by(username=username).first():
            flash('Username already taken.', 'danger')
            return render_template('register.html')

        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return render_template('register.html')

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('Account created! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(url_for('dashboard'))

        flash('Invalid username or password.', 'danger')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


# ── Dashboard ─────────────────────────────────────────────────────────────────

@app.route('/dashboard')
@login_required
def dashboard():
    upload_dir = user_upload_dir(current_user.username)
    files = []
    for f in os.listdir(upload_dir):
        fpath = os.path.join(upload_dir, f)
        if os.path.isfile(fpath) and not f.endswith('.sig'):
            size = os.path.getsize(fpath)
            files.append({
                'name': f,
                'size': f'{size / 1024:.1f} KB',
                'is_encrypted': f.endswith('.enc'),
                'has_signature': os.path.exists(fpath + '.sig')
            })

    # Load public key for key viewer modal
    pub_key_pem = None
    pub_key_path = os.path.join(KEYS_FOLDER, f'{current_user.username}_public.pem')
    if os.path.exists(pub_key_path):
        with open(pub_key_path, 'r') as f:
            pub_key_pem = f.read()

    return render_template('dashboard.html', files=files, public_key_pem=pub_key_pem)


# ── Upload ────────────────────────────────────────────────────────────────────

@app.route('/upload', methods=['POST'])
@login_required
def upload():
    if 'file' not in request.files:
        flash('No file selected.', 'danger')
        return redirect(url_for('dashboard'))

    file = request.files['file']
    if file.filename == '':
        flash('No file selected.', 'danger')
        return redirect(url_for('dashboard'))

    if not allowed_file(file.filename):
        flash(f'File type not allowed. Allowed: {", ".join(ALLOWED_EXT)}', 'danger')
        return redirect(url_for('dashboard'))

    filename = secure_filename(file.filename)
    save_path = os.path.join(user_upload_dir(current_user.username), filename)
    file.save(save_path)
    flash(f'"{filename}" uploaded successfully.', 'success')
    return redirect(url_for('dashboard'))


# ── Encrypt ───────────────────────────────────────────────────────────────────

@app.route('/encrypt', methods=['POST'])
@login_required
def encrypt():
    filename = request.form.get('filename', '').strip()
    password = request.form.get('password', '')

    if not filename or not password:
        flash('Filename and password are required.', 'danger')
        return redirect(url_for('dashboard'))

    upload_dir  = user_upload_dir(current_user.username)
    input_path  = os.path.join(upload_dir, secure_filename(filename))
    output_path = input_path + '.enc'

    if not os.path.exists(input_path):
        flash('File not found.', 'danger')
        return redirect(url_for('dashboard'))

    result = encrypt_file(input_path, output_path, password)
    if result['success']:
        os.remove(input_path)
        flash(f'"{filename}" encrypted successfully → "{filename}.enc"', 'success')
    else:
        flash(f'Encryption failed: {result["message"]}', 'danger')

    return redirect(url_for('dashboard'))


# ── Decrypt ───────────────────────────────────────────────────────────────────

@app.route('/decrypt', methods=['POST'])
@login_required
def decrypt():
    filename = request.form.get('filename', '').strip()
    password = request.form.get('password', '')

    if not filename or not password:
        flash('Filename and password are required.', 'danger')
        return redirect(url_for('dashboard'))

    upload_dir  = user_upload_dir(current_user.username)
    input_path  = os.path.join(upload_dir, secure_filename(filename))

    # Output: remove .enc extension
    output_name = filename[:-4] if filename.endswith('.enc') else filename + '.dec'
    output_path = os.path.join(upload_dir, output_name)

    if not os.path.exists(input_path):
        flash('File not found.', 'danger')
        return redirect(url_for('dashboard'))

    result = decrypt_file(input_path, output_path, password)
    if result['success']:
        os.remove(input_path)
        flash(f'"{filename}" decrypted successfully → "{output_name}"', 'success')
    else:
        flash(f'Decryption failed: {result["message"]}', 'danger')

    return redirect(url_for('dashboard'))


# ── Key Generation ────────────────────────────────────────────────────────────

@app.route('/generate-keys', methods=['POST'])
@login_required
def generate_keys():
    result = generate_key_pair(current_user.username, KEYS_FOLDER)
    if result['success']:
        current_user.has_keys = True
        db.session.commit()
        flash('RSA-2048 key pair generated successfully. You can now sign files.', 'success')
    else:
        flash(f'Key generation failed: {result["message"]}', 'danger')
    return redirect(url_for('dashboard'))


# ── Sign File ─────────────────────────────────────────────────────────────────

@app.route('/sign', methods=['POST'])
@login_required
def sign():
    filename = request.form.get('filename', '').strip()

    if not filename:
        flash('Filename is required.', 'danger')
        return redirect(url_for('dashboard'))

    upload_dir      = user_upload_dir(current_user.username)
    file_path       = os.path.join(upload_dir, secure_filename(filename))
    private_key_path = os.path.join(KEYS_FOLDER, f'{current_user.username}_private.pem')

    if not os.path.exists(file_path):
        flash('File not found.', 'danger')
        return redirect(url_for('dashboard'))

    if not os.path.exists(private_key_path):
        flash('No private key found. Please generate your key pair first.', 'warning')
        return redirect(url_for('dashboard'))

    result = sign_file(file_path, private_key_path)
    if result['success']:
        flash(f'"{filename}" signed successfully. Signature saved.', 'success')
    else:
        flash(f'Signing failed: {result["message"]}', 'danger')

    return redirect(url_for('dashboard'))


# ── Verify Signature ──────────────────────────────────────────────────────────

@app.route('/verify', methods=['POST'])
@login_required
def verify():
    filename = request.form.get('filename', '').strip()

    if not filename:
        flash('Filename is required.', 'danger')
        return redirect(url_for('dashboard'))

    upload_dir      = user_upload_dir(current_user.username)
    file_path       = os.path.join(upload_dir, secure_filename(filename))
    sig_path        = file_path + '.sig'
    public_key_path = os.path.join(KEYS_FOLDER, f'{current_user.username}_public.pem')

    if not os.path.exists(file_path):
        flash('File not found.', 'danger')
        return redirect(url_for('dashboard'))

    if not os.path.exists(sig_path):
        flash('No signature file found for this file.', 'warning')
        return redirect(url_for('dashboard'))

    if not os.path.exists(public_key_path):
        flash('No public key found. Please generate your key pair first.', 'warning')
        return redirect(url_for('dashboard'))

    result = verify_signature(file_path, sig_path, public_key_path)
    if result['success']:
        if result['valid']:
            flash(f'✅ "{filename}" — Signature VALID. File is authentic and untampered.', 'success')
        else:
            flash(f'❌ "{filename}" — Signature INVALID. File may have been tampered with!', 'danger')
    else:
        flash(f'Verification error: {result["message"]}', 'danger')

    return redirect(url_for('dashboard'))


# ── Download ──────────────────────────────────────────────────────────────────

@app.route('/download/<filename>')
@login_required
def download(filename):
    upload_dir = user_upload_dir(current_user.username)
    file_path  = os.path.join(upload_dir, secure_filename(filename))

    if not os.path.exists(file_path):
        flash('File not found.', 'danger')
        return redirect(url_for('dashboard'))

    return send_file(file_path, as_attachment=True)


# ── Delete ────────────────────────────────────────────────────────────────────

@app.route('/delete/<filename>', methods=['POST'])
@login_required
def delete(filename):
    upload_dir = user_upload_dir(current_user.username)
    file_path  = os.path.join(upload_dir, secure_filename(filename))
    sig_path   = file_path + '.sig'

    if os.path.exists(file_path):
        os.remove(file_path)
        if os.path.exists(sig_path):
            os.remove(sig_path)
        flash(f'"{filename}" deleted.', 'info')
    else:
        flash('File not found.', 'danger')

    return redirect(url_for('dashboard'))


# ── Rename File ───────────────────────────────────────────────

@app.route('/rename', methods=['POST'])
@login_required
def rename_file():
    old_filename = request.form.get('old_filename', '').strip()
    new_filename = request.form.get('new_filename', '').strip()

    if not old_filename or not new_filename:
        flash('Both old and new filenames are required.', 'danger')
        return redirect(url_for('dashboard'))

    upload_dir = user_upload_dir(current_user.username)
    old_path   = os.path.join(upload_dir, secure_filename(old_filename))
    new_path   = os.path.join(upload_dir, secure_filename(new_filename))

    if not os.path.exists(old_path):
        flash('File not found.', 'danger')
        return redirect(url_for('dashboard'))

    if os.path.exists(new_path):
        flash(f'A file named "{new_filename}" already exists.', 'danger')
        return redirect(url_for('dashboard'))

    os.rename(old_path, new_path)

    # Also rename the signature file if it exists
    old_sig = old_path + '.sig'
    new_sig = new_path + '.sig'
    if os.path.exists(old_sig):
        os.rename(old_sig, new_sig)

    flash(f'"{old_filename}" renamed to "{new_filename}".', 'success')
    return redirect(url_for('dashboard'))


# ── View / Download Public Key ────────────────────────────────

@app.route('/public-key/download')
@login_required
def download_public_key():
    pub_key_path = os.path.join(KEYS_FOLDER, f'{current_user.username}_public.pem')
    if not os.path.exists(pub_key_path):
        flash('No public key found. Generate your RSA keys first.', 'warning')
        return redirect(url_for('dashboard'))
    return send_file(pub_key_path, as_attachment=True,
                     download_name=f'{current_user.username}_public.pem')


# ── Run ───────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    app.run(debug=True, port=5000)
