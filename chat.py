import streamlit as st
import database as db
import os
import json
import sqlite3
import base64

def get_user_avatar_base64(uname):
    """Kullanıcının profil fotoğrafını güvenli ve hızlı bir şekilde base64'e çevirir."""
    try:
        conn = sqlite3.connect(db.DB_FILE, timeout=5.0)
        cursor = conn.cursor()
        cursor.execute("SELECT game_data FROM users WHERE username = ?", (uname,))
        row = cursor.fetchone()
        conn.close()
        
        if row and row[0]:
            g_data = json.loads(row[0])
            pic = g_data.get("profile_pic", None)
            if pic and os.path.exists(pic):
                with open(pic, "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode()
                    ext = pic.split(".")[-1].lower()
                    mime = "image/jpeg" if ext in ["jpg", "jpeg"] else "image/png"
                    return f"data:{mime};base64,{encoded_string}"
    except Exception:
        pass
    return None

def render_chat_tab():
    """Oyuncular arası genel canlı sohbet panelini çizer."""
    st.subheader("💬 Genel Oyuncu Sohbeti")
    st.caption("Tüm oyuncularla anlık olarak sohbet edebilirsin. Mesajlar kalıcıdır!")

    # 🎨 Yuvarlak Profil Fotoğrafları ve Gri İkon Tasarımı için CSS
    st.markdown("""
        <style>
            .chat-avatar-img {
                width: 38px;
                height: 38px;
                border-radius: 50%;
                object-fit: cover;
                border: 2px solid #ff4b4b;
                margin-right: 10px;
                vertical-align: middle;
            }
            .chat-default-avatar {
                width: 38px;
                height: 38px;
                border-radius: 50%;
                background-color: #e0e0e0;
                color: #555555;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                font-size: 20px;
                margin-right: 10px;
                vertical-align: middle;
            }
        </style>
    """, unsafe_allow_html=True)

    # Sohbet akış alanı
    chat_container = st.container(height=400)

    # Son 50 mesajı çek
    messages = db.get_chat_messages(limit=50)

    with chat_container:
        if not messages:
            st.info("Henüz sohbet mesajı yok. İlk mesajı sen yaz!")
        else:
            for username, msg, msg_time in messages:
                avatar_data = get_user_avatar_base64(username)
                
                # Fotoğraf varsa base64 göster, yoksa gri insan ikonu göster
                if avatar_data:
                    avatar_html = f'<img src="{avatar_data}" class="chat-avatar-img">'
                else:
                    avatar_html = '<div class="chat-default-avatar">👤</div>'

                st.markdown(f"""
                    <div style="display: flex; align-items: flex-start; margin-bottom: 12px;">
                        <div>{avatar_html}</div>
                        <div>
                            <b>{username}</b> <span style="font-size: 0.75em; color: #888;">({msg_time})</span><br>
                            <span style="font-size: 0.95em;">{msg}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

    # Mesaj Girdisi
    prompt = st.chat_input("Mesajını yaz ve Enter'a bas...")
    if prompt:
        current_username = st.session_state.get("username", "Oyuncu")
        db.save_chat_message(current_username, prompt)
        st.rerun()