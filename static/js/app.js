async function sendAnnouncement(event) {
  event.preventDefault();
  const form = event.target;
  const data = new FormData(form);

  const res = await fetch("/", {
    method: "POST",
    body: data
  });

  const text = await res.text();
  showToast((res.ok ? "✅ " : "❌ ") + text);
}

function showToast(msg) {
  const toast = document.getElementById("toast");
  toast.textContent = msg;
  toast.classList.add("show");
  setTimeout(() => toast.classList.remove("show"), 3000);
}

function updatePreview() {
  const text = document.getElementById("message").value;

  fetch("/preview", {
    method: "POST",
    headers: {"Content-Type": "application/x-www-form-urlencoded"},
    body: "text=" + encodeURIComponent(text)
  })
    .then(r => r.text())
    .then(html => {
      document.getElementById("preview").innerHTML = html || "<em>kosong</em>";
    });
}

