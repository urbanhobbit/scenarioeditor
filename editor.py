import streamlit as st
import json
from pathlib import Path
import datetime

# ==============================
# AYARLAR VE DOSYA YOLLARI
# ==============================
st.set_page_config(layout="wide", page_title="CIO Kriz Yönetimi - Editör", page_icon="🛡️")

BASE_DIR = Path(__file__).resolve().parent

# Yüklenen tüm dosyaları buraya tanımlıyoruz
SCENARIO_FILES = {
    "🇹🇷 TR - Ebeveyn Versiyonu": BASE_DIR / "scenarios_parent_tr.json",
    "🇹🇷 TR - Çocuk Versiyonu": BASE_DIR / "scenarios_child_tr.json",
    "🇬🇧 EN - Parent Version": BASE_DIR / "scenarios_parent_en.json",
    "🇬🇧 EN - Child Version": BASE_DIR / "scenarios_child_en.json",
}

# ==============================
# YARDIMCI FONKSİYONLAR
# ==============================
def load_data(file_path: Path):
    """JSON dosyasını okur."""
    try:
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        st.error(f"Dosya okuma hatası: {e}")
        return {}
    return {}

def get_json_string(data):
    """Data dict'ini indirilebilir string formatına çevirir."""
    return json.dumps(data, ensure_ascii=False, indent=2)

