import streamlit as st
import json
from pathlib import Path
import shutil
import datetime

# ==============================
# AYARLAR
# ==============================
st.set_page_config(layout="wide", page_title="CIO Çift Dil Editörü", page_icon="🌍")

BASE_DIR = Path(__file__).resolve().parent
BACKUP_DIR = BASE_DIR / "backups" # Yedeklerin tutulacağı klasör

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

def save_and_backup(path: Path, data: dict):
    """Dosyayı kaydeder ve öncesinde yedek alır."""
    if not path.exists():
        # Dosya yoksa direkt yaz (ilk oluşturma)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return "Oluşturuldu"

    # 1. Yedekleme (Backup)
    BACKUP_DIR.mkdir(exist_ok=True) # Klasör yoksa oluştur
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"{path.stem}_{timestamp}{path.suffix}" # örn: scenarios_tr_20231025_1400.json
    backup_path = BACKUP_DIR / backup_filename
    
    try:
        shutil.copy(path, backup_path)
        backup_status = "Yedeklendi"
    except Exception as e:
        backup_status = f"Yedeklenemedi ({e})"

    # 2. Kaydetme (Overwrite)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return backup_status

def create_empty_scenario():
    return {
        "title": "Yeni Senaryo", "icon": "❓", "story": "", 
        "advisors": [{"name": "Danışman 1", "text": ""}, {"name": "Danışman 2", "text": ""}], 
        "action_cards": [
            {"id": "A", "name": "Kart A", "cost": 10, "hr_cost": 5, "speed": "fast", "security_effect": 10, "freedom_cost": 10, "side_effect_risk": 0.1, "safeguard_reduction": 0.5, "tooltip": ""},
            {"id": "B", "name": "Kart B", "cost": 10, "hr_cost": 5, "speed": "medium", "security_effect": 10, "freedom_cost": 10, "side_effect_risk": 0.1, "safeguard_reduction": 0.5, "tooltip": ""},
            {"id": "C", "name": "Kart C", "cost": 10, "hr_cost": 5, "speed": "slow", "security_effect": 10, "freedom_cost": 10, "side_effect_risk": 0.1, "safeguard_reduction": 0.5, "tooltip": ""}
        ],
        "immediate_text": "", "delayed_text": ""
    }

