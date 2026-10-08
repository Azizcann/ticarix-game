import streamlit as st
from database import save_clan_to_db

def render_clan_tab(save_callback):
    st.header("🛡️ Klan Sistemi (La Familia & Diğerleri)")
    st.write("Klan kurarak ekibini topla, klan kasasından yüksek maaşlar al ve liderlik yarışına katıl.")

    clan_name_input = st.text_input("Klan Adı Belirle", value="La Familia")
    
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Klan Kurulumu")
        st.write("Klan Kurma Maliyeti: **50,000 TL**")
        if st.button("Klan Kur", use_container_width=True):
            if st.session_state.money >= 50000:
                st.session_state.money -= 50000
                st.session_state.user_clan = clan_name_input
                
                # Global klan sözlüğüne ekle
                if clan_name_input not in st.session_state.clans_db:
                    st.session_state.clans_db[clan_name_input] = {
                        "leader": st.session_state.username,
                        "treasury": 100000,
                        "members_count": 1
                    }
                    save_clan_to_db(clan_name_input, st.session_state.clans_db[clan_name_input])

                save_callback()
                st.success(f"Tebrikler, {clan_name_input} klanını kurdun!")
                st.rerun()
            else:
                st.error("Klan kurmak için yeterli paran yok! (Gereken: 50.000 TL)")

    with col2:
        st.subheader("Klan Bilgileri & Maaş")
        current_clan = st.session_state.get("user_clan", None)
        if current_clan:
            st.success(f"Aktif Klanın: {current_clan}")
            st.metric("Klan Üyesi Maaşı", "3,500 TL / Gün")
            
            if st.button("Klan Maaşını Çek", use_container_width=True):
                st.session_state.money += 3500
                save_callback()
                st.success("Klan kasasından 3,500 TL maaş alındı!")
                st.rerun()
        else:
            st.info("Herhangi bir klana üye değilsin.")

    st.divider()
    st.subheader("Aktif Klanlar Listesi")
    for c_name, c_data in st.session_state.clans_db.items():
        st.markdown(f"- **{c_name}** | Lider: {c_data.get('leader')} | Kasa: {c_data.get('treasury', 0):,} TL")