# ==============================
# ARAYÜZ VE MANTIK
# ==============================
def main():
    st.title("🛡️ Kriz Yönetimi Senaryo Editörü (Cloud Uyumlu)")
    
    # --- SIDEBAR: DOSYA VE MODEL SEÇİMİ ---
    st.sidebar.header("⚙️ Ayarlar")
    
    # 1. Dosya Seçimi
    selected_file_name = st.sidebar.selectbox(
        "Düzenlenecek Dosya:",
        options=list(SCENARIO_FILES.keys())
    )
    current_file_path = SCENARIO_FILES[selected_file_name]
    
    # Veriyi Yükle
    if "data_cache" not in st.session_state or st.session_state.get("current_file") != selected_file_name:
        st.session_state.data_cache = load_data(current_file_path)
        st.session_state.current_file = selected_file_name

    data = st.session_state.data_cache

    # 2. Model Tercihi (İsteğiniz üzerine eklendi)
    st.sidebar.markdown("---")
    st.sidebar.subheader("🧠 Simülasyon Modeli")
    st.sidebar.info("Bu ayar, oyunun risk hesaplama motorunu belirler.")
    
    # Mevcut ayarı JSON'dan oku, yoksa varsayılan yap
    current_model = data.get("meta_settings", {}).get("simulation_model", "standard")
    
    model_choice = st.sidebar.radio(
        "Model Seçiniz:",
        options=["standard", "gamma"],
        format_func=lambda x: "Standart (Lineer) Model" if x == "standard" else "Gamma (Olasılıksal) Model",
        index=0 if current_model == "standard" else 1
    )

    # Model bilgisini veriye kaydet (Meta ayar olarak)
    if "meta_settings" not in data:
        data["meta_settings"] = {}
    data["meta_settings"]["simulation_model"] = model_choice

    # Model Açıklaması
    if model_choice == "gamma":
        st.sidebar.warning("⚠️ **Gamma Modeli Seçildi:** Risk hesaplamaları Gamma dağılımı kullanılarak daha belirsiz ve kaotik yapılacaktır.")
    else:
        st.sidebar.success("✅ **Standart Model:** Sonuçlar daha öngörülebilir ve deterministiktir.")

    # --- ANA EDİTÖR ---
    if not data:
        st.warning("Dosya boş veya okunamadı. Yeni bir şablon oluşturuluyor...")
        data = {}

    # Senaryo Listesi
    scenario_keys = [k for k in data.keys() if k != "meta_settings"] # Ayar dışındaki keyler
    
    if not scenario_keys:
        st.info("Henüz senaryo yok. Lütfen ekleyin.")
    
    selected_scenario_key = st.selectbox("Senaryo Seçin:", ["(Yeni Senaryo Ekle)"] + scenario_keys)

    # --- SENARYO DÜZENLEME FORMU ---
    with st.container(border=True):
        if selected_scenario_key == "(Yeni Senaryo Ekle)":
            st.subheader("➕ Yeni Senaryo")
            new_id = st.text_input("Senaryo ID (benzersiz, örn: flood_crisis)")
            if new_id and new_id not in data:
                if st.button("Oluştur"):
                    data[new_id] = {
                        "title": "Yeni Kriz", 
                        "icon": "⚠️", 
                        "story": "", 
                        "advisors": [], 
                        "action_cards": []
                    }
                    st.rerun()
            elif new_id in data:
                st.error("Bu ID zaten var!")
        else:
            scenario = data[selected_scenario_key]
            st.subheader(f"✏️ Düzenleniyor: {scenario.get('title', selected_scenario_key)}")
            
            # Temel Bilgiler
            c1, c2 = st.columns([3, 1])
            scenario["title"] = c1.text_input("Senaryo Başlığı", value=scenario.get("title", ""))
            scenario["icon"] = c2.text_input("İkon (Emoji)", value=scenario.get("icon", "ATTR"))
            
            scenario["story"] = st.text_area("Hikaye Metni", value=scenario.get("story", ""))
            
            # Danışmanlar
            with st.expander("👥 Danışman Görüşleri"):
                advisors = scenario.get("advisors", [])
                for i, adv in enumerate(advisors):
                    cols = st.columns([1, 3])
                    adv["name"] = cols[0].text_input(f"Danışman {i+1} Adı", value=adv.get("name", ""))
                    adv["text"] = cols[1].text_area(f"Görüş {i+1}", value=adv.get("text", ""), height=70)
                
                if st.button("➕ Danışman Ekle"):
                    advisors.append({"name": "Yeni", "text": ""})
                    st.rerun()
                scenario["advisors"] = advisors

            # Aksiyon Kartları
            st.markdown("### 🃏 Aksiyon Kartları")
            cards = scenario.get("action_cards", [])
            
            tabs = st.tabs([c.get("name", f"Kart {i+1}") for i, c in enumerate(cards)] + ["+ Ekle"])
            
            # Kart Düzenleme
            for i, card in enumerate(cards):
                with tabs[i]:
                    c1, c2 = st.columns(2)
                    card["name"] = c1.text_input(f"Kart Adı ({i})", value=card.get("name", ""))
                    card["id"] = c2.text_input(f"Kart ID ({i})", value=card.get("id", ""))
                    
                    card["tooltip"] = st.text_area(f"İpucu ({i})", value=card.get("tooltip", ""))
                    
                    # Metrikler
                    m1, m2, m3 = st.columns(3)
                    card["cost"] = m1.number_input(f"Maliyet ({i})", value=int(card.get("cost", 0)))
                    card["security_effect"] = m2.number_input(f"Güvenlik Etkisi ({i})", value=int(card.get("security_effect", 0)))
                    card["freedom_cost"] = m3.number_input(f"Özgürlük Maliyeti ({i})", value=int(card.get("freedom_cost", 0)))
                    
                    # Gamma/Standart Model Etkisi Görselleştirme
                    if model_choice == "gamma":
                        st.caption(f"📈 *Gamma Modeli Aktif:* Bu kartın yan etki riski ({card.get('side_effect_risk', 0)}) simülasyonda değişkenlik gösterecektir.")

            # Yeni Kart Ekleme Tabı
            with tabs[-1]:
                if st.button("Yeni Kart Oluştur"):
                    cards.append({"id": "NEW", "name": "Yeni Seçenek", "cost": 10})
                    st.rerun()
            
            scenario["action_cards"] = cards
            
            # Sonuç Metinleri
            st.markdown("### 📝 Sonuç Metinleri")
            scenario["immediate_text"] = st.text_area("Anlık Geri Bildirim", value=scenario.get("immediate_text", ""))
            scenario["delayed_text"] = st.text_area("Gecikmeli Sonuç", value=scenario.get("delayed_text", ""))
            
            # Senaryoyu Silme
            if st.button("🗑️ Bu Senaryoyu Sil", type="primary"):
                del data[selected_scenario_key]
                st.rerun()

    # --- KAYDETME VE İNDİRME ALANI ---
    st.markdown("---")
    st.subheader("💾 Kaydet ve İndir")
    st.info("Streamlit Cloud üzerinde dosyalar geçicidir. Yaptığınız değişiklikleri kaybetmemek için JSON dosyasını indirmelisiniz.")

    # Veriyi JSON stringine çevir
    json_str = get_json_string(data)
    
    col_d1, col_d2 = st.columns([1, 1])
    
    # İndirme Butonu
    file_prefix = selected_file_name.split(" - ")[-1].replace(" ", "_").lower()
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    download_name = f"{file_prefix}_{timestamp}.json"
    
    col_d1.download_button(
        label="📥 Güncel JSON Dosyasını İndir",
        data=json_str,
        file_name=download_name,
        mime="application/json",
        type="primary"
    )
    
    # Hızlı Önizleme
    with st.expander("👀 Ham JSON Verisini Gör"):
        st.json(data)

if __name__ == "__main__":
    main()