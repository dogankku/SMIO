import streamlit as st
import easyocr
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import textwrap

# Sayfa Ayarları
st.set_page_config(page_title="Social Media Content Factory", layout="wide")

st.title("🏭 Social Media Content Factory")
st.markdown("1. Adım: Ekran görüntüsünü yükle ve metni al.\n2. Adım: Tasarımı yap ve paylaş.")

# --- FONKSİYONLAR ---

@st.cache_resource
def load_ocr_model():
    return easyocr.Reader(['tr', 'en'], gpu=False)

def create_social_image(text, format_type, bg_color, text_color, font_size, font_file):
    # 1. Tuval Boyutları
    if format_type == "Instagram Post (1:1)":
        width, height = 1080, 1080
    elif format_type == "Instagram Story (9:16)":
        width, height = 1080, 1920
    else: # YouTube Thumbnail
        width, height = 1280, 720
        
    # 2. Tuval Oluştur
    img = Image.new('RGB', (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)
    
    # 3. Font Ayarlama
    try:
        if font_file is not None:
            font = ImageFont.truetype(font_file, font_size)
        else:
            # Font yüklenmezse varsayılanı kullan (biraz küçük olabilir)
            font = ImageFont.load_default()
    except Exception as e:
        st.error(f"Font hatası: {e}")
        font = ImageFont.load_default()

    # 4. Metni Satırlara Bölme (Text Wrapping)
    # Genişliğe göre ortalama karakter sayısını tahmin et (basit bir mantıkla)
    char_per_line = int(width / (font_size * 0.6)) 
    lines = textwrap.wrap(text, width=char_per_line)
    
    # 5. Metni Ortalamak İçin Hesaplama
    # Toplam metin bloğunun yüksekliğini hesapla
    # getbbox yerine getsize kullanımı (eski pillow sürümleri için gerekebilir ama bbox daha modern)
    total_text_height = 0
    line_heights = []
    
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        h = bbox[3] - bbox[1]
        line_heights.append(h)
        total_text_height += h + 10 # 10px satır arası boşluk

    current_y = (height - total_text_height) / 2
    
    # 6. Metni Yazdır
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        line_width = bbox[2] - bbox[0]
        x_pos = (width - line_width) / 2
        
        draw.text((x_pos, current_y), line, font=font, fill=text_color)
        current_y += line_heights[i] + 10
        
    return img

# --- ARAYÜZ ---

# Sol Panel: Yükleme ve OCR
with st.sidebar:
    st.header("1. Veri Kaynağı")
    uploaded_file = st.file_uploader("Ekran Görüntüsü Yükle", type=["png", "jpg", "jpeg"])
    
    # Font Yükleme (Opsiyonel ama Önemli)
    st.info("Daha şık görünüm için bilgisayarından bir .ttf (Font) dosyası yükleyebilirsin.")
    uploaded_font = st.file_uploader("Font Dosyası (.ttf)", type=["ttf"])

    if uploaded_file is not None:
        st.image(uploaded_file, caption='Kaynak Görsel', use_column_width=True)
        if st.button("Metinleri Tara", type="primary"):
            with st.spinner('Yazılar okunuyor...'):
                reader = load_ocr_model()
                image_np = np.array(Image.open(uploaded_file))
                result = reader.readtext(image_np)
                
                # Güvenilir sonuçları al
                extracted_texts = [text for (bbox, text, prob) in result if prob > 0.3]
                st.session_state['ocr_results'] = extracted_texts
                st.success("Tarama Bitti!")

# Ana Panel: Düzenleme ve Önizleme
if 'ocr_results' in st.session_state:
    st.header("2. İçerik Tasarımı")
    
    col_edit, col_preview = st.columns([1, 1])
    
    with col_edit:
        st.subheader("İçerik Ayarları")
        
        # Hangi metni görselleştireceğiz?
        selected_text = st.selectbox("Listeden Metin Seç", st.session_state['ocr_results'])
        custom_text = st.text_area("Metni Düzenle", value=selected_text, height=100)
        
        st.markdown("---")
        st.subheader("Görsel Ayarları")
        
        format_type = st.radio("Boyut", ["Instagram Post (1:1)", "Instagram Story (9:16)", "YouTube Thumbnail (16:9)"])
        bg_color = st.color_picker("Arka Plan Rengi", "#1E1E1E")
        text_color = st.color_picker("Yazı Rengi", "#FFFFFF")
        font_size = st.slider("Yazı Boyutu", 20, 150, 60)
        
        generate_btn = st.button("Tasarımı Oluştur / Güncelle")

    with col_preview:
        st.subheader("Önizleme")
        if generate_btn or 'generated_image' in st.session_state:
            # Görüntüyü oluştur
            final_img = create_social_image(
                custom_text, 
                format_type, 
                bg_color, 
                text_color, 
                font_size, 
                uploaded_font
            )
            
            # Ekrana bas
            st.image(final_img, caption="Oluşturulan İçerik", use_column_width=True)
            
            # İndirme Butonu
            import io
            buf = io.BytesIO()
            final_img.save(buf, format="PNG")
            byte_im = buf.getvalue()
            
            st.download_button(
                label="🖼️ Görseli İndir",
                data=byte_im,
                file_name="social_post.png",
                mime="image/png"
            )

else:
    st.info("👈 Başlamak için sol menüden bir resim yükle ve 'Metinleri Tara' butonuna bas.")
