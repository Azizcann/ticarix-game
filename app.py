import sqlite3
import json
import time
import streamlit as st
from streamlit_autorefresh import st_autorefresh

import database as db
from auth import render_auth_screen
from mining import render_mining_tab, update_mining_progress
from fishing import render_fishing_tab, update_fishing_progress
from bank import render_bank_tab, update_bank_interest
from shops import render_shops_tab, update_shop_income
from clan import render_clan_tab
from chat import render_chat_tab
from leaderboard import render_leaderboard_tab

# Sayfa Yapılandırması
st.set_page_config(
    page_title="Ticarix - Multi-User Economy & Tycoon Game",
    page_icon="🪙",
    layout="wide"
)

db.init_db()

# Session State Başlatma
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "username" not in st.session_state:
    st.session_state.username = ""

st.session_state.clans_db = db.load_all_clans()

# URL Sorgusu Üzerinden Otomatik Giriş Kontrolü
if not st.session_state.logged_in and "uid" in st.query_params:
    try:
        saved_uid = int(st.query_params["uid"])
        conn = sqlite3.connect(db.DB_FILE, timeout=10.0)
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, game_data FROM users WHERE id = ?", (saved_uid,))
        user_row = cursor.fetchone()
        conn.close()
        
        if user_row:
            st.session_state.logged_in = True
            st.session_state.user_id = user_row[0]
            st.session_state.username = user_row[1]
            g_data = json.loads(user_row[2]) if user_row[2] else {}
            
            if db.is_admin_user(st.session_state.user_id):
                g_data = db.get_admin_buffed_data(g_data)
            
            # 🛑 Otomatik girişte de offline süreleri sıfırla
            g_data["active_job"] = None
            g_data["mine_last_time"] = time.time()
            g_data["fish_last_time"] = time.time()
            g_data["last_shop_income_time"] = time.time()
                
            for key, val in g_data.items():
                st.session_state[key] = val
            st.session_state.clans_db = db.load_all_clans()
    except Exception:
        pass


def save_current_game():
    """Oyuncunun güncel durumunu veritabanına kaydeder."""
    if st.session_state.logged_in and st.session_state.user_id:
        if db.is_admin_user(st.session_state.user_id):
            st.session_state.money = 999999999
            st.session_state.bank_balance = 999999999
            st.session_state.bank_debt = 0

        data = {
            "money": int(st.session_state.get("money", 5000)),
            "bank_balance": int(st.session_state.get("bank_balance", 0)),
            "bank_debt": int(st.session_state.get("bank_debt", 0)),
            "tcmb_policy_rate": st.session_state.get("tcmb_policy_rate", 15.0),
            "last_bank_interest_time": st.session_state.get("last_bank_interest_time", time.time()),
            "last_shop_income_time": st.session_state.get("last_shop_income_time", time.time()),
            "clan_name": st.session_state.get("clan_name", "La Familia"),
            "user_clan": st.session_state.get("user_clan", None),
            "clan_members": st.session_state.get("clan_members", 1),
            "accumulated_shop_money": int(st.session_state.get("accumulated_shop_money", 0)),
            "active_job": st.session_state.get("active_job", None),
            "mine_level": st.session_state.get("mine_level", 1),
            "mine_xp": st.session_state.get("mine_xp", 0),
            "mine_inventory": st.session_state.get("mine_inventory", {}),
            "mine_last_time": st.session_state.get("mine_last_time", time.time()),
            "fish_level": st.session_state.get("fish_level", 1),
            "fish_xp": st.session_state.get("fish_xp", 0),
            "fish_inventory": st.session_state.get("fish_inventory", {}),
            "fish_last_time": st.session_state.get("fish_last_time", time.time()),
            "shops": st.session_state.get("shops", {})
        }
        db.save_game_data(st.session_state.user_id, data)


# --- ARAYÜZ AKIŞI ---
if not st.session_state.logged_in:
    render_auth_screen()
