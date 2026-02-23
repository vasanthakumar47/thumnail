import os
import io
from datetime import datetime
from flask import Flask, render_template, request, send_file
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)

def generate_thumbnail(data):
    # --- 1. SETTINGS ---
    width, height = 1280, 720
    margin_x = 90 

    # --- 2. BACKGROUND ---
    bg_img_path = os.path.join(os.path.dirname(__file__), 'static', 'images', 'pg.png')
    try:
        base = Image.open(bg_img_path).convert("RGB")
        base = base.resize((width, height), Image.Resampling.LANCZOS)
    except:
        base = Image.new("RGB", (width, height), (15, 23, 42))

    # Professional Smooth Gradient for Text Base
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw_ov = ImageDraw.Draw(overlay)
    for i in range(int(width * 0.65)):
        alpha = int(230 * (1 - (i / (width * 0.6))))
        draw_ov.line([(i, 0), (i, height)], fill=(0, 0, 0, max(0, alpha)))
    base.paste(overlay, (0, 0), overlay)
    
    draw = ImageDraw.Draw(base)

    # --- 3. FONTS (Refined Sizes) ---
    try:
        f_brand = ImageFont.truetype("arialbd.ttf", 34)
        f_year = ImageFont.truetype("arialbd.ttf", 40)
        f_main = ImageFont.truetype("arialbd.ttf", 90)  # Neet & Balanced
        f_sub1 = ImageFont.truetype("arial.ttf", 48)
        f_sub2 = ImageFont.truetype("arialbd.ttf", 100) # Professional Size
        f_web = ImageFont.truetype("arial.ttf", 24)
    except:
        f_main = f_year = f_sub1 = f_sub2 = f_brand = f_web = ImageFont.load_default()

    # --- 4. PROFESSIONAL DESIGN ELEMENTS ---

    # A. Clean Brand Label (Left Top)
    draw.rectangle([0, 60, 420, 120], fill=(255, 255, 255)) 
    draw.rectangle([0, 60, 15, 120], fill=(255, 204, 0))
    draw.text((45, 72), data['brand_text'].upper(), font=f_brand, fill=(15, 23, 42))

    # B. Year Badge (Clean Pill - Right Top)
    year_txt = data['year_val'].upper()
    tw = draw.textlength(year_txt, font=f_year)
    draw.rounded_rectangle([width - tw - 100, 60, width - 40, 125], radius=32, fill=(255, 204, 0))
    draw.text((width - tw - 70, 72), year_txt, font=f_year, fill=(0, 0, 0))

    # C. Typography (Sharp & Balanced)
    def draw_neat_text(pos, text, font, fill):
        # Very subtle shadow for high-end look
        draw.text((pos[0]+3, pos[1]+3), text, font=font, fill=(0,0,0,120))
        draw.text(pos, text, font=font, fill=fill)

    # Main Headlines (Line Spacing Adjusted)
    draw_neat_text((margin_x, 230), data['main_1'], f_main, "white")
    draw_neat_text((margin_x, 335), data['main_2'], f_main, "white")

    # D. Sub-details & PART-1
    draw.text((margin_x, 480), data['sub_1'], font=f_sub1, fill=(210, 210, 210))
    
    # Balanced PART Highlight
    draw_neat_text((margin_x, 550), data['sub_2'], f_sub2, (255, 204, 0))

    # E. Minimal Footer (No Line, Just Text)
    draw.text((margin_x, 680), data['web_site'].lower(), font=f_web, fill=(160, 160, 160))

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
    return send_file(img_buffer, mimetype='image/png', as_attachment=True, download_name=f"VEL INSTITUTE THUMBNAIL_{timestamp}.png")

if __name__ == '__main__':
    app.run(debug=True)