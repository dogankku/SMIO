import streamlit as st
import easyocr
import numpy as np
from PIL import Image
import pandas as pd

# Sayfa Ayarları
st.set_page_config(page_title="OCR Text Extractor", layout="wide")

st.title("📸 Screenshot to List (OCR Test)")
st.markdown("Ekran görüntüsünü yükle, metinleri ayıkla ve listeyi düzenle.")

# --- CACHING MEKANİZMASI ---
# EasyOCR modelini her seferinde tekrar yüklememek için bellekte tutuyoruz.
@st.cache_resource
def load_model():
    # Türkçe (tr) ve İngilizce (en) desteği
    return easyocr.Reader(['tr', 'en'], gpu=False) 

with st.spinner("AI Modeli Yükleniyor... (İlk açılışta biraz sürebilir)"):
    reader = load_model()

# --- ARAYÜZ ---
col1, col2 = st.columns([1, 2])

with col1:
    uploaded_file = st.file_uploader("Bir ekran görüntüsü yükle (PNG/JPG)", type=["png", "jpg", "jpeg"])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption='Yüklenen Görsel', use_column_width=True)
        
        process_btn = st.button("Metinleri Çıkar", type="primary")

with col2:
    if uploaded_file is not None and process_btn:
        with st.spinner('Görüntü işleniyor, metinler ayıklanıyor...'):
            try:
                # Pillow görselini Numpy array'e çevir (EasyOCR formatı için)
                image_np = np.array(image)
                
                # Okuma işlemi
                result = reader.readtext(image_np)
                
                # Sadece metinleri ve güven skorlarını alalım
                data = []
                for (bbox, text, prob) in result:
                    # Güven skoru %30'un altındaysa gürültü olabilir, almayabiliriz
                    if prob > 0.3: 
                        data.append({"Metin": text, "Güven Skoru": round(prob, 2)})
                
                # Veriyi Pandas DataFrame'e çevir
                df = pd.DataFrame(data)
                
                st.success(f"İşlem Tamamlandı! {len(df)} satır metin bulundu.")
                
                # --- DÜZENLENEBİLİR TABLO ---
                st.subheader("📝 Düzenlenebilir Liste")
                st.info("Aşağıdaki listede hatalı okunan yerleri düzeltebilir veya silebilirsin.")
                
                # st.data_editor ile kullanıcıya Excel gibi düzeltme imkanı veriyoruz
                edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
                
                # --- LİSTEYİ İNDİRME ---
                st.write("---")
                csv = edited_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Listeyi CSV Olarak İndir",
                    data=csv,
                    file_name='okunan_metinler.csv',
                    mime='text/csv',
                )
                
                # Bir sonraki aşama (Formatlama) için veriyi session state'e atabiliriz
                st.session_state['final_list'] = edited_df['Metin'].tolist()

            except Exception as e:
                st.error(f"Bir hata oluştu: {e}")

    elif uploaded_file is None:
        st.info("Başlamak için sol taraftan bir resim yükleyin.")