else:
    # 1 Saniyelik Canlı Otomatik Yenileme
    st_autorefresh(interval=1000, limit=None, key="ticarix_live_clock")

    # Arka Plan Güncellemeleri
    current_t = time.time()
    try:
        update_mining_progress(current_t)
    except Exception:
        pass
    try:
        update_fishing_progress(current_t)
    except Exception:
        pass
    try:
        update_bank_interest(current_t)
    except Exception:
        pass
    try:
        update_shop_income(current_t)
    except Exception:
        pass
    
    save_current_game()

    # Sol Menü (Sidebar)
    st.sidebar.title(f"👤 Oyuncu: {st.session_state.username}")
    
    if db.is_admin_user(st.session_state.user_id):
        st.sidebar.success("👑 Kurucu (Sınırsız Para) Aktif")

    st.sidebar.markdown(f"💰 **Nakit Para:** `{int(st.session_state.get('money', 0)):,} TL`")
    st.sidebar.markdown(f"🏦 **Banka Mevduat:** `{int(st.session_state.get('bank_balance', 0)):,} TL`")
    st.sidebar.markdown(f"📉 **Banka Borç:** `{int(st.session_state.get('bank_debt', 0)):,} TL`")
    st.sidebar.markdown(f"🛡️ **Klan:** `{st.session_state.get('user_clan', 'Yok')}`")
    
    if st.sidebar.button("🚪 Çıkış Yap", use_container_width=True):
        # Çıkışta aktif işleri, kazı/balık ve dükkan gelirini sıfırla
        st.session_state["active_job"] = None
        st.session_state["mine_last_time"] = time.time()
        st.session_state["fish_last_time"] = time.time()
        st.session_state["last_shop_income_time"] = time.time()
        
        save_current_game()
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.username = ""
        if "uid" in st.query_params:
            del st.query_params["uid"]
        st.rerun()

    st.sidebar.divider()
    st.sidebar.caption("Ticarix v2.0 - Modüler Mimari")

    # Ana Sekmeler
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
        render_mining_tab(save_current_game)

    with tab_fish:
        render_fishing_tab(save_current_game)

    with tab_bank:
        render_bank_tab(save_current_game)
        
        # --- HAVALE & PARA TRANSFERİ PANELİ ---
        st.divider()
        st.subheader("💸 Havale & Para Transferi")
        st.caption("Başka bir oyuncunun kullanıcı adını girerek güvenle nakit para transferi yapabilirsiniz.")

        with st.form("transfer_form_final", clear_on_submit=True):
            alici_adi = st.text_input("Alıcı Kullanıcı Adı", placeholder="Örn: Ahmet123")
            gonderilecek_tutar = st.number_input("Gönderilecek Tutar (TL)", min_value=1, step=100, value=1000)
            
            transfer_onayi = st.form_submit_button("Parayı Gönder", use_container_width=True, type="primary")
            
            if transfer_onayi:
                current_user = st.session_state.get("username")
                
                if not alici_adi.strip():
                    st.error("Lütfen bir alıcı kullanıcı adı girin!")
                else:
                    # db modülü üzerinden transfer fonksiyonunu çağırıyoruz
                    basarili, mesaj = db.transfer_money(current_user, alici_adi.strip(), gonderilecek_tutar)
                    
                    if basarili:
                        if "money" in st.session_state:
                            st.session_state.money -= gonderilecek_tutar
                            
                        st.success(mesaj)
                        st.rerun()
                    else:
                        st.error(mesaj)

    with tab_clan:
        render_clan_tab(save_current_game)

    with tab_shops:
        render_shops_tab(save_current_game)

    with tab_chat:
        render_chat_tab()

    with tab_leaderboard:
        render_leaderboard_tab()

    # Satış Bildirimi
    if "sale_message" in st.session_state:
        st.toast(st.session_state.sale_message, icon="✅")
        del st.session_state.sale_message