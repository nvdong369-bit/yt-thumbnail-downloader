async function getThumbnail() {
    const url = document.getElementById("ytLink").value.trim();
    const resDiv = document.getElementById("result");
    const titleH2 = document.getElementById("videoTitle");

    // Xóa kết quả cũ
    resDiv.innerHTML = "";
    titleH2.innerText = "";
    titleH2.style.display = 'none';

    if (!url) {
        resDiv.innerHTML = "<p class='error'>❌ Vui lòng nhập link YouTube</p>";
        return;
    }

    resDiv.innerHTML = "<p class='loading'>⏳ Đang xử lý, vui lòng chờ...</p>";

    try {
        const res = await fetch("/get_thumbnail", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            // Chỉ gửi URL
            body: JSON.stringify({ url }) 
        });

        const data = await res.json();
        let html = "";

        if (data.error) {
            html = `<p class='error'>${data.error}</p>`;
        } else if (data.thumbnails) {
            // Hiển thị Tiêu đề video
            if (data.title && data.title !== "⚠️ Lỗi: Không thể lấy Tiêu đề (Video Private/Không tồn tại)") {
                 titleH2.innerText = data.title;
                 titleH2.style.display = 'block';
            } else {
                 titleH2.innerText = data.title; // Hiển thị thông báo lỗi Tiêu đề
                 titleH2.style.color = 'red';
                 titleH2.style.display = 'block';
            }

            // Xây dựng HTML cho TẤT CẢ thumbnails
            data.thumbnails.forEach(thumb => {
                // Chỉ hiển thị các ảnh chuẩn theo tên (maxres, sd, hq, mq, default)
                if (['maxres', 'sd', 'hq', 'mq', 'default'].includes(thumb.quality)) {
                    html += `
                        <div class="box thumbnail-box">
                            <h3>${thumb.description}</h3>
                            <div class="thumb-preview">
                                <img src="${thumb.url}" alt="Thumbnail ${thumb.quality}" loading="lazy">
                            </div>
                            <p class="download-link">
                                <a href="${thumb.url}" download="${data.title || 'thumbnail'}_${thumb.quality}.jpg">
                                    ⬇️ Tải ảnh (${thumb.quality})
                                </a>
                            </p>
                        </div>
                    `;
                }
            });
            
            // Nếu không có ảnh nào được hiển thị
            if (html === "") {
                html = "<p class='error'>⚠️ Không tìm thấy ảnh thumbnail tiêu chuẩn nào.</p>";
            }
        }

        resDiv.innerHTML = html;

    } catch (e) {
        console.error(e);
        resDiv.innerHTML = "<p class='error'>⚠️ Lỗi kết nối hoặc xử lý dữ liệu server</p>";
    }
}