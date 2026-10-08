import streamlit as st
import json
from database import register_user, login_user

def render_auth_screen():
    """Giriş ve kayıt ekranını çizer."""
    st.title("🪙 Ticarix - Giriş Sistemi")
    st.caption("Çok oyunculu dünyaya katılmak için giriş yap veya kayıt ol.")
    
    auth_tab1, auth_tab2 = st.tabs(["🔑 Giriş Yap", "📝 Kayıt Ol"])
    
    with auth_tab1:
        st.subheader("Hesabına Giriş Yap")
        login_identifier = st.text_input("Kullanıcı Adı veya E-posta", key="login_u")
        login_pass = st.text_input("Şifre", type="password", key="login_p")
        
        if st.button("Giriş Yap", use_container_width=True):
            if login_identifier and login_pass:
                user = login_user(login_identifier, login_pass)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user_id = user[0]
                    st.session_state.username = user[1]
                    
                    # 🔗 URL parametresine ID'yi sabitle (F5 atılsa bile anında okunur)
                    st.query_params["uid"] = str(user[0])
                    
                    g_data = json.loads(user[2])
                    for key, val in g_data.items():
                        st.session_state[key] = val
                        
                    st.success(f"Hoş geldin, {user[1]}! Giriş başarılı.")
                    st.rerun()
                else:
                    st.error("Hatalı kullanıcı adı/e-posta veya şifre!")
            else:
                st.warning("Lütfen tüm alanları doldurun!")

    with auth_tab2:
        st.subheader("Yeni Hesap Oluştur")
        reg_username = st.text_input("Kullanıcı Adı", key="reg_u")
        reg_email = st.text_input("E-posta Adresi", key="reg_e")
        reg_pass = st.text_input("Şifre", type="password", key="reg_p")
        reg_pass_confirm = st.text_input("Şifre (Tekrar)", type="password", key="reg_p2")
        
        if st.button("Kayıt Ol", use_container_width=True):
            if reg_username and reg_email and reg_pass:
                if reg_pass != reg_pass_confirm:
                    st.error("Şifreler birbiriyle uyuşmuyor!")
                else:
                    success, message = register_user(reg_username, reg_email, reg_pass)
                    if success:
                        st.success(message + " Şimdi 'Giriş Yap' sekmesinden giriş yapabilirsin.")
                    else:
                        st.error(message)
            else:
                st.warning("Lütfen tüm alanları doldurun!")