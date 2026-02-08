from flask import Flask, request, render_template
import requests, os
from markdown import markdown
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")
ADMIN_KEY = os.getenv("ADMIN_KEY", "admin123")

@app.route("/", methods=["GET", "POST"])
def announce():
    if request.method == "POST":
        if request.form.get("key") != ADMIN_KEY:
            return "Unauthorized", 403

        title = request.form.get("title", "").strip()
        body = request.form.get("message", "")
        content = f"# {title}\n{body}" if title else body

        image_file = request.files.get("image_file")

        try:
            if image_file and image_file.filename:
                files = {
                    "file": (
                        image_file.filename,
                        image_file.stream,
                        image_file.mimetype
                    )
                }
                data = {"content": content}
                r = requests.post(DISCORD_WEBHOOK, data=data, files=files)
            else:
                r = requests.post(DISCORD_WEBHOOK, json={"content": content})

            if r.status_code in (200, 204):
                return "Sent to Discord!"
            return f"Discord error: {r.text}", 500

        except Exception as e:
            return f"Error: {e}", 500

    return render_template("index.html")


@app.route("/preview", methods=["POST"])
def preview():
    text = request.form.get("text", "")
    return markdown(text)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

