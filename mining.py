import streamlit as st
import time
import random
from clan import add_clan_xp

ORE_TYPES = [
    ("Kömür", 20, 1), ("Bakır", 50, 1), ("Demir", 120, 3),
    ("Gümüş", 300, 5), ("Altın", 800, 8), ("Elmas", 2000, 10)
]

def render_mining_tab(save_callback):
    """Madencilik sekmesini ve üretim mantığını çizer."""
    st.subheader("⛏️ Madencilik Sahası")
    
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.metric(label="Madencilik Seviyesi", value=f"Level {st.session_state.mine_level}")
        st.progress(
            st.session_state.mine_xp / (st.session_state.mine_level * 100), 
            text=f"XP: {st.session_state.mine_xp} / {st.session_state.mine_level * 100}"
        )
    with col_m2:
        if st.session_state.active_job == "mining":
            kalan_sure_m = 20 - int(time.time() - st.session_state.mine_last_time)
            st.metric(label="Sonraki Otomatik Kazım", value=f"{max(0, kalan_sure_m)} saniye")
        else:
            st.metric(label="Durum", value="Görevde Değil (Beklemede)")

    if st.session_state.active_job != "mining":
        if st.button("🚀 Madencilik Görevine Başla", use_container_width=True):
            st.session_state.active_job = "mining"
            st.session_state.mine_last_time = time.time()
            save_callback()
            st.success("Madencilik görevine başlandı!")
            st.rerun()
    else:
        if st.button("⏹️ Görevi Durdur / Dinlen", use_container_width=True):
            st.session_state.active_job = None
            save_callback()
            st.warning("Madencilik görevi durduruldu.")
            st.rerun()

    st.markdown("### 📦 Gizli Envanter & Madenler")
    toplam_maden_degeri = 0
    for isim, fiyat, req_lvl in ORE_TYPES:
        adet = st.session_state.mine_inventory[isim]
        bonuslu_fiyat = fiyat * (1 + (st.session_state.mine_level - 1) * 0.02)
        toplam_maden_degeri += adet * bonuslu_fiyat
        st.text(f"• {isim}: {adet} Adet (Birim: {bonuslu_fiyat:,.1f} TL)")

    st.info(f"💡 Seviye Bonusu Aktif: **%{(st.session_state.mine_level - 1) * 2} Ekstra Kazanç**")

    if st.button("💰 Madenleri Hesaplat ve Sat", use_container_width=True):
        if toplam_maden_degeri > 0:
            st.session_state.money += toplam_maden_degeri
            satilan_ozet = f"Madenler başarıyla satıldı! Kasaya **{toplam_maden_degeri:,.2f} TL** eklendi."
            for isim in st.session_state.mine_inventory:
                st.session_state.mine_inventory[isim] = 0
            save_callback()
            st.session_state.sale_message = satilan_ozet
            st.rerun()
        else:
            st.warning("Satılacak hiç madeniniz yok!")

def update_mining_progress(current_time):
    """Arka planda madencilik üretimini ve seviye atlamayı hesaplar."""
    if st.session_state.active_job == "mining":
        mine_elapsed = current_time - st.session_state.mine_last_time
        if mine_elapsed >= 20:
            ticks = int(mine_elapsed // 20)
            st.session_state.mine_last_time = current_time - (mine_elapsed % 20)
            for _ in range(ticks):
                uygun_madenler = [o for o in ORE_TYPES if st.session_state.mine_level >= o[2]]
                secilen_maden = random.choices(
                    uygun_madenler, 
                    weights=[max(1, 10 - i*1.5) for i in range(len(uygun_madenler))][::-1]
                )[0][0]
                st.session_state.mine_inventory[secilen_maden] += 1
                st.session_state.mine_xp += 15
                add_clan_xp(st.session_state.get("username", "Oyuncu"), 15)
    else:
        st.session_state.mine_last_time = current_time

    mine_req_xp = st.session_state.mine_level * 100
    if st.session_state.mine_xp >= mine_req_xp:
        st.session_state.mine_xp -= mine_req_xp
        st.session_state.mine_level += 1