import streamlit as st
import time

# Güncellenmiş Maden Fiyatları
MINE_ITEMS = {
    "Kömür": {"price": 50, "xp": 10, "level": 1},
    "Bakır": {"price": 150, "xp": 25, "level": 1},
    "Demir": {"price": 400, "xp": 50, "level": 3},
    "Gümüş": {"price": 1200, "xp": 100, "level": 5},
    "Altın": {"price": 3500, "xp": 250, "level": 8},
    "Elmas": {"price": 10000, "xp": 500, "level": 10}
}

def update_mining_progress(current_t):
    # Arka plan maden ilerleme mantığı
    pass

def render_mining_tab(save_callback):
    st.header("⛏️ Madencilik Ocağı")
    st.write("Madencilik yaparak değerli madenler kazabilir ve bunları pazarda nakite dönüştürebilirsin.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Envanter & Kazanç")
        total_value = sum(st.session_state.mine_inventory[item] * MINE_ITEMS[item]["price"] for item in MINE_ITEMS)
        st.metric("Depodaki Madenlerin Değeri", f"{total_value:,} TL")

        if st.button("Tüm Madenleri Sat", use_container_width=True):
            if total_value > 0:
                st.session_state.money += total_value
                for item in MINE_ITEMS:
                    st.session_state.mine_inventory[item] = 0
                save_callback()
                st.success(f"{total_value:,} TL kazanç cüzdana eklendi!")
                st.rerun()
            else:
                st.warning("Satılacak madenin yok!")

    with col2:
        st.subheader("Maden Fiyat Listesi")
        for item, details in MINE_ITEMS.items():
            count = st.session_state.mine_inventory.get(item, 0)
            st.text(f"{item}: {details['price']} TL (Adet: {count})")

    st.divider()
    
    # Maden Kazma Simülasyon Butonu
    if st.button("🪨 Kazma Vur (Madensel Üretim)", use_container_width=True):
        # Örnek kazı mantığı (Rastgele bir maden düşürme)
        import random
        unlocked_items = [k for k, v in MINE_ITEMS.items() if st.session_state.mine_level >= v["level"]]
        found_item = random.choice(unlocked_items)
        st.session_state.mine_inventory[found_item] += 1
        st.session_state.mine_xp += MINE_ITEMS[found_item]["xp"]
        
        # Seviye Atlama Kontrolü
        required_xp = st.session_state.mine_level * 1000
        if st.session_state.mine_xp >= required_xp:
            st.session_state.mine_level += 1
            st.success(f"Tebrikler! Madencilik seviyeniz {st.session_state.mine_level} oldu!")

        save_callback()
        st.success(f"1 adet {found_item} buldun!")
        st.rerun()