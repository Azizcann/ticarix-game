import streamlit as st
import database as db

def render_chat_tab():
    """Oyuncular arası genel canlı sohbet panelini çizer."""
    st.subheader("💬 Genel Oyuncu Sohbeti")
    st.caption("Tüm oyuncularla anlık olarak sohbet edebilirsin.")

    # Sohbet akış alanı (Yüksekliği biraz dengeliyelim ki akış hızlı olsun)
    chat_container = st.container(height=380)

    # Sohbeti hafifletmek ve hızlandırmak için limiti 30'a düşürdük
    messages = db.get_chat_messages(limit=30)

    with chat_container:
        if not messages:
            st.info("Henüz sohbet mesajı yok. İlk mesajı sen yaz!")
        else:
            for username, msg, msg_time in messages:
                is_me = (username == st.session_state.get("username"))
                avatar = "😎" if is_me else "👤"
                
                with st.chat_message("assistant" if is_me else "user", avatar=avatar):
                    st.markdown(f"**{username}** <span style='font-size: 0.75em; color: #888;'>({msg_time})</span>", unsafe_allow_html=True)
                    st.write(msg)

    # Mesaj Girdisi
    prompt = st.chat_input("Mesajını yaz ve Enter'a bas...")
    if prompt:
        current_username = st.session_state.get("username", "Oyuncu")
        db.save_chat_message(current_username, prompt)
        st.rerun()