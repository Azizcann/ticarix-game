import streamlit as st
from database import save_clan_to_db, delete_clan_from_db, load_all_clans

def add_clan_xp(username, xp_amount):
    """Madencilik veya Balıkçılıkta kazanılan XP'nin %25'ini klana ve oyuncunun klan birikimine aktarır."""
    if "user_clan" in st.session_state and st.session_state.user_clan:
        aktif_klan = st.session_state.user_clan
        
        # Güncel klan verilerini veritabanından çek
        st.session_state.clans_db = load_all_clans()
        
        if aktif_klan in st.session_state.clans_db:
            klan_bilgi = st.session_state.clans_db[aktif_klan]
            
            current_username = st.session_state.get("username", "Oyuncu")
            target_user = username if username and username != "Oyuncu" else current_username
                
            klan_nakli = int(xp_amount * 0.25)
            
            if klan_nakli > 0:
                klan_bilgi["xp"] = klan_bilgi.get("xp", 0) + klan_nakli
                
                if "member_xp_progress" not in klan_bilgi:
                    klan_bilgi["member_xp_progress"] = {}
                
                mevcut_bireysel_xp = klan_bilgi["member_xp_progress"].get(target_user, 0)
                klan_bilgi["member_xp_progress"][target_user] = mevcut_bireysel_xp + klan_nakli
                
                # Veritabanına anında kalıcı olarak kaydet
                save_clan_to_db(aktif_klan, klan_bilgi)

def get_sorted_clans():
    """Klanları veritabanından çekip Klan XP'sine göre büyükten küçüğe sıralar."""
    st.session_state.clans_db = load_all_clans()
    clans_list = list(st.session_state.clans_db.items())
    # XP değerine göre sırala
    clans_list.sort(key=lambda x: x[1].get("xp", 0), reverse=True)
    return clans_list

