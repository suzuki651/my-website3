from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, g
import sqlite3
import functools
from werkzeug.security import generate_password_hash, check_password_hash
from typing import Callable, Any, Union, Optional
from werkzeug.wrappers import Response as WerkzeugResponse
from flask.wrappers import Response as FlaskResponse
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Email, Length
import datetime
import pytz
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
import logging
from pathlib import Path

# 環境変数の読み込み
load_dotenv()

# 本番環境とローカル環境の区別
IS_PRODUCTION = os.getenv('FLASK_ENV') == 'production' or os.getenv('WEBSITE_SITE_NAME')

# ログレベルの設定
log_level = logging.INFO if IS_PRODUCTION else logging.DEBUG
logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Secret Keyの設定（本番環境では環境変数から取得）
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
if not IS_PRODUCTION and app.secret_key == 'your-secret-key-change-in-production':
    logger.warning("本番環境では必ずSECRET_KEYを環境変数で設定してください")

# CSRFプロテクションの設定
app.config['WTF_CSRF_ENABLED'] = True
app.config['WTF_CSRF_TIME_LIMIT'] = 3600  # 1時間（3600秒）

# メール設定（環境変数から取得）
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USER = os.getenv('EMAIL_USER', 'your-email@gmail.com')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', 'your-app-password')
EMAIL_FROM = os.getenv('EMAIL_FROM', 'your-email@gmail.com')

# デフォルト管理者アカウント設定（環境変数から取得）
DEFAULT_ADMIN_USERNAME = os.getenv('DEFAULT_ADMIN_USERNAME', 'admin')
DEFAULT_ADMIN_PASSWORD = os.getenv('DEFAULT_ADMIN_PASSWORD', 'change-this-password')
DEFAULT_ADMIN_EMAIL = os.getenv('DEFAULT_ADMIN_EMAIL', 'admin@example.com')
DEFAULT_ADMIN_SECURITY_QUESTION = os.getenv('DEFAULT_ADMIN_SECURITY_QUESTION', 'あなたの最初のペットの名前は？')
DEFAULT_ADMIN_SECURITY_ANSWER = os.getenv('DEFAULT_ADMIN_SECURITY_ANSWER', 'your-answer-here')

# データベース設定（Azure対応）
if IS_PRODUCTION:
    # Azure App Serviceでは /home ディレクトリが永続化される
    DATABASE = '/home/perch_database.db'
    # データディレクトリを作成
    try:
        db_dir = os.path.dirname(DATABASE)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            logger.info(f"データベースディレクトリを作成: {db_dir}")
    except Exception as e:
        logger.error(f"ディレクトリ作成エラー: {e}")
        # フォールバック: /tmpを使用
        DATABASE = '/tmp/perch_database.db'
        logger.warning(f"フォールバック: {DATABASE}を使用")
else:
    DATABASE = 'perch_database.db'

def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def create_default_admin(conn: sqlite3.Connection) -> None:
    """デフォルト管理者アカウントを作成する共通関数"""
    tokyo_tz = pytz.timezone('Asia/Tokyo')
    current_time_jst = datetime.datetime.now(tokyo_tz)
    conn.execute(
        '''INSERT INTO admin_users
           (username, password_hash, email, security_question, security_answer_hash, created_at)
           VALUES (?, ?, ?, ?, ?, ?)''',
        (DEFAULT_ADMIN_USERNAME,
         generate_password_hash(DEFAULT_ADMIN_PASSWORD),
         DEFAULT_ADMIN_EMAIL,
         DEFAULT_ADMIN_SECURITY_QUESTION,
         generate_password_hash(DEFAULT_ADMIN_SECURITY_ANSWER),
         current_time_jst)
    )
    logger.info(f"デフォルト管理者アカウントを作成しました: {DEFAULT_ADMIN_USERNAME}")

# データベース接続をgオブジェクトに格納する関数
def get_db():
    if 'db' not in g:
        g.db = get_db_connection()
    return g.db

