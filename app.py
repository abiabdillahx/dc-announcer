from flask import Flask, request, render_template_string
import requests, os
from markdown import markdown

app = Flask(__name__)
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")
ADMIN_KEY = os.getenv("ADMIN_KEY", "admin123")

HTML_FORM = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Discord Announcement Panel</title>
<style>
  :root {
    --primary: #2563eb;
    --primary-dark: #1d4ed8;
    --bg: #f3f4f6;
    --card: #ffffff;
    --text: #1f2937;
    --border: #e5e7eb;
  }

  * {
    box-sizing: border-box;
  }

  body {
    font-family: 'Inter', sans-serif;
    background: var(--bg);
    margin: 0;
    padding: 0;
    color: var(--text);
  }

  .container {
    max-width: 720px;
    margin: 3em auto;
    background: var(--card);
    padding: 2.5em;
    border-radius: 12px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
  }

  h2 {
    text-align: center;
    margin-bottom: 1em;
  }

  input, textarea, button {
    width: 100%;
    font-size: 1em;
    margin: 0.5em 0;
    padding: 0.7em;
    border-radius: 8px;
    border: 1px solid var(--border);
  }

  input:focus, textarea:focus {
    outline: none;
    border-color: var(--primary);
    box-shadow: 0 0 0 2px rgba(37,99,235,0.2);
  }

  button {
    background: var(--primary);
    color: white;
    border: none;
    cursor: pointer;
    transition: 0.2s;
    font-weight: 600;
  }

  button:hover { background: var(--primary-dark); }

  h3 {
    margin-top: 2em;
    border-bottom: 2px solid var(--border);
    padding-bottom: 0.3em;
  }

  /* Markdown Preview Container */
  .preview {
    background: #f9fafb;
    padding: 1em 1.2em;
    border-radius: 8px;
    min-height: 80px;
    border: 1px solid var(--border);
    overflow-x: auto;
    word-wrap: break-word;
    overflow-wrap: anywhere;
    max-width: 100%;
    color: #111827;
  }

  .preview h1, .preview h2, .preview h3,
  .preview p, .preview ul, .preview ol {
    margin: 0.4em 0;
  }

  .preview pre {
    background: #1e293b;
    color: #f8fafc;
    padding: 0.6em;
    border-radius: 6px;
    overflow-x: auto;
  }

  .preview code {
    background: #e2e8f0;
    padding: 2px 4px;
    border-radius: 4px;
    font-family: monospace;
  }

  .preview img {
    max-width: 100%;
    height: auto;
    border-radius: 6px;
  }

  /* Toast */
  #toast {
    visibility: hidden;
    min-width: 250px;
    background-color: #333;
    color: #fff;
    text-align: center;
    border-radius: 8px;
    padding: 12px;
    position: fixed;
    z-index: 9999;
    left: 50%;
    bottom: 30px;
    transform: translateX(-50%);
    font-size: 16px;
    opacity: 0;
    transition: opacity 0.5s, bottom 0.5s;
  }

  #toast.show {
    visibility: visible;
    opacity: 1;
    bottom: 50px;
  }

  /* Responsive */
  @media (max-width: 768px) {
    .container {
      margin: 1em;
      padding: 1.5em;
    }
  }
</style>
<script>
async function sendAnnouncement(event) {
  event.preventDefault();
  const form = event.target;
  const data = new FormData(form);

  const res = await fetch("/", { method: "POST", body: data });
  const text = await res.text();

  if (res.ok) showToast("✅ " + text);
  else showToast("❌ " + text);
}

function showToast(msg) {
  const toast = document.getElementById("toast");
  toast.textContent = msg;
  toast.className = "show";
  setTimeout(() => toast.className = toast.className.replace("show", ""), 3500);
}

function updatePreview() {
  const text = document.getElementById("message").value;
  fetch("/preview", {
    method: "POST",
    headers: {"Content-Type": "application/x-www-form-urlencoded"},
    body: "text=" + encodeURIComponent(text)
  })
  .then(r => r.text())
  .then(html => document.getElementById("preview").innerHTML = html);
}
</script>
</head>
<body>
  <div class="container">
    <h2>📢 Discord Announcement Panel</h2>
    <form method="POST" onsubmit="sendAnnouncement(event)">
      <input type="password" name="key" placeholder="Admin Key" required>
      <input name="title" placeholder="Judul Announcement" required>
      <textarea id="message" name="message" placeholder="Tulis pesan (Markdown supported)" oninput="updatePreview()"></textarea>
      <button type="submit">Send</button>
    </form>

    <h3>Markdown Preview</h3>
    <div id="preview" class="preview"><em>kosong</em></div>
  </div>

  <div id="toast"></div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def announce():
    if request.method == "POST":
        if request.form["key"] != ADMIN_KEY:
            return "Unauthorized", 403

        title = request.form["title"]
        message = request.form["message"]
        msg = { "content": f"# {title} \n{message}" }
        try:
            r = requests.post(DISCORD_WEBHOOK, json=msg)
            return f"Sent to Discord! ({r.status_code})"
        except Exception as e:
            return f"Error: {e}", 500
    return render_template_string(HTML_FORM)

@app.route("/preview", methods=["POST"])
def preview():
    text = request.form.get("text", "")
    html = markdown(text)
    return html

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

