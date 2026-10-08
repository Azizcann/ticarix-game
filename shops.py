import streamlit as st
import time

def render_shops_tab(save_callback):
    """Pasif gelir getiren dükkanların yönetim, biriken para toplama ve satın alım paneli."""
    st.subheader("🏢 Ticarix İşletmeler & Dükkanlar")
    st.info("Dükkanlar arka planda dakikalık olarak pasif gelir üretir. Biriken paraları dilediğin zaman toplayabilirsin!")

    # Biriken pasif para havuzu için session state kontrolü
    if "accumulated_shop_money" not in st.session_state:
        st.session_state.accumulated_shop_money = 0

    # Klan bonusunu hesapla
    clan_bonus = 1.0 + (st.session_state.get('clan_members', 0) * 0.05)

    # 💰 BİRİKEN PARA TOPLAMA KUTUSU
    if st.session_state.accumulated_shop_money > 0:
        st.success(f"📦 Dükkanlarda toplanmayı bekleyen birikmiş kasa: **{int(st.session_state.accumulated_shop_money):,} TL**")
        if st.button("📥 Biriken Paraları Kasaya Aktar", use_container_width=True, type="primary"):
            toplanan = int(st.session_state.accumulated_shop_money)
            st.session_state.money += toplanan
            st.session_state.accumulated_shop_money = 0
            save_callback()
            st.success(f"Başarıyla {toplanan:,} TL cüzdana aktarıldı!")
            st.rerun()
    else:
        st.info("📦 Dükkan Kasası: Henüz biriken para yok, dükkanlar üretim yapıyor...")

    st.write("---")

    if "shops" not in st.session_state:
        st.session_state.shops = {}

    for shop_key, shop_data in st.session_state.shops.items():
        st.markdown(f"### {shop_data['name']}")
        col_s1, col_s2, col_s3 = st.columns(3)
        
        # Fiyatı adet arttıkça ölçeklendir, geliri dakikalık bazda hesapla
        guncel_maliyet = int(shop_data['cost'] * (1.15 ** shop_data['count']))
        guncel_gelir_dakikalik = int(shop_data['income'] * shop_data['count'] * clan_bonus)
        
        with col_s1:
            st.metric(label="Sahip Olunan Adet", value=f"{shop_data['count']} Adet")
        with col_s2:
            st.metric(label="Pasif Gelir / Dakika", value=f"{guncel_gelir_dakikalik:,} TL")
        with col_s3:
            st.metric(label="Sonraki Dükkan Maliyeti", value=f"{guncel_maliyet:,} TL")

        if st.button(f"🛒 {shop_data['name']} Satın Al", key=f"buy_{shop_key}", use_container_width=True):
            if st.session_state.money >= guncel_maliyet:
                st.session_state.money -= guncel_maliyet
                shop_data['count'] += 1
                save_callback()
                st.success(f"1 adet {shop_data['name']} başarıyla satın alındı!")
                st.rerun()
            else:
                st.warning("Yetersiz nakit bakiye!")
        st.divider()

def update_shop_income(current_time):
    """Arka planda dükkanların pasif gelirlerini dakikalık orana göre biriken kasa havuzuna ekler."""
    if 'last_shop_income_time' not in st.session_state:
        st.session_state.last_shop_income_time = current_time

    if 'accumulated_shop_money' not in st.session_state:
        st.session_state.accumulated_shop_money = 0

    shop_elapsed = current_time - st.session_state.last_shop_income_time
    if shop_elapsed >= 1: # Her 1 saniyede bir akıcı şekilde hesaplayıp ekler
        real_seconds = shop_elapsed
        
        minutes_passed = real_seconds / 60.0
        clan_bonus = 1.0 + (st.session_state.get('clan_members', 0) * 0.05)
        
        toplam_pasif = 0
        if "shops" in st.session_state:
            for shop_key, shop_data in st.session_state.shops.items():
                guncel_gelir_dakikalik = shop_data['income'] * shop_data['count'] * clan_bonus
                toplam_pasif += guncel_gelir_dakikalik * minutes_passed
                
        if toplam_pasif > 0:
            st.session_state.accumulated_shop_money += toplam_pasif
            
        st.session_state.last_shop_income_time = current_time - (shop_elapsed % 1)