def render_clan_tab(save_callback):
    """Klan yönetim, kurma, katılma ve klan içi sekmelerin ana paneli."""
    st.subheader("🛡️ Klanlar & Birlik Sistemi")

    if "user_clan" not in st.session_state:
        st.session_state.user_clan = None  
    
    current_username = st.session_state.get("username", "Oyuncu")
    sorted_clans = get_sorted_clans()

    if not st.session_state.user_clan:
        st.info("Henüz bir klana üye değilsin. Yeni bir klan kurabilir veya mevcut klanlara katılarak bonuslar kazanabilirsin!")
        
        tab_kur, tab_katil = st.tabs(["🏗️ Klan Kur", "🤝 Klana Katıl"])
        
        with tab_kur:
            st.write("### Yeni Klan Oluştur")
            yeni_klan_adi = st.text_input("Klan Adı", placeholder="Örn: Levantenler")
            kurulus_maliyeti = 50000  # Klan kurma ücreti 50.000 TL
            st.caption(f"Klan Kurma Maliyeti: **{kurulus_maliyeti:,} TL**")
            
            if st.button("Klanı Kur ve Lider Ol", use_container_width=True, type="primary"):
                if not yeni_klan_adi.strip():
                    st.warning("Lütfen geçerli bir klan adı gir!")
                elif st.session_state.get("money", 0) < kurulus_maliyeti:
                    st.error("Yeterli nakit paran yok! (Gerekli: 50,000 TL)")
                elif yeni_klan_adi in st.session_state.clans_db:
                    st.error("Bu isimde bir klan zaten mevcut!")
                else:
                    st.session_state.money -= kurulus_maliyeti
                    yeni_klan_verisi = {
                        "owner": current_username,
                        "members": [current_username],
                        "xp": 100,
                        "treasury": 0,
                        "salary_active": True,
                        "target_xp": 100,
                        "salary_amount": 3500,  # Varsayılan üye maaşı 3.500 TL
                        "member_xp_progress": {current_username: 0}
                    }
                    # Veritabanına kaydet
                    save_clan_to_db(yeni_klan_adi, yeni_klan_verisi)
                    st.session_state.clans_db[yeni_klan_adi] = yeni_klan_verisi
                    
                    st.session_state.user_clan = yeni_klan_adi
                    st.session_state.clan_members = 1
                    save_callback()
                    st.success(f"Tebrikler! '{yeni_klan_adi}' klanını kurdun ve lideri oldun!")
                    st.rerun()

        with tab_katil:
            st.write("### Aktif Klanlar Sıralaması")
            if not sorted_clans:
                st.warning("Şu anda kurulmuş hiçbir klan bulunmuyor. İlk klanı sen kurabilirsin!")
            else:
                for idx, (k_adi, k_data) in enumerate(sorted_clans, start=1):
                    if idx == 1:
                        rank_str = "🥇 1"
                    elif idx == 2:
                        rank_str = "🥈 2"
                    elif idx == 3:
                        rank_str = "🥉 3"
                    else:
                        rank_str = f"#{idx}"

                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**{rank_str} {k_adi}** | Lider: *{k_data.get('owner', 'Bilinmiyor')}* | Üye: {len(k_data.get('members', []))} | XP: **{k_data.get('xp', 0):,} XP**")
                    with col2:
                        if st.button(f"Katıl", key=f"join_{k_adi}", use_container_width=True):
                            members = k_data.get("members", [])
                            if current_username not in members:
                                members.append(current_username)
                                k_data["members"] = members
                            if "member_xp_progress" not in k_data:
                                k_data["member_xp_progress"] = {}
                            if current_username not in k_data["member_xp_progress"]:
                                k_data["member_xp_progress"][current_username] = 0
                                
                            save_clan_to_db(k_adi, k_data)
                            
                            st.session_state.user_clan = k_adi
                            st.session_state.clan_members = len(k_data["members"])
                            save_callback()
                            st.success(f"Başarıyla {k_adi} klanına katıldın!")
                            st.rerun()
        return

    aktif_klan = st.session_state.user_clan
    
    if aktif_klan not in st.session_state.clans_db:
        st.session_state.user_clan = None
        st.rerun()

    klan_bilgi = st.session_state.clans_db[aktif_klan]
    is_owner = (klan_bilgi.get("owner") == current_username)

    if "salary_active" not in klan_bilgi: klan_bilgi["salary_active"] = True
    if "target_xp" not in klan_bilgi: klan_bilgi["target_xp"] = 100
    if "salary_amount" not in klan_bilgi: klan_bilgi["salary_amount"] = 3500
    if "member_xp_progress" not in klan_bilgi: klan_bilgi["member_xp_progress"] = {}
    if current_username not in klan_bilgi["member_xp_progress"]:
        klan_bilgi["member_xp_progress"][current_username] = 0

    st.markdown(f"""
        <div style="background-color: #1e1e2f; padding: 15px; border-radius: 10px; border: 1px solid #3f3f7f; margin-bottom: 20px; text-align: center;">
            <h2 style="margin: 0; color: #ffca28;">🛡️ {aktif_klan}</h2>
            <p style="margin: 5px 0 0 0; color: #b0bec5; font-size: 16px;">Klan Lideri: <b style="color: #4caf50;">{klan_bilgi.get('owner', 'Bilinmiyor')}</b> | Klan Toplam XP: <b style="color: #00bcd4;">{klan_bilgi.get('xp', 0):,} XP</b></p>
        </div>
    """, unsafe_allow_html=True)

    tab_titles = ["👥 Üye Listesi & XP", "💰 Maaş & Kasa", "📜 Klanlar Sıralaması"]
    if is_owner:
        tab_titles.append("⚙️ Yönetim")

    tabs = st.tabs(tab_titles)

    # 1. SEKME: ÜYE LİSTESİ & XP
    with tabs[0]:
        st.write("### Klan Üyeleri ve Kazandıkları XP'ler")
        for idx, member in enumerate(klan_bilgi.get("members", []), 1):
            rol = "👑 Lider" if member == klan_bilgi.get("owner") else "🛡️ Üye"
            uye_xp = klan_bilgi["member_xp_progress"].get(member, 0)
            st.write(f"{idx}. **{member}** — *{rol}* | Bireysel İlerleme XP: **{uye_xp:,} XP**")
        
        st.divider()
        
        if not is_owner:
            if st.button("🚪 Klandan Ayrıl", use_container_width=True, type="secondary"):
                if current_username in klan_bilgi["members"]:
                    klan_bilgi["members"].remove(current_username)
                if current_username in klan_bilgi["member_xp_progress"]:
                    del klan_bilgi["member_xp_progress"][current_username]
                
                save_clan_to_db(aktif_klan, klan_bilgi)
                
                st.session_state.user_clan = None
                st.session_state.clan_members = 0
                save_callback()
                st.warning(f"'{aktif_klan}' klanından ayrıldın.")
                st.rerun()
        else:
            st.info("💡 Klan lideri olduğun için klandan doğrudan ayrılamazsın. Yönetim sekmesinden klanı silebilirsin.")

    # 2. SEKME: MAAŞ & KASA
    with tabs[1]:
        st.write("### Klan Kasası & Maaş Al")
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.metric("Klan Kasası", f"{int(klan_bilgi.get('treasury', 0)):,} TL")
        with col_m2:
            st.metric("Maaş Durumu", "🟢 Aktif" if klan_bilgi.get("salary_active", True) else "🔴 Kapalı")
        
        st.divider()
        
        target_xp = klan_bilgi.get("target_xp", 100)
        salary_amount = int(klan_bilgi.get("salary_amount", 3500))
        user_current_p = klan_bilgi["member_xp_progress"].get(current_username, 0)
        
        st.write(f"- **Hedeflenen Klan XP Eşiği:** {target_xp:,} XP")
        st.write(f"- **Mevcut XP İlerlemen:** {user_current_p:,} / {target_xp:,} XP")
        st.write(f"- **Üye Başına Maaş Miktarı:** {salary_amount:,} TL")

        salary_active = klan_bilgi.get("salary_active", True)
        treasury = klan_bilgi.get("treasury", 0)
        can_claim = salary_active and (user_current_p >= target_xp) and (treasury >= salary_amount)

        if not salary_active:
            st.warning("⚠️ Klan lideri şu anda maaş dağıtımını kapatmıştır.")
        elif treasury < salary_amount:
            st.warning("⚠️ Klan kasasında yeterli bütçe bulunmuyor! Liderin kasaya para yatırması gerekiyor.")
        elif user_current_p < target_xp:
            st.info(f"⏳ Maaş alabilmek için {target_xp - user_current_p:,} XP daha kazanman gerekiyor.")
        else:
            st.success("🎉 Hedef XP'ye ulaştın! Maaşını alabilirsin.")

        if st.button("💰 Maaş Al", use_container_width=True, type="primary", disabled=not can_claim):
            klan_bilgi["treasury"] -= salary_amount
            if "bank_balance" in st.session_state:
                st.session_state.bank_balance += salary_amount
            else:
                st.session_state.money += salary_amount
            
            klan_bilgi["member_xp_progress"][current_username] -= target_xp
            save_clan_to_db(aktif_klan, klan_bilgi)
            save_callback()
            st.success(f"Tebrikler! Klan kasasından **{salary_amount:,} TL** maaş aldın ve banka hesabına yatırıldı!")
            st.rerun()

    # 3. SEKME: KLANLAR SIRALAMASI
    with tabs[2]:
        st.write("### 🏆 Canlı Klan XP Sıralaması")
        st.caption("Klanlar kazandıkları toplam Klan XP'sine göre sıralanır.")
        
        if not sorted_clans:
            st.write("Henüz aktif klan bulunmuyor.")
        else:
            clan_table_data = []
            for idx, (k_adi, k_dat) in enumerate(sorted_clans, start=1):
                if idx == 1:
                    rank_str = "🥇 1"
                elif idx == 2:
                    rank_str = "🥈 2"
                elif idx == 3:
                    rank_str = "🥉 3"
                else:
                    rank_str = f"#{idx}"

                owner_str = k_dat.get("owner") or k_dat.get("leader", "Bilinmiyor")
                member_cnt = len(k_dat.get("members", []))
                xp_val = k_dat.get("xp", 0)

                clan_table_data.append({
                    "Sıra": rank_str,
                    "Klan Adı": k_adi,
                    "Lider": owner_str,
                    "Üye Sayısı": member_cnt,
                    "Toplam XP": f"{xp_val:,} XP"
                })

            st.dataframe(clan_table_data, use_container_width=True, hide_index=True)

    # 4. SEKME: YÖNETİM (YALNIZCA LİDER)
    if is_owner:
        with tabs[3]:
            st.write("### ⚙️ Klan Yönetim Paneli (Kurucu Özel)")
            st.warning("Bu sekmeyi yalnızca klan kurucusu görüntüler ve yönetebilir.")
            
            st.write("#### 💰 Kasa Finansmanı")
            yatirilacak = int(st.number_input("Klan Kasasına Para Ekle (TL)", min_value=100, step=500))
            if st.button("Kasaya Para Aktar", use_container_width=True):
                if st.session_state.money >= yatirilacak:
                    st.session_state.money -= yatirilacak
                    klan_bilgi["treasury"] += yatirilacak
                    save_clan_to_db(aktif_klan, klan_bilgi)
                    save_callback()
                    st.success(f"Klan kasasına {yatirilacak:,} TL aktarıldı!")
                    st.rerun()
                else:
                    st.error("Cüzdanında bu kadar nakit yok!")
            
            st.divider()
            st.write("#### 🎛️ Maaş ve Hedef Ayarları")
            
            yeni_salary_active = st.toggle("Maaş Dağıtımı Aktif mi?", value=klan_bilgi.get("salary_active", True))
            yeni_target_db = int(st.number_input("Hedef Klan XP Eşiği", min_value=10, value=int(klan_bilgi.get("target_xp", 100)), step=50))
            yeni_salary_amount = int(st.number_input("Üye Başına Verilecek Maaş (TL)", min_value=0, value=int(klan_bilgi.get("salary_amount", 3500)), step=500))

            if st.button("Ayarları Güncelle", use_container_width=True):
                klan_bilgi["salary_active"] = yeni_salary_active
                klan_bilgi["target_xp"] = yeni_target_db
                klan_bilgi["salary_amount"] = yeni_salary_amount
                save_clan_to_db(aktif_klan, klan_bilgi)
                save_callback()
                st.success("Klan maaş ve hedef ayarları başarıyla güncellendi!")
                st.rerun()

            st.divider()
            
            if st.button("🗑️ Klanı Tamamen Sil", use_container_width=True, type="primary"):
                delete_clan_from_db(aktif_klan)
                st.session_state.user_clan = None
                st.session_state.clan_members = 0
                save_callback()
                st.error(f"'{aktif_klan}' klanı kurucu tarafından tamamen silindi!")
                st.rerun()