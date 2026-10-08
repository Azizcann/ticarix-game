import streamlit as st

def update_shop_income(current_t):
    # Pasif gelir birikim mekanizması
    pass

def render_shops_tab(save_callback):
    st.header("🏢 Dükkanlar ve İşletmeler")
    st.write("Pasif gelir elde etmek için işletme satın al ve ciro topla.")

    shops = st.session_state.shops

    cols = st.columns(len(shops))
    for i, (key, shop) in enumerate(shops.items()):
        with cols[i]:
            st.subheader(shop["name"])
            st.write(f"Maliyet: **{shop['cost']:,} TL**")
            st.write(f"Dakikalık Gelir: **{shop['income']:,} TL**")
            st.write(f"Sahip Olunan: **{shop['count']} Adet**")

            if st.button(f"Satın Al ({shop['cost']:,} TL)", key=f"buy_{key}", use_container_width=True):
                if st.session_state.money >= shop["cost"]:
                    st.session_state.money -= shop["cost"]
                    shop["count"] += 1
                    save_callback()
                    st.success(f"1 adet {shop['name']} satın alındı!")
                    st.rerun()
                else:
                    st.error("Yetersiz nakit para!")

    st.divider()
    
    # Toplu Gelir Toplama Alanı
    accumulated = st.session_state.get("accumulated_shop_money", 0)
    st.metric("Biriken İşletme Cirosu", f"{accumulated:,} TL")
    if st.button("Ciro Hak Edişini Topla", use_container_width=True):
        if accumulated > 0:
            st.session_state.money += accumulated
            st.session_state.accumulated_shop_money = 0
            save_callback()
            st.success("İşletme ciroları kasaya aktarıldı!")
            st.rerun()
        else:
            st.info("Toplanacak ciro bulunmuyor.")