import streamlit as st
import database as db

def render_leaderboard_tab():
    st.header("🏆 Ticarix Liderlik Tablosu")

    # İç içe tab yerine Streamlit uyumlu radio filtresi
    sub_category = st.radio(
        "Sıralama Türünü Seçin:",
        ["👤 En Zengin Oyuncular (Top 100)", "🛡️ Klan Sıralaması"],
        horizontal=True
    )
    st.divider()

    # --- OYUNCU SERVET SIRALAMASI ---
    if sub_category == "👤 En Zengin Oyuncular (Top 100)":
        st.subheader("💰 Oyuncu Servet Sıralaması")
        st.caption("Servet = Nakit Para + Banka Mevduatı + Dükkan Yatırım Değeri - Banka Borcu")
        
        players = db.get_top_players(limit=100)

        if not players:
            st.info("Henüz sıralamada gösterilecek oyuncu bulunmuyor.")
        else:
            table_data = []
            for idx, p in enumerate(players, start=1):
                rank_str = "🥇 1" if idx == 1 else "🥈 2" if idx == 2 else "🥉 3" if idx == 3 else f"#{idx}"

                table_data.append({
                    "Sıra": rank_str,
                    "Oyuncu": p["username"],
                    "Klan": p["clan"],
                    "Toplam Servet": f"{p['total_wealth']:,} TL",
                    "Nakit": f"{p['money']:,} TL",
                    "Banka Mevduat": f"{p['bank']:,} TL",
                    "Dükkan Değeri": f"{p['shop_value']:,} TL"
                })

            st.dataframe(table_data, use_container_width=True, hide_index=True)

    # --- KLAN SIRALAMASI ---
    elif sub_category == "🛡️ Klan Sıralaması":
        st.subheader("🛡️ En Güçlü Klanlar")
        st.caption("Klanlar toplam kazandıkları Klan XP'ye göre sıralanır.")

        clans = db.get_top_clans(limit=100)

        if not clans:
            st.info("Henüz kurulmuş bir klan bulunmuyor.")
        else:
            clan_table = []
            for idx, c in enumerate(clans, start=1):
                rank_str = "🥇 1" if idx == 1 else "🥈 2" if idx == 2 else "🥉 3" if idx == 3 else f"#{idx}"

                clan_table.append({
                    "Sıra": rank_str,
                    "Klan Adı": c["clan_name"],
                    "Lider": c["leader"],
                    "Üye Sayısı": c["member_count"],
                    "Klan XP": f"{c['xp']:,} XP"
                })

            st.dataframe(clan_table, use_container_width=True, hide_index=True)