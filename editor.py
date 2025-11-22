import streamlit as st
import json
from pathlib import Path
import datetime

# ==============================
# AYARLAR
# ==============================
st.set_page_config(layout="wide", page_title="CIO Çift Dil Editörü", page_icon="🌍")

BASE_DIR = Path(__file__).resolve().parent

# Dosyaları Çiftler Halinde Tanımlıyoruz
SCENARIO_PAIRS = {
    "👨‍👩‍👧 Ebeveyn Versiyonu (Parent)": {
        "tr": BASE_DIR / "scenarios_parent_tr.json",
        "en": BASE_DIR / "scenarios_parent_en.json"
    },
    "🧸 Çocuk Versiyonu (Child)": {
        "tr": BASE_DIR / "scenarios_child_tr.json",
        "en": BASE_DIR / "scenarios_child_en.json"
    }
}

# ==============================
# FONKSİYONLAR
# ==============================
def load_json(path: Path):
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def get_json_str(data):
    return json.dumps(data, ensure_ascii=False, indent=2)

# Eksik alanları doldurmak için boş şablon
def ensure_structure(data, key_list):
    for key in key_list:
        if key not in data:
            data[key] = {
                "title": "New Scenario", "icon": "❓", "story": "", 
                "advisors": [], "action_cards": []
            }

# ==============================
# ARAYÜZ
# ==============================
def main():
    st.title("🌍 Çift Dil Senaryo Editörü")
    st.markdown("Türkçe ve İngilizce metinleri yan yana görerek düzenleyin.")

    # --- SIDEBAR ---
    st.sidebar.header("⚙️ Dosya Seçimi")
    selected_pair_name = st.sidebar.selectbox("Versiyon Seç:", list(SCENARIO_PAIRS.keys()))
    
    pair_paths = SCENARIO_PAIRS[selected_pair_name]

    # Model Seçimi (Her iki dosyaya da yazılır)
    st.sidebar.divider()
    st.sidebar.subheader("🧠 Model Ayarı")
    model_choice = st.sidebar.radio("Simülasyon Modeli:", ["standard", "gamma"], index=0)

    # --- VERİ YÜKLEME ---
    # Session state kullanarak veriyi hafızada tutalım
    if "current_pair" not in st.session_state or st.session_state.current_pair != selected_pair_name:
        st.session_state.data_tr = load_json(pair_paths["tr"])
        st.session_state.data_en = load_json(pair_paths["en"])
        st.session_state.current_pair = selected_pair_name

    data_tr = st.session_state.data_tr
    data_en = st.session_state.data_en

    # Model ayarını güncelle
    for d in [data_tr, data_en]:
        if "meta_settings" not in d: d["meta_settings"] = {}
        d["meta_settings"]["simulation_model"] = model_choice

    # Senaryo Anahtarlarını Birleştir (Birisinde olup diğerinde olmayan varsa yakala)
    all_keys = sorted(list(set(list(data_tr.keys()) + list(data_en.keys()))))
    all_keys = [k for k in all_keys if k != "meta_settings"] # Meta ayarı listeden çıkar

    # Eksik senaryoları tamamla
    ensure_structure(data_tr, all_keys)
    ensure_structure(data_en, all_keys)

    # --- SENARYO SEÇİMİ ---
    selected_key = st.selectbox("Düzenlenecek Senaryo:", all_keys)

    if selected_key:
        sc_tr = data_tr[selected_key]
        sc_en = data_en[selected_key]

        # --- DÜZENLEME ALANI ---
        with st.container(border=True):
            st.subheader(f"Senaryo ID: `{selected_key}`")
            
            # BAŞLIKLAR
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### 🇹🇷 Türkçe")
                sc_tr["icon"] = st.text_input("İkon", sc_tr.get("icon", ""), key="icon_tr")
                sc_tr["title"] = st.text_input("Başlık (TR)", sc_tr.get("title", ""), key="title_tr")
                sc_tr["story"] = st.text_area("Hikaye (TR)", sc_tr.get("story", ""), height=150, key="story_tr")
            
            with col2:
                st.markdown("### 🇬🇧 English")
                # İkonu TR'den kopyalamak isteyebiliriz ama manuel bırakalım
                sc_en["icon"] = st.text_input("Icon", sc_en.get("icon", ""), key="icon_en")
                sc_en["title"] = st.text_input("Title (EN)", sc_en.get("title", ""), key="title_en")
                sc_en["story"] = st.text_area("Story (EN)", sc_en.get("story", ""), height=150, key="story_en")

            st.divider()
            
            # DANIŞMANLAR (Advisors)
            st.info("👥 **Danışmanlar (Advisors)** - Sıralamanın aynı olduğundan emin olun.")
            
            # Sayıları eşitle (Eksik varsa boş ekle)
            max_adv = max(len(sc_tr.get("advisors", [])), len(sc_en.get("advisors", [])))
            while len(sc_tr.get("advisors", [])) < max_adv: