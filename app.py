from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, g
import sqlite3
import functools
from werkzeug.security import generate_password_hash, check_password_hash
from typing import Callable, Any, Union, Optional
from werkzeug.wrappers import Response as WerkzeugResponse
from flask.wrappers import Response as FlaskResponse
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo
import datetime
import pytz

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'

# データベース設定
DATABASE = 'perch_database.db'

def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# データベース接続をgオブジェクトに格納する関数
def get_db():
    if 'db' not in g:
        g.db = get_db_connection()
    return g.db

# リクエスト終了時にデータベース接続を閉じる関数
@app.teardown_appcontext
def close_db(error: Optional[BaseException] = None) -> None:
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db() -> None:
    """データベースの初期化"""
    with sqlite3.connect(DATABASE) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT,
                genre TEXT NOT NULL,
                user_type TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TIMESTAMP
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS admin_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP
            )
        ''')
        # デフォルト管理者アカウント
        if conn.execute('SELECT COUNT(*) FROM admin_users').fetchone()[0] == 0:
            tokyo_tz = pytz.timezone('Asia/Tokyo')
            current_time_jst = datetime.datetime.now(tokyo_tz)
            conn.execute(
                'INSERT INTO admin_users (username, password_hash, created_at) VALUES (?, ?, ?)',
                ('admin', generate_password_hash('admin123'), current_time_jst)
            )
        conn.commit()

# WTFormsのフォームクラスを定義
class LoginForm(FlaskForm):
    username = StringField('ユーザー名', validators=[DataRequired()])
    password = PasswordField('パスワード', validators=[DataRequired()])
    submit = SubmitField('ログイン')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('現在のパスワード', validators=[DataRequired()])
    new_password = PasswordField('新しいパスワード', validators=[DataRequired()])
    confirm_password = PasswordField('新しいパスワード (確認)', validators=[DataRequired(), EqualTo('new_password', message='パスワードが一致しません。')])
    submit = SubmitField('パスワードを変更')

# ログインを必須にするためのデコレータ
ViewFunc = Callable[..., Union[str, FlaskResponse, WerkzeugResponse]]
def login_required(view: ViewFunc) -> Callable[..., Union[str, FlaskResponse, WerkzeugResponse]]:
    @functools.wraps(view)
    def wrapped_view(**kwargs: Any) -> Union[str, FlaskResponse, WerkzeugResponse]:
        if 'logged_in' not in session:
            flash('ログインが必要です。', 'error')
            return redirect(url_for('admin_login'))
        return view(**kwargs)
    return wrapped_view

# 一般ユーザー向けルート
@app.route('/')
def index() -> str:
    return render_template('index.html')

@app.route('/about')
def about() -> str:
    return render_template('about.html')

@app.route('/concept')
def concept() -> str:
    return render_template('concept.html')

@app.route('/product')
def product() -> str:
    return render_template('product.html')

@app.route('/machine')
def machine() -> str:
    return render_template('machine.html')

@app.route('/shop')
def shop() -> str:
    return render_template('shop.html')

@app.route('/access', methods=['GET', 'POST'])
def access() -> Union[str, WerkzeugResponse]:
    if request.method == 'POST':
        try:
            name = request.form['name']
            email = request.form['email']
            phone = request.form.get('tel', '')
            genre = request.form['genre']
            user_type = request.form['user-type']
            message = request.form['message']
            if not name or not email or not message:
                flash('必須項目を入力してください。', 'error')
                return render_template('access.html')
            
            # タイムゾーンを日本標準時（JST）に設定して時刻を取得
            tokyo_tz = pytz.timezone('Asia/Tokyo')
            created_at_jst = datetime.datetime.now(tokyo_tz)

            conn = get_db_connection()
            conn.execute(
                'INSERT INTO contacts (name, email, phone, genre, user_type, message, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (name, email, phone, genre, user_type, message, created_at_jst)
            )
            conn.commit()
            conn.close()
            flash('お問い合わせを受け付けました。ありがとうございます。', 'success')
            return redirect(url_for('access'))
        except Exception as e:
            print(f"Error: {e}")
            flash('エラーが発生しました。再度お試しください。', 'error')
            return render_template('access.html')
    return render_template('access.html')

# 管理者向けルート
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login() -> Union[str, WerkzeugResponse]:
    if 'logged_in' in session:
        return redirect(url_for('admin_dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        conn = get_db()
        user = conn.execute('SELECT * FROM admin_users WHERE username = ?', (username,)).fetchone()
        if user and check_password_hash(user['password_hash'], password):
            session['logged_in'] = True
            session['username'] = user['username']
            flash('ログインしました。', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('ユーザー名またはパスワードが正しくありません。', 'error')
    return render_template('admin/login.html', form=form)

@app.route('/admin/logout')
def admin_logout() -> WerkzeugResponse:
    session.pop('logged_in', None)
    session.pop('username', None)
    flash('ログアウトしました。', 'success')
    return redirect(url_for('admin_login'))

@app.route('/admin/change_password', methods=['GET', 'POST'])
@login_required
def admin_change_password() -> Union[str, WerkzeugResponse]:
    form = ChangePasswordForm()
    if form.validate_on_submit():
        conn = get_db()
        user = conn.execute('SELECT * FROM admin_users WHERE username = ?', (session['username'],)).fetchone()
        
        if not check_password_hash(user['password_hash'], form.current_password.data):
            flash('現在のパスワードが間違っています。', 'error')
            return redirect(url_for('admin_change_password'))

        new_password_hash = generate_password_hash(form.new_password.data)
        conn.execute('UPDATE admin_users SET password_hash = ? WHERE id = ?', (new_password_hash, user['id']))
        conn.commit()

        flash('パスワードが正常に変更されました。', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('admin/change_password.html', form=form)

@app.route('/admin/')
@login_required
def admin_dashboard() -> str:
    return render_template('admin/dashboard.html')

@app.route('/admin/contacts')
@login_required
def admin_contacts() -> str:
    conn = get_db()
    contacts = conn.execute('SELECT * FROM contacts ORDER BY created_at DESC').fetchall()
    return render_template('admin/contacts.html', contacts=contacts)

@app.route('/admin/contact/<int:contact_id>')
@login_required
def admin_contact_detail(contact_id: int) -> Union[str, WerkzeugResponse]:
    conn = get_db()
    contact = conn.execute('SELECT * FROM contacts WHERE id = ?', (contact_id,)).fetchone()
    if contact is None:
        flash('お問い合わせが見つかりません。', 'error')
        return redirect(url_for('admin_contacts'))
    return render_template('admin/contact_detail.html', contact=contact)

@app.route('/admin/api/contacts')
@login_required
def api_contacts() -> FlaskResponse:
    conn = get_db()
    contacts = conn.execute('SELECT * FROM contacts ORDER BY created_at DESC').fetchall()
    return jsonify([dict(contact) for contact in contacts])

@app.route('/admin/api/stats')
@login_required
def api_stats() -> FlaskResponse:
    conn = get_db()
    tokyo_tz = pytz.timezone('Asia/Tokyo')
    now_jst = datetime.datetime.now(tokyo_tz)
    current_month_str = now_jst.strftime('%Y-%m')

    total_contacts = conn.execute('SELECT COUNT(*) FROM contacts').fetchone()[0]
    this_month = conn.execute(
        "SELECT COUNT(*) FROM contacts WHERE strftime('%Y-%m', created_at) = ?",
        (current_month_str,)
    ).fetchone()[0]
    genre_stats = conn.execute('SELECT genre, COUNT(*) FROM contacts GROUP BY genre').fetchall()
    user_type_stats = conn.execute('SELECT user_type, COUNT(*) FROM contacts GROUP BY user_type').fetchall()
    
    return jsonify({
        'total_contacts': total_contacts,
        'this_month': this_month,
        'genre_stats': [{'genre': g[0], 'count': g[1]} for g in genre_stats],
        'user_type_stats': [{'user_type': u[0], 'count': u[1]} for u in user_type_stats]
    })

@app.errorhandler(404)
def not_found_error(error: Exception) -> tuple[str, int]:
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error: Exception) -> tuple[str, int]:
    return render_template('errors/500.html'), 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)