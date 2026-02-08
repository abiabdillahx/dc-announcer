import os
import requests
from flask import Flask, render_template, request
from flask_login import LoginManager, login_required
from markdown import markdown

from models import db, User
from auth import auth_bp

# ======================================================
# App init
# ======================================================

app = Flask(__name__)

# ---------- ENV ----------
app.secret_key = os.getenv("SECRET_KEY")

DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

# ======================================================
# Database (Flask-native instance path)
# ======================================================

# Pastikan instance folder ada (WAJIB di Docker)
os.makedirs(app.instance_path, exist_ok=True)

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    db_path = os.path.join(app.instance_path, "app.db")
    DATABASE_URL = f"sqlite:///{db_path}"

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# ======================================================
# Login manager
# ======================================================

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ======================================================
# Blueprints
# ======================================================

app.register_blueprint(auth_bp)

# ======================================================
# Routes
# ======================================================

@app.route("/")
@login_required
def announce():
    return render_template("announce.html")


@app.route("/send", methods=["POST"])
@login_required
def send():
    if not DISCORD_WEBHOOK:
        return "DISCORD_WEBHOOK not set", 500

    title = request.form.get("title", "").strip()
    msg = request.form.get("message", "").strip()

    content = f"# {title}\n{msg}" if title else msg

    data = {
        "content": content
    }

    files = None

    # ===== IMAGE OPTIONAL =====
    if "image_file" in request.files:
        img = request.files["image_file"]

        if img and img.filename:
            files = {
                "file": (img.filename, img.stream, img.mimetype)
            }

    # ===== SEND TO DISCORD =====
    r = requests.post(
        DISCORD_WEBHOOK,
        data=data,
        files=files,
        timeout=10
    )

    return ("OK", 200) if r.status_code in (200, 204) else ("FAIL", 500)


@app.route("/preview", methods=["POST"])
@login_required
def preview():
    text = request.form.get("text", "")
    return markdown(text)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


# ======================================================
# Bootstrap DB + Admin (RUN ONCE)
# ======================================================

def bootstrap():
    db.create_all()

    if not User.query.first():
        admin = User.create_admin(ADMIN_USERNAME, ADMIN_PASSWORD)
        db.session.add(admin)
        db.session.commit()
        print("[+] Admin user created")
    else:
        print("[*] Admin already exists")


# ======================================================
# Main
# ======================================================

if __name__ == "__main__":
    with app.app_context():
        bootstrap()

    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", 5000)),
        debug=os.getenv("FLASK_DEBUG", "false").lower() == "true"
    )

