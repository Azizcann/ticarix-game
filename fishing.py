import streamlit as st

FISH_ITEMS = {
    "Sazan": {"price": 40, "xp": 10, "level": 1},
    "Alabalık": {"price": 120, "xp": 25, "level": 1},
    "Levrek": {"price": 350, "xp": 50, "level": 3},
    "Somon": {"price": 1000, "xp": 100, "level": 5},
    "Kalkan": {"price": 3000, "xp": 250, "level": 8},
    "Kılıç Balığı": {"price": 8500, "xp": 500, "level": 10}
}

def update_fishing_progress(current_t):
    pass

def render_fishing_tab(save_callback):
    st.header("🎣 Balıkçılık İskelesi")
    st.write("Denize açıl ve tuttuğun balıkları satarak sermayeni büyüt.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Balık Envanteri")
        total_fish_value = sum(st.session_state.fish_inventory[item] * FISH_ITEMS[item]["price"] for item in FISH_ITEMS)
        st.metric("Kasadaki Balık Değeri", f"{total_fish_value:,} TL")

        if st.button("Balıkları Pazarda Sat", use_container_width=True):
            if total_fish_value > 0:
                st.session_state.money += total_fish_value
                for item in FISH_ITEMS:
                    st.session_state.fish_inventory[item] = 0
                save_callback()
                st.success(f"{total_fish_value:,} TL balık satışı gerçekleştirildi!")
                st.rerun()
            else:
                st.warning("Satılacak balık yok!")

    with col2:
        st.subheader("Balık Türleri ve Fiyatları")
        for item, details in FISH_ITEMS.items():
            count = st.session_state.fish_inventory.get(item, 0)
            st.text(f"{item}: {details['price']} TL (Adet: {count})")

    st.divider()

    if st.button("🎣 Olta At", use_container_width=True):
        import random
        unlocked_fish = [k for k, v in FISH_ITEMS.items() if st.session_state.fish_level >= v["level"]]
        caught = random.choice(unlocked_fish)
        st.session_state.fish_inventory[caught] += 1
        st.session_state.fish_xp += FISH_ITEMS[caught]["xp"]
        
        req_xp = st.session_state.fish_level * 1000
        if st.session_state.fish_xp >= req_xp:
            st.session_state.fish_level += 1
            st.success(f"Tebrikler! Balıkçılık seviyen {st.session_state.fish_level} oldu!")

        save_callback()
        st.success(f"Olta takıldı ve bir {caught} tuttun!")
        st.rerun()