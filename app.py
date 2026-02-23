import os
import io
from datetime import datetime
from flask import Flask, render_template, request, send_file
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)

# Base Directory handling
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_font(font_name, size):
    """Unga static/fonts folder-la irunthu fonts-ah load panna"""
    # Filename exactly match aaganum (Case Sensitive)
    font_path = os.path.join(BASE_DIR, 'static', 'fonts', font_name)
    try:
        if os.path.exists(font_path):
            return ImageFont.truetype(font_path, size)
        else:
            # Local testing fallback
            return ImageFont.truetype("arial.ttf", size)
    except:
        return ImageFont.load_default()

def generate_thumbnail(data):
    # --- 1. CANVAS SETTINGS ---
    width, height = 1280, 720
    margin_x = 95 

    # --- 2. BACKGROUND ---
    bg_img_path = os.path.join(BASE_DIR, 'static', 'images', 'pg.png')
    try:
        base = Image.open(bg_img_path).convert("RGB")
        base = base.resize((width, height), Image.Resampling.LANCZOS)
    except:
        base = Image.new("RGB", (width, height), (15, 23, 42))

    # Clean Gradient Overlay
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw_ov = ImageDraw.Draw(overlay)
    for i in range(int(width * 0.65)):
        alpha = int(235 * (1 - (i / (width * 0.6))))
        draw_ov.line([(i, 0), (i, height)], fill=(0, 0, 0, max(0, alpha)))
    base.paste(overlay, (0, 0), overlay)
    
    draw = ImageDraw.Draw(base)

    # --- 3. FONTS (Unga folder-la irukura names-ah use panren) ---
    f_brand = get_font("ARIALBD.TTF", 34)
    f_year = get_font("ARIALBD.TTF", 40)
    f_main = get_font("ARIALBD.TTF", 88)   # Neet and balanced
    f_sub1 = get_font("ARIAL.TTF", 48)
    f_sub2 = get_font("ARIALBD.TTF", 100)  # Professional Part size
    f_web = get_font("ARIAL.TTF", 24)

    # --- 4. DESIGN ---

    # A. Brand Label
    draw.rectangle([0, 60, 420, 120], fill=(255, 255, 255)) 
    draw.rectangle([0, 60, 15, 120], fill=(255, 204, 0))
    draw.text((45, 72), data['brand_text'].upper(), font=f_brand, fill=(15, 23, 42))

    # B. Year Badge
    year_txt = data['year_val'].upper()
    tw = draw.textlength(year_txt, font=f_year)
    draw.rounded_rectangle([width - tw - 100, 60, width - 40, 125], radius=32, fill=(255, 204, 0))
    draw.text((width - tw - 70, 72), year_txt, font=f_year, fill=(0, 0, 0))

    # C. Typography Spacing
    def draw_neat_text(pos, text, font, fill):
        draw.text((pos[0]+3, pos[1]+3), text, font=font, fill=(0,0,0,130))
        draw.text(pos, text, font=font, fill=fill)

    # Headlines
    draw_neat_text((margin_x, 230), data['main_1'], f_main, "white")
    draw_neat_text((margin_x, 335), data['main_2'], f_main, "white")

    # D. Sub-details
    draw.text((margin_x, 485), data['sub_1'], font=f_sub1, fill=(215, 215, 215))
    
    # Yellow PART Highlight
    draw_neat_text((margin_x, 555), data['sub_2'], f_sub2, (255, 204, 0))

    # E. Footer
    draw.text((margin_x, 685), data['web_site'].lower(), font=f_web, fill=(160, 160, 160))

    # --- 5. EXPORT ---
    img_io = io.BytesIO()
    base.save(img_io, 'PNG', quality=100)
    img_io.seek(0)
    return img_io

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    user_inputs = {
        'brand_text': request.form.get('brand', 'VEL INSTITUTE'),
        'year_val': request.form.get('year', 'FEB 2026'),
        'main_1': request.form.get('main1', 'Ramsar Sites'),
        'main_2': request.form.get('main2', 'Current Affairs'),
        'sub_1': request.form.get('sub1', 'Full Coverage'),
        'sub_2': request.form.get('sub2', 'PART-1'),
        'web_site': request.form.get('web', 'www.vasanth.com')
    }
    img_buffer = generate_thumbnail(user_inputs)
    timestamp = datetime.now().strftime("%d-%m-%Y_%I.%M %p")
    return send_file(img_buffer, mimetype='image/png', as_attachment=True, download_name=f"TN_{timestamp}.png")

if __name__ == '__main__':
    app.run(debug=True)