# ==============================
# ARAYÜZ
# ==============================
def main():
    st.title("🌍 Çift Dil Senaryo Editörü v3.0")
    st.markdown("Otomatik senkronizasyon, sunucuya kaydetme ve yedekleme özellikleri aktiftir.")

    # --- SIDEBAR ---
    st.sidebar.header("⚙️ Dosya Seçimi")
    selected_pair_name = st.sidebar.selectbox("Versiyon Seç:", list(SCENARIO_PAIRS.keys()))
    
    pair_paths = SCENARIO_PAIRS[selected_pair_name]

    # --- VERİ YÜKLEME ---
    if "current_pair" not in st.session_state or st.session_state.current_pair != selected_pair_name:
        st.session_state.data_tr = load_json(pair_paths["tr"])
        st.session_state.data_en = load_json(pair_paths["en"])
        st.session_state.current_pair = selected_pair_name

    data_tr = st.session_state.data_tr
    data_en = st.session_state.data_en

    # --- KAYDET & YEDEKLE BUTONU (SIDEBAR) ---
    st.sidebar.divider()
    st.sidebar.subheader("💾 Kaydetme İşlemleri")
    
    if st.sidebar.button("💾 Değişiklikleri Kaydet (Sunucuya)", type="primary", use_container_width=True):
        # TR Kaydet
        res_tr = save_and_backup(pair_paths["tr"], data_tr)
        # EN Kaydet
        res_en = save_and_backup(pair_paths["en"], data_en)
        
        st.sidebar.success(f"Başarılı!\nTR: {res_tr}\nEN: {res_en}")
        st.toast("Dosyalar sunucuya kaydedildi ve yedeklendi!", icon="✅")

    # --- YENİ SENARYO EKLEME ---
    st.sidebar.divider()
    with st.sidebar.form("new_scenario_form"):
        st.subheader("➕ Yeni Senaryo Ekle")
        new_id = st.text_input("Senaryo ID (örn: flood_crisis)").strip().lower()
        if st.form_submit_button("Ekle"):
            if new_id and new_id not in data_tr:
                data_tr[new_id] = create_empty_scenario()
                data_en[new_id] = create_empty_scenario()
                data_en[new_id]["title"] = "New Scenario" 
                save_and_backup(pair_paths["tr"], data_tr) # Hemen kaydet
                save_and_backup(pair_paths["en"], data_en)
                st.success(f"'{new_id}' eklendi ve kaydedildi!")
                st.rerun()
            elif new_id in data_tr:
                st.error("Bu ID zaten var!")

    # --- SENARYO LİSTESİ ---
    all_keys = sorted([k for k in data_tr.keys() if k != "meta_settings"])
    selected_key = st.selectbox("Düzenlenecek Senaryo:", all_keys)

    if selected_key:
        sc_tr = data_tr[selected_key]
        sc_en = data_en[selected_key]

        # --- DÜZENLEME ALANI ---
        with st.container(border=True):
            st.subheader(f"Senaryo ID: `{selected_key}`")
            
            # GENEL BİLGİLER
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### 🇹🇷 Türkçe")
                common_icon = st.text_input("İkon (Ortak)", sc_tr.get("icon", "❓"), key=f"icon_common_{selected_key}")
                sc_tr["icon"] = common_icon
                sc_en["icon"] = common_icon 
                
                sc_tr["title"] = st.text_input("Başlık (TR)", sc_tr.get("title", ""), key=f"title_tr_{selected_key}")
                sc_tr["story"] = st.text_area("Hikaye (TR)", sc_tr.get("story", ""), height=150, key=f"story_tr_{selected_key}")
            
            with col2:
                st.markdown("### 🇬🇧 English")
                st.text_input("Icon (Synced)", sc_en.get("icon", ""), disabled=True, key=f"icon_en_disp_{selected_key}")
                sc_en["title"] = st.text_input("Title (EN)", sc_en.get("title", ""), key=f"title_en_{selected_key}")
                sc_en["story"] = st.text_area("Story (EN)", sc_en.get("story", ""), height=150, key=f"story_en_{selected_key}")

            st.divider()
            
            # DANIŞMANLAR
            st.info("👥 **Danışmanlar**")
            max_adv = max(len(sc_tr.get("advisors", [])), len(sc_en.get("advisors", [])))
            
            while len(sc_tr.get("advisors", [])) < max_adv: sc_tr.setdefault("advisors", []).append({})
            while len(sc_en.get("advisors", [])) < max_adv: sc_en.setdefault("advisors", []).append({})

            for i in range(max_adv):
                adv_tr = sc_tr["advisors"][i]
                adv_en = sc_en["advisors"][i]
                
                c1, c2 = st.columns(2)
                with c1:
                    adv_tr["name"] = st.text_input(f"Danışman {i+1} Adı (TR)", adv_tr.get("name", ""), key=f"adv_n_tr_{selected_key}_{i}")
                    adv_tr["text"] = st.text_area(f"Görüş {i+1} (TR)", adv_tr.get("text", ""), height=100, key=f"adv_t_tr_{selected_key}_{i}")
                with c2:
                    adv_en["name"] = st.text_input(f"Advisor {i+1} Name (EN)", adv_en.get("name", ""), key=f"adv_n_en_{selected_key}_{i}")
                    adv_en["text"] = st.text_area(f"Advice {i+1} (EN)", adv_en.get("text", ""), height=100, key=f"adv_t_en_{selected_key}_{i}")
                st.divider()

            # AKSİYON KARTLARI
            st.info("🃏 **Aksiyon Kartları (Metrikler TR'den Kopyalanır)**")
            
            max_cards = max(len(sc_tr.get("action_cards", [])), len(sc_en.get("action_cards", [])))
            while len(sc_tr.get("action_cards", [])) < max_cards: sc_tr.setdefault("action_cards", []).append({"id": "NEW", "cost": 0})
            while len(sc_en.get("action_cards", [])) < max_cards: sc_en.setdefault("action_cards", []).append({"id": "NEW", "cost": 0})

            tabs = st.tabs([f"Kart {i+1}" for i in range(max_cards)])
            
            for i, tab in enumerate(tabs):
                with tab:
                    card_tr = sc_tr["action_cards"][i]
                    card_en = sc_en["action_cards"][i]
                    
                    c1, c2 = st.columns(2)
                    
                    # TR (Sol)
                    with c1:
                        st.markdown("**🇹🇷 Türkçe & ⚙️ Ayarlar**")
                        card_tr["id"] = st.text_input("Kart ID", card_tr.get("id", "A"), key=f"cid_{selected_key}_{i}")
                        card_tr["name"] = st.text_input("Kart Adı (TR)", card_tr.get("name", ""), key=f"cn_tr_{selected_key}_{i}")
                        card_tr["tooltip"] = st.text_area("İpucu (TR)", card_tr.get("tooltip", ""), height=80, key=f"ct_tr_{selected_key}_{i}")
                        
                        m1, m2, m3 = st.columns(3)
                        card_tr["cost"] = m1.number_input("Maliyet", value=int(card_tr.get("cost", 0)), key=f"cost_{selected_key}_{i}")
                        card_tr["hr_cost"] = m2.number_input("İK", value=int(card_tr.get("hr_cost", 0)), key=f"hr_{selected_key}_{i}")
                        card_tr["speed"] = m3.selectbox("Hız", ["fast", "medium", "slow"], index=["fast", "medium", "slow"].index(card_tr.get("speed", "medium")), key=f"spd_{selected_key}_{i}")
                        
                        m4, m5 = st.columns(2)
                        card_tr["security_effect"] = m4.number_input("Güvenlik Etkisi (+)", value=int(card_tr.get("security_effect", 0)), key=f"sec_{selected_key}_{i}")
                        card_tr["freedom_cost"] = m5.number_input("Özgürlük Maliyeti (-)", value=int(card_tr.get("freedom_cost", 0)), key=f"free_{selected_key}_{i}")

                        # Senkronizasyon
                        card_en["id"] = card_tr["id"]
                        card_en["cost"] = card_tr["cost"]
                        card_en["hr_cost"] = card_tr["hr_cost"]
                        card_en["speed"] = card_tr["speed"]
                        card_en["security_effect"] = card_tr["security_effect"]
                        card_en["freedom_cost"] = card_tr["freedom_cost"]
                        if "side_effect_risk" in card_tr: card_en["side_effect_risk"] = card_tr["side_effect_risk"]
                        if "safeguard_reduction" in card_tr: card_en["safeguard_reduction"] = card_tr["safeguard_reduction"]

                    # EN (Sağ)
                    with c2:
                        st.markdown("**🇬🇧 English Translation**")
                        st.text_input("Card ID (Locked)", card_en.get("id", ""), disabled=True, key=f"cid_en_{selected_key}_{i}")
                        card_en["name"] = st.text_input("Card Name (EN)", card_en.get("name", ""), key=f"cn_en_{selected_key}_{i}")
                        card_en["tooltip"] = st.text_area("Tooltip (EN)", card_en.get("tooltip", ""), height=80, key=f"ct_en_{selected_key}_{i}")
                        
                        st.info(f"📊 Stats synced: Cost {card_en.get('cost')} | Sec +{card_en.get('security_effect')} | Free -{card_en.get('freedom_cost')}")

            st.divider()
            
            # SONUÇLAR
            col_res1, col_res2 = st.columns(2)
            with col_res1:
                sc_tr["immediate_text"] = st.text_area("Anlık Sonuç Metni (TR)", sc_tr.get("immediate_text", ""), key=f"it_tr_{selected_key}")
                sc_tr["delayed_text"] = st.text_area("Gecikmeli Sonuç Metni (TR)", sc_tr.get("delayed_text", ""), key=f"dt_tr_{selected_key}")
            with col_res2:
                sc_en["immediate_text"] = st.text_area("Immediate Result Text (EN)", sc_en.get("immediate_text", ""), key=f"it_en_{selected_key}")
                sc_en["delayed_text"] = st.text_area("Delayed Result Text (EN)", sc_en.get("delayed_text", ""), key=f"dt_en_{selected_key}")

    # --- ALTTAKİ İNDİR BUTONLARI (Yine de kalsın isteyen PC'ye indirsin) ---
    st.markdown("---")
    st.caption("Aşağıdaki butonlar dosyayı bilgisayarınıza indirir. Yukarıdaki 'Kaydet' butonu ise sunucudaki dosyayı günceller.")
    c_down1, c_down2 = st.columns(2)
    
    if "Parent" in selected_pair_name:
        name_tr, name_en = "scenarios_parent_tr.json", "scenarios_parent_en.json"
    else:
        name_tr, name_en = "scenarios_child_tr.json", "scenarios_child_en.json"

    c_down1.download_button(
        label=f"📥 {name_tr} Bilgisayara İndir",
        data=get_json_str(data_tr),
        file_name=name_tr,
        mime="application/json",
        use_container_width=True
    )
    
    c_down2.download_button(
        label=f"📥 {name_en} Bilgisayara İndir",
        data=get_json_str(data_en),
        file_name=name_en,
        mime="application/json",
        use_container_width=True
    )

if __name__ == "__main__":
    main()