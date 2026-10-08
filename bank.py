import streamlit as st
import time

def render_bank_tab(save_callback):
    """Merkez Bankası, mevduat ve kredi işlemlerini yöneten arayüz."""
    st.subheader("🏦 Ticarix Merkez Bankası")
    
    col_info1, col_info2, col_info3 = st.columns(3)
    with col_info1:
        st.metric(label="📊 TCMB Politika Faizi", value=f"%{st.session_state.tcmb_policy_rate:.1f}")
    with col_info2:
        st.metric(label="📈 Bankadaki Mevduat", value=f"{int(st.session_state.bank_balance):,} TL")
    with col_info3:
        st.metric(label="📉 Aktif Kredi / Borç", value=f"{int(st.session_state.bank_debt):,} TL")

    st.info("⏰ **Zaman Algısı:** 1 Gerçek Saat = 1 Oyun Ayı (Faizler bu ölçekte bileşik olarak işler).")

    with st.expander("🔄 Merkez Bankası Piyasa Güncellemesi"):
        yeni_faiz = st.slider(
            "Politika Faizi Oranını Belirle (%)", 
            min_value=10.0, 
            max_value=70.0, 
            value=float(st.session_state.tcmb_policy_rate), 
            step=0.5
        )
        if st.button("Faiz Oranını Güncelle", use_container_width=True):
            st.session_state.tcmb_policy_rate = yeni_faiz
            save_callback()
            st.success(f"Merkez Bankası politika faizi %{yeni_faiz} olarak güncellendi!")
            st.rerun()

    st.divider()
    
    col_b1, col_b2 = st.columns(2)
    
    with col_b1:
        st.markdown("#### Para İşlemleri (Mevduat)")
        yatirilan = st.number_input("Yatırılacak Tutar (TL)", min_value=0, max_value=int(st.session_state.money), step=100, key="yatir_inp")
        if st.button("Bankaya Para Yatır (Faiz Kazan)", use_container_width=True):
            if yatirilan > 0 and st.session_state.money >= yatirilan:
                st.session_state.money -= yatirilan
                st.session_state.bank_balance += yatirilan
                save_callback()
                st.success("Para bankaya yatırıldı, bileşik faiz işlemeye başladı.")
                st.rerun()
            else:
                st.warning("Yetersiz nakit bakiye!")

        cekilen = st.number_input("Çekilecek Tutar (TL)", min_value=0, max_value=int(st.session_state.bank_balance), step=100, key="cek_inp")
        if st.button("Bankadan Para Çek", use_container_width=True):
            if cekilen > 0 and st.session_state.bank_balance >= cekilen:
                st.session_state.bank_balance -= cekilen
                st.session_state.money += cekilen
                save_callback()
                st.success("Para bankadan çekildi.")
                st.rerun()
            else:
                st.warning("Bankada yeterli bakiye yok!")

    with col_b2:
        st.markdown("#### Kredi & Borç Yönetimi")
        kredi_tutari = st.number_input("Çekilecek Kredi (TL)", min_value=0, max_value=5000000, step=10000, key="kredi_inp")
        if st.button("Kredi Çek (Faizli Geri Ödemeli)", use_container_width=True):
            if kredi_tutari > 0:
                st.session_state.money += kredi_tutari
                st.session_state.bank_debt += kredi_tutari
                save_callback()
                st.success("Kredi çekildi. Borca saatlik ölçekli aylık faiz işlemeye başladı!")
                st.rerun()

        max_borc_odeme = int(min(st.session_state.money, st.session_state.bank_debt))
        borc_odeme = st.number_input("Ödenecek Tutar (TL)", min_value=0, max_value=max_borc_odeme, step=100, key="borc_inp")
        if st.button("Borcu Kapat / Öde", use_container_width=True):
            if borc_odeme > 0 and st.session_state.money >= borc_odeme:
                st.session_state.money -= borc_odeme
                st.session_state.bank_debt -= borc_odeme
                if st.session_state.bank_debt < 0:
                    st.session_state.bank_debt = 0
                save_callback()
                st.success("Borç başarıyla ödendi.")
                st.rerun()
            else:
                st.warning("Geçersiz tutar veya yetersiz nakit!")

def update_bank_interest(current_time):
    """Arka planda banka mevduat ve kredi faizlerini işler."""
    bank_elapsed = current_time - st.session_state.get('last_bank_interest_time', current_time)
    if bank_elapsed >= 5:
        real_seconds = bank_elapsed
        st.session_state.last_bank_interest_time = current_time
        
        game_months_passed = (real_seconds / 3600.0)
        annual_rate = st.session_state.tcmb_policy_rate / 100.0
        monthly_deposit_rate = annual_rate / 12.0
        monthly_debt_rate = (annual_rate + 0.05) / 12.0
        
        if st.session_state.bank_balance > 0:
            st.session_state.bank_balance = int(st.session_state.bank_balance * ((1.0 + monthly_deposit_rate) ** game_months_passed))
            
        if st.session_state.bank_debt > 0:
            st.session_state.bank_debt = int(st.session_state.bank_debt * ((1.0 + monthly_debt_rate) ** game_months_passed))