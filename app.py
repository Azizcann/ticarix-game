import sqlite3
import json
import time
import streamlit as st
from streamlit_autorefresh import st_autorefresh
from database import init_db, save_game_data, load_all_clans, is_admin_user, get_admin_buffed_data, DB_FILE
from auth import render_auth_screen
from mining import render_mining_tab, update_mining_progress
from fishing import render_fishing_tab, update_fishing_progress
from bank import render_bank_tab, update_bank_interest
from shops import render_shops_tab, update_shop_income
from clan import render_clan_tab
from chat import render_chat_tab

st.set_page_config(
    page_title="Ticarix - Multi-User Economy & Tycoon Game",
    page_icon="🪙",
    layout="wide"
)

init_db()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "username" not in st.session_state:
    st.session_state.username = ""

st.session_state.clans_db = load_all_clans()

if not st.session_state.logged_in and "uid" in st.query_params:
    try:
        saved_uid = int(st.query_params["uid"])
        conn = sqlite3.connect(DB_FILE, timeout=10.0)
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, game_data FROM users WHERE id = ?", (saved_uid,))
        user_row = cursor.fetchone()
        conn.close()
        
        if user_row:
            st.session_state.logged_in = True
            st.session_state.user_id = user_row[0]
            st.session_state.username = user_row[1]
            g_data = json.loads(user_row[2])
            
            if is_admin_user(st.session_state.user_id):
                g_data = get_admin_buffed_data(g_data)
                
            for key, val in g_data.items():
                st.session_state[key] = val
            st.session_state.clans_db = load_all_clans()
    except Exception:
        pass

def save_current_game():
    if st.session_state.logged_in and st.session_state.user_id:
        if is_admin_user(st.session_state.user_id):
            st.session_state.money = 999999999
            st.session_state.bank_balance = 999999999
            st.session_state.bank_debt = 0

        data = {
            "money": int(st.session_state.money),
            "bank_balance": int(st.session_state.bank_balance),
            "bank_debt": int(st.session_state.bank_debt),
            "tcmb_policy_rate": st.session_state.tcmb_policy_rate,
            "last_bank_interest_time": st.session_state.last_bank_interest_time,
            "last_shop_income_time": st.session_state.last_shop_income_time,
            "clan_name": st.session_state.get("clan_name", "La Familia"),
            "user_clan": st.session_state.get("user_clan", None),
            "clan_members": st.session_state.get("clan_members", 1),
            "accumulated_shop_money": int(st.session_state.get("accumulated_shop_money", 0)),
            "active_job": st.session_state.active_job,
            "mine_level": st.session_state.mine_level,
            "mine_xp": st.session_state.mine_xp,
            "mine_inventory": st.session_state.mine_inventory,
            "mine_last_time": st.session_state.mine_last_time,
            "fish_level": st.session_state.fish_level,
            "fish_xp": st.session_state.fish_xp,
            "fish_inventory": st.session_state.fish_inventory,
            "fish_last_time": st.session_state.fish_last_time,
            "shops": st.session_state.shops
        }
        save_game_data(st.session_state.user_id, data)

if not st.session_state.logged_in:
    render_auth_screen()
else:
    st_autorefresh(interval=1000, limit=None, key="ticarix_live_clock")

    current_t = time.time()
    update_mining_progress(current_t)
    update_fishing_progress(current_t)
    update_bank_interest(current_t)
    update_shop_income(current_t)
    
    save_current_game()

    st.sidebar.title(f"👤 Oyuncu: {st.session_state.username}")
    
    if is_admin_user(st.session_state.user_id):
        st.sidebar.success("👑 Kurucu (Sınırsız Para) Aktif")

    st.sidebar.markdown(f"💰 **Nakit Para:** `{int(st.session_state.money):,} TL`")
    st.sidebar.markdown(f"🏦 **Banka Mevduat:** `{int(st.session_state.bank_balance):,} TL`")
    st.sidebar.markdown(f"📉 **Banka Borç:** `{int(st.session_state.bank_debt):,} TL`")
    st.sidebar.markdown(f"🛡️ **Klan:** `{st.session_state.get('user_clan', 'Yok')}`")
    
    if st.sidebar.button("🚪 Çıkış Yap", use_container_width=True):
        save_current_game()
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.username = ""
        if "uid" in st.query_params:
            del st.query_params["uid"]
        st.rerun()

    st.sidebar.divider()
    st.sidebar.caption("Ticarix v2.0 - Modüler Mimari")

    if "sale_message" in st.session_state:
        st.success(st.session_state.sale_message)
        del st.session_state.sale_message

    tab_mine, tab_fish, tab_bank, tab_clan, tab_shops, tab_chat = st.tabs([
        "⛏️ Madencilik", "🎣 Balıkçılık", "🏦 Merkez Bankası", "🛡️ Klan", "🏢 Dükkanlar", "💬 Sohbet"
    ])

    with tab_mine:
        render_mining_tab(save_current_game)

    with tab_fish:
        render_fishing_tab(save_current_game)

    with tab_bank:
        render_bank_tab(save_current_game)

    with tab_clan:
        render_clan_tab(save_current_game)

    with tab_shops:
        render_shops_tab(save_current_game)

    with tab_chat:
        render_chat_tab()