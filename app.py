import streamlit as st
from PIL import Image
import easyocr
from templates import get_template_list, apply_template, ALL_TEMPLATES

# Sayfa yapılandırması

st.set_page_config(
page_title=“📸 OCR Sosyal Medya Otomasyon”,
page_icon=“📸”,
layout=“wide”
)

# Custom CSS

st.markdown(”””

<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
    .template-preview {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>

“””, unsafe_allow_html=True)

# Başlık

st.markdown(’<div class="main-header">📸 OCR Sosyal Medya Otomasyon</div>’, unsafe_allow_html=True)
st.markdown(’<div class="sub-header">Görsel'den Metne - Profesyonel Sosyal Medya Formatları</div>’, unsafe_allow_html=True)
st.markdown(”—”)

# Session state’i başlat

if ‘extracted_text’ not in st.session_state:
st.session_state.extracted_text = “”
if ‘list_items’ not in st.session_state:
st.session_state.list_items = []
if ‘formatted_text’ not in st.session_state:
st.session_state.formatted_text = “”

# OCR okuyucusunu önbelleğe al

@st.cache_resource
def load_ocr_reader():
“”“EasyOCR okuyucusunu yükle (Türkçe ve İngilizce)”””
with st.spinner(“OCR modeli yükleniyor… (İlk seferde birkaç dakika sürebilir)”):
return easyocr.Reader([‘tr’, ‘en’], gpu=False)

# Ana uygulama - 3 Kolon Layout

col1, col2, col3 = st.columns([1, 1, 1.2])

# SOL KOLON - Görsel Yükleme ve OCR

with col1:
st.markdown(”### 1️⃣ Görsel Yükle”)

```
uploaded_file = st.file_uploader(
    "Ekran görüntüsü seçin",
    type=['png', 'jpg', 'jpeg'],
    help="PNG, JPG veya JPEG formatında görsel yükleyin"
)

if uploaded_file:
    # Görseli göster
    image = Image.open(uploaded_file)
    st.image(image, caption="Yüklenen Görsel", use_container_width=True)
    
    # OCR işlemi
    if st.button("🔍 Metni Çıkar", type="primary"):
        with st.spinner("Metin çıkarılıyor..."):
            try:
                reader = load_ocr_reader()
                result = reader.readtext(uploaded_file.getvalue())
                
                # Metni birleştir
                extracted_text = "\n".join([text[1] for text in result])
                st.session_state.extracted_text = extracted_text
                
                # Satırlara böl ve temizle
                lines = [line.strip() for line in extracted_text.split('\n') if line.strip()]
                st.session_state.list_items = lines
                
                st.success(f"✅ {len(lines)} madde tespit edildi!")
                
            except Exception as e:
                st.error(f"❌ Hata: {str(e)}")

# Manuel metin girişi
st.markdown("---")
st.markdown("### ✏️ Manuel Giriş")
manual_text = st.text_area(
    "Her satıra bir madde:",
    height=150,
    placeholder="Madde 1\nMadde 2\nMadde 3...",
    help="Enter tuşuyla yeni madde ekleyin"
)

if st.button("📝 Manuel Listeyi Kullan"):
    if manual_text:
        lines = [line.strip() for line in manual_text.split('\n') if line.strip()]
        st.session_state.list_items = lines
        st.session_state.extracted_text = manual_text
        st.success(f"✅ {len(lines)} madde eklendi!")
    else:
        st.warning("⚠️ Lütfen metin girin")
```

# ORTA KOLON - Liste Düzenleme ve Format Seçimi

with col2:
st.markdown(”### 2️⃣ Düzenle ve Format Seç”)

```
if st.session_state.list_items:
    # Liste önizleme
    with st.expander("📋 Çıkarılan Maddeler", expanded=True):
        for i, item in enumerate(st.session_state.list_items, 1):
            st.text(f"{i}. {item}")
        
        st.caption(f"Toplam {len(st.session_state.list_items)} madde")
    
    # Düzenleme seçeneği
    st.markdown("---")
    edit_mode = st.checkbox("✏️ Maddeleri Düzenle", value=False)
    
    if edit_mode:
        edited_text = st.text_area(
            "Düzenleyin:",
            value="\n".join(st.session_state.list_items),
            height=200,
            help="Her satıra bir madde gelecek şekilde düzenleyin"
        )
        if st.button("💾 Değişiklikleri Kaydet", type="primary"):
            lines = [line.strip() for line in edited_text.split('\n') if line.strip()]
            st.session_state.list_items = lines
            st.success("✅ Kaydedildi!")
            st.rerun()
    
    st.markdown("---")
    
    # Platform seçimi
    st.markdown("### 🎨 Platform Seç")
    platforms = list(ALL_TEMPLATES.keys())
    selected_platform = st.selectbox(
        "Platform:",
        platforms,
        help="Hangi platform için format oluşturacaksınız?"
    )
    
    # Platform'a göre şablonlar
    platform_templates = ALL_TEMPLATES[selected_platform]
    template_names = [f"{data['emoji']} {data['name']}" 
                     for data in platform_templates.values()]
    template_keys = list(platform_templates.keys())
    
    selected_template_index = st.selectbox(
        "Format Şablonu:",
        range(len(template_names)),
        format_func=lambda x: template_names[x],
        help="Oluşturmak istediğiniz formatı seçin"
    )
    
    selected_template_key = template_keys[selected_template_index]
    
    # Başlık girişi
    st.markdown("---")
    custom_title = st.text_input(
        "📌 Başlık (opsiyonel):",
        placeholder="Örn: Bugünün En İyi 10 Tavsiyesi",
        help="Boş bırakırsanız varsayılan başlık kullanılır"
    )
    
    # Format oluştur butonu
    if st.button("🎯 Formatı Oluştur", type="primary"):
        title = custom_title if custom_title else "📋 Liste"
        
        formatted = apply_template(
            selected_platform,
            selected_template_key,
            st.session_state.list_items,
            title
        )
        
        if formatted:
            st.session_state.formatted_text = formatted
            st.session_state.selected_platform = selected_platform
            st.session_state.selected_template = platform_templates[selected_template_key]['name']
            st.success("✅ Format oluşturuldu!")
        else:
            st.error("❌ Format oluşturulamadı")

else:
    st.info("👈 Önce bir görsel yükleyin veya manuel metin girin")
```

# SAĞ KOLON - Sonuç ve İndirme

with col3:
st.markdown(”### 3️⃣ Sonuç”)

```
if st.session_state.formatted_text:
    # Platform ve şablon bilgisi
    if hasattr(st.session_state, 'selected_platform'):
        st.success(f"📱 Platform: **{st.session_state.selected_platform}**")
        st.info(f"🎨 Şablon: **{st.session_state.selected_template}**")
    
    st.markdown("---")
    
    # Karakter sayısı
    char_count = len(st.session_state.formatted_text)
    st.caption(f"📊 Karakter sayısı: {char_count}")
    
    # Önizleme
    st.markdown("### ✨ Önizleme")
    st.text_area(
        "Kopyalamak için tıklayın:",
        value=st.session_state.formatted_text,
        height=400,
        label_visibility="collapsed"
    )
    
    # Butonlar
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        # İndirme butonu
        st.download_button(
            label="📥 TXT İndir",
            data=st.session_state.formatted_text,
            file_name=f"sosyal_medya_format_{st.session_state.selected_platform.lower()}.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    with col_btn2:
        # Temizle butonu
        if st.button("🗑️ Temizle", use_container_width=True):
            st.session_state.formatted_text = ""
            st.rerun()
    
    st.markdown("---")
    
    # Paylaşım ipuçları
    with st.expander("💡 Paylaşım İpuçları"):
        platform = st.session_state.selected_platform
        
        if platform == "Instagram":
            st.markdown("""
            **Instagram için:**
            - Story için maksimum 2200 karakter
            - Post'ta ilk 125 karakter önizlemede görünür
            - Hashtag'leri caption'ın sonuna ekleyin
            - Emojiler etkileşimi artırır
            """)
        elif platform == "YouTube":
            st.markdown("""
            **YouTube için:**
            - Açıklama alanı 5000 karaktere kadar
            - İlk 200 karakter "daha fazla göster" öncesi görünür
            - Zaman damgalarını kullanın
            - Linklerinizi ekleyin
            """)
        elif platform == "Twitter/X":
            st.markdown("""
            **Twitter/X için:**
            - Tek tweet 280 karakter
            - Thread kullanarak daha fazla paylaşın
            - Hashtag sayısını 2-3 ile sınırlayın
            - Görsel eklemek etkileşimi artırır
            """)
        elif platform == "LinkedIn":
            st.markdown("""
            **LinkedIn için:**
            - Post'lar için 3000 karakter
            - Profesyonel dil kullanın
            - Soru sorarak etkileşim yaratın
            - İlgili kişileri etiketleyin
            """)
        elif platform == "TikTok":
            st.markdown("""
            **TikTok için:**
            - Açıklama 2200 karaktere kadar
            - Trend hashtag'leri kullanın
            - İlk birkaç kelime çok önemli
            - Call-to-action ekleyin
            """)

else:
    st.info("👈 Format oluşturmak için sol tarafı kullanın")
    
    # Örnek şablonları göster
    st.markdown("### 📚 Mevcut Şablonlar")
    
    for platform, templates in ALL_TEMPLATES.items():
        with st.expander(f"{platform} ({len(templates)} şablon)"):
            for template_data in templates.values():
                st.markdown(f"**{template_data['emoji']} {template_data['name']}**")
```

# Footer

st.markdown(”—”)
col_f1, col_f2, col_f3 = st.columns(3)

with col_f1:
st.metric(“📱 Platformlar”, “6+”)
with col_f2:
st.metric(“🎨 Şablonlar”, “15+”)
with col_f3:
st.metric(“🌍 Diller”, “TR + EN”)

st.markdown(
“””
<div style='text-align: center; color: gray; margin-top: 2rem;'>
<p>💡 <strong>İpucu:</strong> En iyi sonuçlar için net ve yüksek çözünürlüklü görseller kullanın</p>
<p>🚀 Streamlit ile geliştirildi | 📧 Geri bildirim için iletişime geçin</p>
</div>
“””,
unsafe_allow_html=True
)
