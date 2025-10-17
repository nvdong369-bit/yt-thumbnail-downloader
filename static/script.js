async function getThumbnail() {
  const url = document.getElementById("ytLink").value.trim();
  const size = document.getElementById("size").value;
  const resDiv = document.getElementById("result");

  if (!url) {
    resDiv.innerHTML = "<p class='error'>❌ Vui lòng nhập link YouTube</p>";
    return;
  }

  resDiv.innerHTML = "<p class='loading'>⏳ Đang xử lý...</p>";

  try {
    const res = await fetch("/get_thumbnail", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url, size })
    });

    const data = await res.json();
    let html = "";

    if (data.error) {
      html = `<p class='error'>${data.error}</p>`;
    } else if (data.thumbnail_url) {
      html = `<div class="box"><h3>Thumbnail</h3>
              <img src="${data.thumbnail_url}" alt="Thumbnail"><br>
              <a href="${data.thumbnail_url}" download>⬇️ Tải thumbnail</a></div>`;
    }

    resDiv.innerHTML = html;
  } catch {
    resDiv.innerHTML = "<p class='error'>⚠️ Lỗi kết nối server</p>";
  }
}