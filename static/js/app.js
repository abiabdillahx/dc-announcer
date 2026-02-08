async function sendAnnouncement(event) {
  event.preventDefault();
  const form = event.target;
  const data = new FormData(form);

  const res = await fetch("/send", {
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
  const previewTextElement = document.getElementById("preview-text"); // New element for markdown preview

  fetch("/preview", {
    method: "POST",
    headers: {"Content-Type": "application/x-www-form-urlencoded"},
    body: "text=" + encodeURIComponent(text)
  })
    .then(r => r.text())
    .then(html => {
      previewTextElement.innerHTML = html || "<em>Preview markdown akan muncul di sini…</em>"; // Update to use previewTextElement
    });
}

function previewImage(event) {
  const reader = new FileReader();
  const imageElement = document.getElementById("preview-image");
  const file = event.target.files[0];

  if (file) {
    reader.onload = function(e) {
      imageElement.src = e.target.result;
      imageElement.hidden = false;
    };
    reader.readAsDataURL(file);
  } else {
    imageElement.src = "";
    imageElement.hidden = true;
  }
}