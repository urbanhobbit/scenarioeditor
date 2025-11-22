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
            while len(sc_tr.get("advisors", [])) < max_adv: sc_tr.setdefault("advisors", []).append({})
            while len(sc_en.get("advisors", [])) < max_adv: sc_en.setdefault("advisors", []).append({})

            for i in range(max_adv):
                adv_tr = sc_tr["advisors"][i]
                adv_en = sc_en["advisors"][i]
                
                c1, c2 = st.columns(2)
                with c1:
                    with st.expander(f"Danışman {i+1} (TR)"):
                        adv_tr["name"] = st.text_input("Adı", adv_tr.get("name", ""), key=f"adv_name_tr_{i}")
                        adv_tr["text"] = st.text_area("Görüşü", adv_tr.get("text", ""), key=f"adv_text_tr_{i}")
                with c2:
                    with st.expander(f"Advisor {i+1} (EN)"):
                        adv_en["name"] = st.text_input("Name", adv_en.get("name", ""), key=f"adv_name_en_{i}")
                        adv_en["text"] = st.text_area("Advice", adv_en.get("text", ""), key=f"adv_text_en_{i}")

            st.divider()

            # AKSİYON KARTLARI
            st.info("🃏 **Aksiyon Kartları**")
            
            max_cards = max(len(sc_tr.get("action_cards", [])), len(sc_en.get("action_cards", [])))
            # Kart listelerini eşitle
            while len(sc_tr.get("action_cards", [])) < max_cards: sc_tr.setdefault("action_cards", []).append({"id": "NEW", "cost": 0})
            while len(sc_en.get("action_cards", [])) < max_cards: sc_en.setdefault("action_cards", []).append({"id": "NEW", "cost": 0})

            tabs = st.tabs([f"Kart {i+1}" for i in range(max_cards)])
            
            for i, tab in enumerate(tabs):
                with tab:
                    card_tr = sc_tr["action_cards"][i]
                    card_en = sc_en["action_cards"][i]
                    
                    # ID ve Metrikler (Ortak olmalı ama ayrı ayrı düzenlenebilir, dikkat edilmeli)
                    st.caption("Metrikleri (Maliyet, Risk vb.) TR tarafında düzenlemeniz önerilir. EN tarafı genelde aynı kalır.")
                    
                    c1, c2 = st.columns(2)
                    
                    # TR Tarafı (Sol)
                    with c1:
                        st.markdown("**🇹🇷 Türkçe İçerik**")
                        card_tr["name"] = st.text_input("Kart Adı", card_tr.get("name", ""), key=f"cn_tr_{i}")
                        card_tr["tooltip"] = st.text_area("İpucu", card_tr.get("tooltip", ""), height=100, key=f"ct_tr_{i}")
                        
                        # Metrikler TR tarafında
                        m1, m2 = st.columns(2)
                        card_tr["cost"] = m1.number_input("Maliyet", value=int(card_tr.get("cost", 0)), key=f"cc_tr_{i}")
                        card_tr["hr_cost"] = m2.number_input("İK Maliyeti", value=int(card_tr.get("hr_cost", 0)), key=f"chr_tr_{i}")
                        
                        card_tr["side_effect_risk"] = st.slider("Yan Etki Riski", 0.0, 1.0, float(card_tr.get("side_effect_risk", 0.0)), key=f"cr_tr_{i}")

                    # EN Tarafı (Sağ)
                    with c2:
                        st.markdown("**🇬🇧 English Content**")
                        card_en["name"] = st.text_input("Card Name", card_en.get("name", ""), key=f"cn_en_{i}")
                        card_en["tooltip"] = st.text_area("Tooltip", card_en.get("tooltip", ""), height=100, key=f"ct_en_{i}")
                        
                        # Metrikleri senkronize etmek ister misin?
                        # Şimdilik sadece gösteriyoruz ama editable.
                        m1, m2 = st.columns(2)
                        card_en["cost"] = m1.number_input("Cost", value=int(card_en.get("cost", 0)), key=f"cc_en_{i}")
                        card_en["hr_cost"] = m2.number_input("HR Cost", value=int(card_en.get("hr_cost", 0)), key=f"chr_en_{i}")
                        
                        card_en["side_effect_risk"] = st.slider("Side Effect Risk", 0.0, 1.0, float(card_en.get("side_effect_risk", 0.0)), key=f"cr_en_{i}")

                    # Diğer tüm teknik metrikleri JSON'a kaydetmek için arkada kopyalamak iyi fikir olabilir
                    # Ama şimdilik basit tutuyoruz.

            st.divider()
            
            # SONUÇ METİNLERİ
            col_res1, col_res2 = st.columns(2)
            with col_res1:
                sc_tr["immediate_text"] = st.text_area("Anlık Sonuç (TR)", sc_tr.get("immediate_text", ""), key="it_tr")
                sc_tr["delayed_text"] = st.text_area("Gecikmeli Sonuç (TR)", sc_tr.get("delayed_text", ""), key="dt_tr")
            with col_res2:
                sc_en["immediate_text"] = st.text_area("Immediate Result (EN)", sc_en.get("immediate_text", ""), key="it_en")
                sc_en["delayed_text"] = st.text_area("Delayed Result (EN)", sc_en.get("delayed_text", ""), key="dt_en")

    # --- KAYDETME ALANI ---
    st.markdown("---")
    st.subheader("💾 Dosyaları İndir (Download)")
    
    c_down1, c_down2 = st.columns(2)
    
    # Dosya isimlerini oluştur
    if "Parent" in selected_pair_name:
        name_tr, name_en = "scenarios_parent_tr.json", "scenarios_parent_en.json"
    else:
        name_tr, name_en = "scenarios_child_tr.json", "scenarios_child_en.json"

    # TR İndir
    c_down1.download_button(
        label=f"📥 {name_tr} İndir",
        data=get_json_str(data_tr),
        file_name=name_tr,
        mime="application/json",
        type="primary",
        use_container_width=True
    )
    
    # EN İndir
    c_down2.download_button(
        label=f"📥 {name_en} İndir",
        data=get_json_str(data_en),
        file_name=name_en,
        mime="application/json",
        type="primary",
        use_container_width=True
    )

if __name__ == "__main__":
    main()