@app.teardown_appcontext
def close_db(error: Optional[BaseException] = None) -> None:
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db() -> None:
    """データベースの初期化"""
    try:
        logger.info(f"データベース初期化開始: {DATABASE}")
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
                    email TEXT UNIQUE NOT NULL,
                    security_question TEXT NOT NULL,
                    security_answer_hash TEXT NOT NULL,
                    created_at TIMESTAMP
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS password_reset_tokens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    token TEXT UNIQUE NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    used BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES admin_users (id)
                )
            ''')
            
            # デフォルト管理者アカウント
            admin_count = conn.execute('SELECT COUNT(*) FROM admin_users').fetchone()[0]
            if admin_count == 0:
                create_default_admin(conn)
            
            conn.commit()
            logger.info("データベース初期化完了")
    except Exception as e:
        logger.error(f"データベース初期化エラー: {e}")
        raise

def ensure_db_initialized():
    """データベースの初期化を確実に実行"""
    try:
        # データベースファイルの存在確認
        if not os.path.exists(DATABASE):
            logger.info(f"データベースファイルが存在しません: {DATABASE}")
            init_db()
            logger.info("データベースを初期化しました")
            return
        
        # テーブル存在確認
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # contactsテーブルの確認
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='contacts'")
        contacts_exists = cursor.fetchone()
        
        # admin_usersテーブルの確認
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='admin_users'")
        admin_exists = cursor.fetchone()
        
        if not contacts_exists or not admin_exists:
            logger.info("必要なテーブルが存在しません。データベースを再初期化します")
            conn.close()
            init_db()
        else:
            # 管理者アカウントの存在確認
            cursor.execute("SELECT COUNT(*) FROM admin_users")
            admin_count = cursor.fetchone()[0]
            if admin_count == 0:
                logger.info("管理者アカウントが存在しません。作成します")
                create_default_admin(conn)
                conn.commit()
            
            conn.close()
            logger.info("データベースは正常に初期化済みです")
            
    except Exception as e:
        logger.error(f"データベース確認・初期化エラー: {e}")
        try:
            init_db()
        except Exception as init_error:
            logger.error(f"データベース初期化の再試行も失敗: {init_error}")

# アプリケーション起動時の必須初期化
try:
    ensure_db_initialized()
    logger.info("=== アプリケーション初期化完了 ===")
except Exception as e:
    logger.error(f"=== アプリケーション初期化エラー: {e} ===")

def send_email(to_email: str, subject: str, body: str) -> bool:
    """メール送信関数"""
    try:
        # デバッグモードの場合のみ詳細情報を出力
        if not IS_PRODUCTION:
            logger.debug("=== メール送信設定 ===")
            logger.debug(f"HOST: {EMAIL_HOST}")
            logger.debug(f"PORT: {EMAIL_PORT}")
            logger.debug(f"FROM: {EMAIL_FROM}")
            logger.debug(f"USER: {EMAIL_USER}")
            logger.debug(f"TO: {to_email}")

            # パスワードの形式をチェック
            if len(EMAIL_PASSWORD) != 16:
                logger.warning(f"アプリパスワードは通常16文字です。現在: {len(EMAIL_PASSWORD)}文字")

            if ' ' in EMAIL_PASSWORD:
                logger.warning("パスワードにスペースが含まれています。スペースを除去してください。")

        msg = MIMEMultipart()
        msg['From'] = EMAIL_FROM
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'html', 'utf-8'))

        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)

        # デバッグモードの場合のみSMTPデバッグを有効化
        if not IS_PRODUCTION:
            server.set_debuglevel(1)
            logger.debug("SMTP接続中...")

        server.starttls()

        if not IS_PRODUCTION:
            logger.debug("認証中...")

        server.login(EMAIL_USER, EMAIL_PASSWORD)

        if not IS_PRODUCTION:
            logger.debug("認証成功")

        server.send_message(msg)
        server.quit()

        logger.info(f"メール送信成功: {to_email}")
        return True
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"メール認証エラー: {e}")
        if not IS_PRODUCTION:
            logger.error("解決策:")
            logger.error("  1. Googleアカウントで2段階認証が有効か確認")
            logger.error("  2. 新しいアプリパスワードを生成")
            logger.error("  3. EMAIL_USERとEMAIL_PASSWORDが正確か確認")
            logger.error("  4. https://myaccount.google.com/apppasswords にアクセス")
        return False
    except Exception as e:
        logger.error(f"メール送信エラー: {e}")
        if not IS_PRODUCTION:
            logger.error(f"エラーの詳細: {type(e).__name__}")
        return False

# WTFormsのフォームクラスを定義
class LoginForm(FlaskForm):
    username = StringField('ユーザー名', validators=[DataRequired()])
    password = PasswordField('パスワード', validators=[DataRequired()])
    submit = SubmitField('ログイン')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('現在のパスワード', validators=[DataRequired()])
    new_password = PasswordField('新しいパスワード', validators=[DataRequired(), Length(min=6, message='パスワードは6文字以上である必要があります。')])
    confirm_password = PasswordField('新しいパスワード (確認)', validators=[DataRequired(), EqualTo('new_password', message='パスワードが一致しません。')])
    submit = SubmitField('パスワードを変更')

class ForgotPasswordForm(FlaskForm):
    username = StringField('ユーザー名', validators=[DataRequired()])
    email = StringField('メールアドレス', validators=[DataRequired(), Email(message='有効なメールアドレスを入力してください。')])
    security_answer = StringField('セキュリティ質問の答え', validators=[DataRequired()])
    submit = SubmitField('リセット要求を送信')

class ResetPasswordForm(FlaskForm):
    new_password = PasswordField('新しいパスワード', validators=[DataRequired(), Length(min=6, message='パスワードは6文字以上である必要があります。')])
    confirm_password = PasswordField('新しいパスワード (確認)', validators=[DataRequired(), EqualTo('new_password', message='パスワードが一致しません。')])
    submit = SubmitField('パスワードをリセット')

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
            logger.error(f"お問い合わせ処理エラー: {e}")
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

@app.route('/admin/forgot-password', methods=['GET', 'POST'])
def forgot_password() -> Union[str, WerkzeugResponse]:
    form = ForgotPasswordForm()
    
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        security_answer = form.security_answer.data
        
        conn = get_db()
        user = conn.execute(
            'SELECT * FROM admin_users WHERE username = ? AND email = ?',
            (username, email)
        ).fetchone()
        
        if user and check_password_hash(user['security_answer_hash'], security_answer):
            # トークンを生成
            token = secrets.token_urlsafe(32)
            tokyo_tz = pytz.timezone('Asia/Tokyo')
            current_time = datetime.datetime.now(tokyo_tz)
            expires_at = current_time + datetime.timedelta(hours=24)  # 24時間有効
            
            # トークンをデータベースに保存
            conn.execute(
                '''INSERT INTO password_reset_tokens 
                   (user_id, token, expires_at, created_at) VALUES (?, ?, ?, ?)''',
                (user['id'], token, expires_at, current_time)
            )
            conn.commit()
            
            # リセットメールを送信
            reset_url = url_for('reset_password', token=token, _external=True)
            email_body = f'''
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                    <h2 style="color: #0d6efd; text-align: center;">パスワードリセット</h2>
                    <p>こんにちは、{username}さん</p>
                    <p>パスワードのリセット要求を受け付けました。</p>
                    <p>以下のリンクをクリックして、新しいパスワードを設定してください：</p>
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{reset_url}" 
                           style="display: inline-block; padding: 12px 24px; background-color: #0d6efd; color: white; text-decoration: none; border-radius: 5px; font-weight: bold;">
                            パスワードをリセット
                        </a>
                    </div>
                    <p><strong>重要:</strong></p>
                    <ul>
                        <li>このリンクは24時間有効です</li>
                        <li>リンクは一度のみ使用可能です</li>
                        <li>心当たりがない場合は、このメールを無視してください</li>
                    </ul>
                    <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                    <p style="font-size: 12px; color: #666; text-align: center;">
                        このメールは自動送信されています。返信しないでください。
                    </p>
                </div>
            </body>
            </html>
            '''
            
            # 開発環境での代替手段：ログにURLを表示
            if not IS_PRODUCTION:
                logger.debug("=" * 80)
                logger.debug("パスワードリセット開発用情報")
                logger.debug(f"ユーザー: {username}")
                logger.debug(f"リセットURL: {reset_url}")
                logger.debug(f"トークン有効期限: {expires_at}")
                logger.debug("=" * 80)
            
            if send_email(email, 'パスワードリセット要求', email_body):
                flash('パスワードリセット用のメールを送信しました。メールをご確認ください。', 'success')
            else:
                flash(f'メール送信に失敗しました。開発環境の場合は、コンソールに表示されたURLを使用してください。<br>リセットURL: <a href="{reset_url}" target="_blank">{reset_url}</a>', 'error')
        else:
            flash('入力された情報に誤りがあります。再度確認してください。', 'error')
    
    return render_template('admin/forgot_password.html', form=form)

@app.route('/admin/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token: str) -> Union[str, WerkzeugResponse]:
    conn = get_db()
    tokyo_tz = pytz.timezone('Asia/Tokyo')
    current_time = datetime.datetime.now(tokyo_tz)
    
    # トークンの有効性を確認
    token_record = conn.execute(
        '''SELECT prt.*, au.username FROM password_reset_tokens prt
           JOIN admin_users au ON prt.user_id = au.id
           WHERE prt.token = ? AND prt.expires_at > ? AND prt.used = FALSE''',
        (token, current_time)
    ).fetchone()
    
    if not token_record:
        flash('無効または期限切れのリセットリンクです。', 'error')
        return redirect(url_for('forgot_password'))
    
    form = ResetPasswordForm()
    
    if form.validate_on_submit():
        new_password = form.new_password.data
        new_password_hash = generate_password_hash(new_password)
        
        # パスワードを更新
        conn.execute(
            'UPDATE admin_users SET password_hash = ? WHERE id = ?',
            (new_password_hash, token_record['user_id'])
        )
        
        # トークンを使用済みにマーク
        conn.execute(
            'UPDATE password_reset_tokens SET used = TRUE WHERE id = ?',
            (token_record['id'],)
        )
        
        conn.commit()
        
        flash('パスワードが正常にリセットされました。新しいパスワードでログインしてください。', 'success')
        return redirect(url_for('admin_login'))
    
    return render_template('admin/reset_password.html', form=form, username=token_record['username'])

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

# セキュリティ関連のユーティリティルート
@app.route('/admin/test-email', methods=['GET', 'POST'])
@login_required
def test_email() -> Union[str, FlaskResponse]:
    """メール送信テスト"""
    if request.method == 'POST':
        test_email = request.form.get('test_email', '')
        if test_email:
            result = send_email(
                test_email,
                'テストメール - パスワードリセット機能',
                '''
                <html>
                <body>
                    <h2>メール送信テスト</h2>
                    <p>このメールが届いていれば、メール送信機能は正常に動作しています。</p>
                    <p>パスワードリセット機能を安心してご利用ください。</p>
                </body>
                </html>
                '''
            )
            if result:
                flash('テストメールを送信しました。', 'success')
            else:
                flash('テストメールの送信に失敗しました。', 'error')
        else:
            flash('メールアドレスを入力してください。', 'error')
    
    # 設定値をテンプレートに渡す
    config = {
        'EMAIL_HOST': EMAIL_HOST,
        'EMAIL_PORT': EMAIL_PORT,
        'EMAIL_USER': EMAIL_USER,
        'EMAIL_PASSWORD': EMAIL_PASSWORD,
        'EMAIL_FROM': EMAIL_FROM
    }
    
    return render_template('admin/test_email.html', config=config)

@app.route('/admin/cleanup-tokens')
@login_required
def cleanup_expired_tokens() -> FlaskResponse:
    """期限切れのトークンをクリーンアップ"""
    conn = get_db()
    tokyo_tz = pytz.timezone('Asia/Tokyo')
    current_time = datetime.datetime.now(tokyo_tz)
    
    deleted = conn.execute(
        'DELETE FROM password_reset_tokens WHERE expires_at < ?',
        (current_time,)
    ).rowcount
    conn.commit()
    
    return jsonify({'deleted_tokens': deleted})

@app.errorhandler(404)
def not_found_error(error: Exception) -> tuple[str, int]:
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error: Exception) -> tuple[str, int]:
    return render_template('errors/500.html'), 500

# Gunicorn用のアプリケーションオブジェクト
# 本番環境では gunicorn app:app または gunicorn app:application として参照される
application = app

# ローカル開発時のみ実行（本番環境ではGunicornが直接app:appを読み込む）
if __name__ == '__main__':
    # ローカル開発サーバーの起動
    debug_mode = not IS_PRODUCTION
    port = int(os.getenv('PORT', 5000))  # ローカル開発では5000番ポート
    
    logger.info(f"ローカル開発サーバー起動 - Debug: {debug_mode}, Port: {port}")
    app.run(debug=debug_mode, host='0.0.0.0', port=port)