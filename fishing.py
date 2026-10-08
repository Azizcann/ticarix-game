import streamlit as st
import time
import random
from clan import add_clan_xp

FISH_TYPES = [
    ("Sazan", 20, 1), ("Alabalık", 50, 1), ("Levrek", 120, 3),
    ("Somon", 300, 5), ("Kalkan", 800, 8), ("Kılıç Balığı", 2000, 10)
]

def render_fishing_tab(save_callback):
    """Balıkçılık sekmesini ve avlanma mantığını çizer."""
    st.subheader("🎣 Balıkçılık İskelesi")
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        st.metric(label="Balıkçılık Seviyesi", value=f"Level {st.session_state.fish_level}")
        st.progress(
            st.session_state.fish_xp / (st.session_state.fish_level * 100), 
            text=f"XP: {st.session_state.fish_xp} / {st.session_state.fish_level * 100}"
        )
    with col_f2:
        if st.session_state.active_job == "fishing":
            kalan_sure_f = 20 - int(time.time() - st.session_state.fish_last_time)
            st.metric(label="Sonraki Otomatik Av", value=f"{max(0, kalan_sure_f)} saniye")
        else:
            st.metric(label="Durum", value="Görevde Değil (Beklemede)")

    if st.session_state.active_job != "fishing":
        if st.button("🚀 Balıkçılık Görevine Başla", use_container_width=True):
            st.session_state.active_job = "fishing"
            st.session_state.fish_last_time = time.time()
            save_callback()
            st.success("Balıkçılık görevine başlandı!")
            st.rerun()
    else:
        if st.button("⏹️ Görevi Durdur / Dinlen", use_container_width=True):
            st.session_state.active_job = None
            save_callback()
            st.warning("Balıkçılık görevi durduruldu.")
            st.rerun()

    st.markdown("### 🐟 Gizli Envanter & Balıklar")
    toplam_balik_degeri = 0
    for isim, fiyat, req_lvl in FISH_TYPES:
        adet = st.session_state.fish_inventory[isim]
        bonuslu_fiyat = fiyat * (1 + (st.session_state.fish_level - 1) * 0.02)
        toplam_balik_degeri += adet * bonuslu_fiyat
        st.text(f"• {isim}: {adet} Adet (Birim: {bonuslu_fiyat:,.1f} TL)")

    st.info(f"💡 Seviye Bonusu Aktif: **%{(st.session_state.fish_level - 1) * 2} Ekstra Kazanç**")

    if st.button("🐟 Balıkları Hesaplat ve Sat", use_container_width=True):
        if toplam_balik_degeri > 0:
            st.session_state.money += toplam_balik_degeri
            satilan_ozet = f"Balıklar başarıyla satıldı! Kasaya **{toplam_balik_degeri:,.2f} TL** eklendi."
            for isim in st.session_state.fish_inventory:
                st.session_state.fish_inventory[isim] = 0
            save_callback()
            st.session_state.sale_message = satilan_ozet
            st.rerun()
        else:
            st.warning("Satılacak hiç balığınız yok!")

def update_fishing_progress(current_time):
    """Arka planda balıkçılık üretimini ve seviye atlamayı hesaplar."""
    if st.session_state.active_job == "fishing":
        fish_elapsed = current_time - st.session_state.fish_last_time
        if fish_elapsed >= 20:
            ticks = int(fish_elapsed // 20)
            st.session_state.fish_last_time = current_time - (fish_elapsed % 20)
            for _ in range(ticks):
                uygun_baliklar = [f for f in FISH_TYPES if st.session_state.fish_level >= f[2]]
                secilen_balik = random.choices(
                    uygun_baliklar, 
                    weights=[max(1, 10 - i*1.5) for i in range(len(uygun_baliklar))][::-1]
                )[0][0]
                st.session_state.fish_inventory[secilen_balik] += 1
                st.session_state.fish_xp += 15
                add_clan_xp(st.session_state.get("username", "Oyuncu"), 15)
    else:
        st.session_state.fish_last_time = current_time

    fish_req_xp = st.session_state.fish_level * 100
    if st.session_state.fish_xp >= fish_req_xp:
        st.session_state.fish_xp -= fish_req_xp
        st.session_state.fish_level += 1