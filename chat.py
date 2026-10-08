import streamlit as st
import database as db
import os
import json
import sqlite3

def get_user_avatar_by_username(uname):
    """Veritabanından kullanıcının profil fotoğrafı yolunu çeker."""
    try:
        conn = sqlite3.connect(db.DB_FILE, timeout=10.0)
        cursor = conn.cursor()
        cursor.execute("SELECT game_data FROM users WHERE username = ?", (uname,))
        row = cursor.fetchone()
        conn.close()
        if row and row[0]:
            g_data = json.loads(row[0])
            pic = g_data.get("profile_pic", None)
            if pic and os.path.exists(pic):
                return pic
    except Exception:
        pass
    return None

def render_chat_tab():
    """Oyuncular arası genel canlı sohbet panelini çizer."""
    st.subheader("💬 Genel Oyuncu Sohbeti")
    st.caption("Tüm oyuncularla anlık olarak sohbet edebilirsin. Mesajlar kalıcıdır!")

    # 🎨 Yuvarlak Profil Fotoğrafları için CSS Stili
    st.markdown("""
        <style>
            .chat-avatar-img {
                width: 38px;
                height: 38px;
                border-radius: 50%;
                object-fit: cover;
                border: 2px solid #ff4b4b;
                margin-right: 8px;
                vertical-align: middle;
            }
            .chat-initial-avatar {
                width: 38px;
                height: 38px;
                border-radius: 50%;
                background-color: #333;
                color: white;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                font-weight: bold;
                margin-right: 8px;
                vertical-align: middle;
            }
        </style>
    """, unsafe_allow_html=True)

    # Sohbet akış alanı
    chat_container = st.container(height=400)

    # Son 50 mesajı çek[cite: 5]
    messages = db.get_chat_messages(limit=50)

    with chat_container:
        if not messages:
            st.info("Henüz sohbet mesajı yok. İlk mesajı sen yaz!")[cite: 5]
        else:
            for username, msg, msg_time in messages:
                avatar_path = get_user_avatar_by_username(username)
                
                # HTML ile yuvarlak profil resmi veya baş harf gösterimi
                if avatar_path and os.path.exists(avatar_path):
                    avatar_html = f'<img src="app/static/{avatar_path}" class="chat-avatar-img" onerror="this.style.display=\'none\'">'
                else:
                    initial = username[0].upper() if username else "O"
                    avatar_html = f'<div class="chat-initial-avatar">{initial}</div>'

                st.markdown(f"""
                    <div style="display: flex; align-items: flex-start; margin-bottom: 10px;">
                        <div>{avatar_html}</div>
                        <div>
                            <b>{username}</b> <span style="font-size: 0.75em; color: #888;">({msg_time})</span><br>
                            <span style="font-size: 0.95em;">{msg}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

    # Mesaj Girdisi[cite: 5]
    prompt = st.chat_input("Mesajını yaz ve Enter'a bas...")
    if prompt:
        current_username = st.session_state.get("username", "Oyuncu")
        db.save_chat_message(current_username, prompt)
        st.rerun()