async function getThumbnail() {
  const url = document.getElementById("ytLink").value.trim();
  const resDiv = document.getElementById("result");
  const titleH2 = document.getElementById("videoTitle");

  // Reset hiển thị
  titleH2.style.display = 'none';
  titleH2.textContent = '';

  if (!url) {
    resDiv.innerHTML = "<p class='error'>❌ Vui lòng nhập link YouTube</p>";
    return;
  }

  resDiv.innerHTML = "<p class='loading'>⏳ Đang xử lý và lấy metadata video...</p>";

  try {
    const res = await fetch("/get_thumbnail", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url }) // Không gửi size
    });

    const data = await res.json();
    let html = "";

    if (data.error) {
      html = `<p class='error'>${data.error}</p>`;
      resDiv.innerHTML = html;
      return;
    } 
    
    // 1. Hiển thị Tiêu đề Video (từ Pytube)
    titleH2.textContent = data.title;
    titleH2.style.display = 'block';

    // 2. Chuẩn bị hiển thị TẤT CẢ Thumbnails
    const thumbnails = data.thumbnails;

    html = `<div class="box"><h3>Tất cả kích thước Thumbnail (Chuẩn)</h3>`;
    
    // Giải thích cho người dùng về ảnh thử nghiệm
    html += `<p style="color:#555; font-size:14px;">
        *Lưu ý quan trọng: YouTube KHÔNG công khai ảnh Thử nghiệm (A/B testing) qua các công cụ.
        Chúng tôi hiển thị TẤT CẢ các kích thước ảnh chuẩn của video mà YouTube cung cấp.
        </p>`;

    thumbnails.forEach(thumb => {
        // Tạo box cho từng thumbnail
        html += `<div style="margin-top: 20px; border: 1px solid #eee; padding: 15px; border-radius: 8px;">
                    <h4>${thumb.description} (${thumb.quality})</h4>
                    <img src="${thumb.url}" alt="Thumbnail ${thumb.quality}"><br>
                    <a href="${thumb.url}" download>⬇️ Tải ảnh (${thumb.description})</a>
                </div>`;
    });

    html += `</div>`;
    resDiv.innerHTML = html;

  } catch (error) {
    console.error(error);
    resDiv.innerHTML = "<p class='error'>⚠️ Lỗi kết nối hoặc xử lý dữ liệu.</p>";
  }
}