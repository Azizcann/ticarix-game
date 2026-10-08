import json
import time
import streamlit as st
import database as db

# Modül render fonksiyonlarını içe aktar
from mining import render_mining_tab
from fishing import render_fishing_tab
from bank import render_bank_tab
from clan import render_clan_tab
from shops import render_shops_tab
from chat import render_chat_tab
from leaderboard import render_leaderboard_tab

# Sayfa Yapılandırması
st.set_page_config(
    page_title="Ticarix - Ekonomi & Klan Simülasyonu",
    page_icon="💼",
    layout="wide"
)

# Veritabanı Tablolarını Başlat
db.init_db()

# Oturum Durumlarını (Session State) Kontrol Et ve İlklendir
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "username" not in st.session_state:
    st.session_state.username = None


def save_current_user_data():
    """Oyuncunun güncel oturum verilerini veritabanına kaydeder."""
    if not st.session_state.user_id:
        return
    
    data_to_save = {
        "money": st.session_state.get("money", 5000),
        "bank_balance": st.session_state.get("bank_balance", 0),
        "bank_debt": st.session_state.get("bank_debt", 0),
        "user_clan": st.session_state.get("user_clan", None),
        "clan_members": st.session_state.get("clan_members", 1),
        "mine_level": st.session_state.get("mine_level", 1),
        "mine_xp": st.session_state.get("mine_xp", 0),
        "mine_inventory": st.session_state.get("mine_inventory", {}),
        "mine_last_time": st.session_state.get("mine_last_time", 0),
        "fish_level": st.session_state.get("fish_level", 1),
        "fish_xp": st.session_state.get("fish_xp", 0),
        "fish_inventory": st.session_state.get("fish_inventory", {}),
        "fish_last_time": st.session_state.get("fish_last_time", 0),
        "shops": st.session_state.get("shops", {})
    }
    db.save_game_data(st.session_state.user_id, data_to_save)


# --- 1. GİRİŞ & KAYIT EKRANI ---
if not st.session_state.user_id:
    st.title("💼 Ticarix'e Hoş Geldiniz")
    st.caption("Multiplayer Ekonomi ve Klan Yönetim Oyunu")
    
    tab_login, tab_register = st.tabs(["🔑 Giriş Yap", "📝 Kayıt Ol"])
    
    with tab_login:
        st.subheader("Giriş Yap")
        login_id = st.text_input("Kullanıcı Adı veya E-Posta", key="login_id")
        login_pass = st.text_input("Şifre", type="password", key="login_pass")
        
        if st.button("Giriş Yap", type="primary", use_container_width=True):
            user = db.login_user(login_id, login_pass)
            if user:
                user_id, username, game_data_json = user
                st.session_state.user_id = user_id
                st.session_state.username = username
                
                g_data = json.loads(game_data_json)
                for key, val in g_data.items():
                    st.session_state[key] = val
                    
                st.success(f"Hoş geldin, {username}!")
                st.rerun()
            else:
                st.error("Kullanıcı adı/e-posta veya şifre hatalı!")

    with tab_register:
        st.subheader("Yeni Hesap Oluştur")
        reg_user = st.text_input("Kullanıcı Adı", key="reg_user")
        reg_email = st.text_input("E-Posta", key="reg_email")
        reg_pass = st.text_input("Şifre", type="password", key="reg_pass")
        
        if st.button("Kayıt Ol", type="primary", use_container_width=True):
            if not reg_user or not reg_email or not reg_pass:
                st.warning("Lütfen tüm alanları doldurun!")
            else:
                success, msg = db.register_user(reg_user, reg_email, reg_pass)
                if success:
                    st.success(msg)
                else:
                    st.error(msg)
    st.stop()


# --- 2. OYUN ANA EKRANI (GİRİŞ YAPILMIŞ) ---

# Yan Menü (Sidebar) Profil Paneli
with st.sidebar:
    st.title(f"👤 Oyuncu: {st.session_state.username}")
    st.write(f"💰 **Nakit Para:** {int(st.session_state.get('money', 0)):,} TL")
    st.write(f"🏦 **Banka Mevduat:** {int(st.session_state.get('bank_balance', 0)):,} TL")
    st.write(f"💸 **Banka Borç:** {int(st.session_state.get('bank_debt', 0)):,} TL")
    st.write(f"🛡️ **Klan:** {st.session_state.get('user_clan') or 'Yok'}")
    
    st.divider()
    if st.button("🚪 Çıkış Yap", use_container_width=True):
        save_current_user_data()
        st.session_state.clear()
        st.rerun()

# Satış Bildirim Mesajı
if "sale_message" in st.session_state:
    st.toast(st.session_state.sale_message, icon="✅")
    del st.session_state.sale_message

# Ana Sekme Yapısı
tab_mine, tab_fish, tab_bank, tab_clan, tab_shops, tab_chat, tab_leaderboard = st.tabs([
    "⛏️ Madencilik", 
    "🎣 Balıkçılık", 
    "🏦 Merkez Bankası", 
    "🛡️ Klan", 
    "🏢 Dükkanlar", 
    "💬 Sohbet", 
    "🏆 Sıralama"
])

with tab_mine:
    render_mining_tab(save_current_user_data)

with tab_fish:
    render_fishing_tab(save_current_user_data)

with tab_bank:
    render_bank_tab(save_current_user_data)

with tab_clan:
    render_clan_tab(save_current_user_data)

with tab_shops:
    render_shops_tab(save_current_user_data)

with tab_chat:
    render_chat_tab()

with tab_leaderboard:
    render_leaderboard_tab()

# --- 3. CANLI SAYAÇ DÖNGÜSÜ (AUTO-REFRESH) ---
# Ekranda geri sayımların ve zamanın canlı aksı için her 1 saniyede bir sayfayı günceller.
time.sleep(1)
st.rerun()