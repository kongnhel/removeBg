import os
import base64
from flask import Flask, render_template, request, jsonify
from rembg import remove, new_session
from PIL import Image, ImageFilter
from io import BytesIO

app = Flask(__name__)

# 🧠 BEST overall model for people + hair
session = new_session("isnet-general-use")


def upscale_for_hair(img: Image.Image, scale: float = 1.8) -> Image.Image:
    """Upscale image before remove to preserve fine hair details"""
    w, h = img.size
    return img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)


def smooth_alpha_edges(img: Image.Image) -> Image.Image:
    """Light edge smoothing for hair"""
    alpha = img.split()[-1]
    alpha = alpha.filter(ImageFilter.GaussianBlur(radius=0.6))
    img.putalpha(alpha)
    return img


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/remove-background', methods=['POST'])
def remove_background_local():

    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No selected file'}), 400

    try:
        # 1️⃣ Load image
        input_image = Image.open(file.stream).convert("RGBA")

        # 2️⃣ Upscale for hair detail (IMPORTANT)
        input_image = upscale_for_hair(input_image, scale=1.8)

        # 3️⃣ Remove background (HAIR-TUNED SETTINGS 🔥)
        output_image = remove(
            input_image,
            session=session,
            alpha_matting=True,

            # 🎯 Hair-friendly tuning
            alpha_matting_foreground_threshold=235,
            alpha_matting_background_threshold=15,
            alpha_matting_erode_size=5
        )

        # 4️⃣ Smooth alpha edges (post-process)
        output_image = smooth_alpha_edges(output_image)

        # 5️⃣ Save to memory
        buffer = BytesIO()
        output_image.save(buffer, format="PNG")
        buffer.seek(0)

        # 6️⃣ Base64 for preview
        base64_img = base64.b64encode(buffer.read()).decode("utf-8")

        return jsonify({
            'success': True,
            'image_base64_png': f"data:image/png;base64,{base64_img}",
            'filename': f"perfect_hair_removed_{os.path.splitext(file.filename)[0]}.png"
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)
