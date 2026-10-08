import sqlite3
import hashlib
import json
import time
import os

DB_FILE = "ticarix_users.db"

def init_db():
    """Veritabanını ve gerekli tüm tabloları sıfırdan/kontrol ederek oluşturur."""
    conn = sqlite3.connect(DB_FILE, timeout=10.0)
    cursor = conn.cursor()
    
    # 1. Kullanıcılar Tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            game_data TEXT NOT NULL
        )
    ''')
    
    # 2. Global Klanlar Tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clans (
            clan_name TEXT PRIMARY KEY,
            clan_data TEXT NOT NULL
        )
    ''')
    
    # 3. Genel Sohbet Tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def hash_password(password):
    """Şifreleri SHA-256 ile güvenli hale getirir."""
    return hashlib.sha256(password.encode()).hexdigest()

def get_default_game_data():
    """Yeni kayıt olan bir oyuncunun başlangıç oyun verilerini döndürür."""
    return {
        "money": 5000,
        "bank_balance": 0,
        "bank_debt": 0,
        "tcmb_policy_rate": 37.0,
        "last_bank_interest_time": time.time(),
        "last_shop_income_time": time.time(),
        "clan_name": "La Familia",
        "user_clan": None,
        "clan_members": 1,
        "accumulated_shop_money": 0,
        "active_job": None,
        "mine_level": 1,
        "mine_xp": 0,
        "mine_inventory": {"Kömür": 0, "Bakır": 0, "Demir": 0, "Gümüş": 0, "Altın": 0, "Elmas": 0},
        "mine_last_time": time.time(),
        "fish_level": 1,
        "fish_xp": 0,
        "fish_inventory": {"Sazan": 0, "Alabalık": 0, "Levrek": 0, "Somon": 0, "Kalkan": 0, "Kılıç Balığı": 0},
        "fish_last_time": time.time(),
        "shops": {
            "bakkal": {"name": "Mahalle Bakkalı", "count": 0, "cost": 10000, "income": 150},
            "cafe": {"name": "Sahil Kafe", "count": 0, "cost": 75000, "income": 1200},
            "holding": {"name": "Ticarix Plaza", "count": 0, "cost": 500000, "income": 8500}
        }
    }

def is_admin_user(user_id):
    """Kullanıcının admin/kurucu hesap olup olmadığını kontrol eder."""
    if not user_id:
        return False
    conn = sqlite3.connect(DB_FILE, timeout=10.0)
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return bool(row and row[0] == "azizcanakgul8@gmail.com")

def get_admin_buffed_data(current_data):
    """Admin hesabı için parayı sınırsız yapar."""
    current_data["money"] = 999999999
    current_data["bank_balance"] = 999999999
    current_data["bank_debt"] = 0
    return current_data

def register_user(username, email, password):
    """Yeni kullanıcı kaydı yapar."""
    try:
        conn = sqlite3.connect(DB_FILE, timeout=10.0)
        cursor = conn.cursor()
        hashed_p = hash_password(password)
        initial_data = get_default_game_data()
        
        if email == "azizcanakgul8@gmail.com":
            initial_data = get_admin_buffed_data(initial_data)

        initial_data_json = json.dumps(initial_data, ensure_ascii=False)
        
        cursor.execute("INSERT INTO users (username, email, password_hash, game_data) VALUES (?, ?, ?, ?)",
                       (username, email, hashed_p, initial_data_json))
        conn.commit()
        conn.close()
        return True, "Kayıt başarılı!"
    except sqlite3.IntegrityError:
        return False, "Bu kullanıcı adı veya e-posta zaten kullanımda!"

def login_user(identifier, password):
    """Kullanıcı girişi yapar ve (user_id, username, game_data_json) döndürür."""
    conn = sqlite3.connect(DB_FILE, timeout=10.0)
    cursor = conn.cursor()
    hashed_p = hash_password(password)
    
    cursor.execute("SELECT id, username, game_data, email FROM users WHERE (username = ? OR email = ?) AND password_hash = ?", 
                   (identifier, identifier, hashed_p))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        user_id, username, g_data_json, email = user
        if email == "azizcanakgul8@gmail.com":
            g_data = json.loads(g_data_json)
            g_data = get_admin_buffed_data(g_data)
            g_data_json = json.dumps(g_data, ensure_ascii=False)
            
            conn = sqlite3.connect(DB_FILE, timeout=10.0)
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET game_data = ? WHERE id = ?", (g_data_json, user_id))
            conn.commit()
            conn.close()
            
        return (user_id, username, g_data_json)
            
    return None

def save_game_data(user_id, data):
    """Oyuncunun güncel oyun verilerini veritabanına kalıcı olarak kaydeder."""
    if not user_id:
        return
    if is_admin_user(user_id):
        data = get_admin_buffed_data(data)
        
    try:
        conn = sqlite3.connect(DB_FILE, timeout=10.0)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET game_data = ? WHERE id = ?", (json.dumps(data, ensure_ascii=False), user_id))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Kayıt Hatası: {e}")

# --- GLOBAL KLAN FONKSİYONLARI ---
def load_all_clans():
    conn = sqlite3.connect(DB_FILE, timeout=10.0)
    cursor = conn.cursor()
    cursor.execute("SELECT clan_name, clan_data FROM clans")
    rows = cursor.fetchall()
    conn.close()
    
    clans_dict = {}
    for row in rows:
        try:
            clans_dict[row[0]] = json.loads(row[1])
        except Exception:
            pass
    return clans_dict

def save_clan_to_db(clan_name, clan_data):
    conn = sqlite3.connect(DB_FILE, timeout=10.0)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO clans (clan_name, clan_data) VALUES (?, ?)",
                   (clan_name, json.dumps(clan_data, ensure_ascii=False)))
    conn.commit()
    conn.close()

def delete_clan_from_db(clan_name):
    conn = sqlite3.connect(DB_FILE, timeout=10.0)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM clans WHERE clan_name = ?", (clan_name,))
    conn.commit()
    conn.close()

# --- GLOBAL SOHBET FONKSİYONLARI ---
def save_chat_message(username, message):
    """Sohbet mesajını kaydeder."""
    conn = sqlite3.connect(DB_FILE, timeout=10.0)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO chat_messages (username, message) VALUES (?, ?)",
        (username, message)
    )
    conn.commit()
    conn.close()

def get_chat_messages(limit=50):
    """Yalnızca son 5 dakika içerisindeki sohbet mesajlarını getirir."""
    conn = sqlite3.connect(DB_FILE, timeout=10.0)
    cursor = conn.cursor()
    
    # SQLite datetime ile son 5 dakika filtresi uygulanır
    cursor.execute(
        """
        SELECT username, message, created_at 
        FROM chat_messages 
        WHERE created_at >= datetime('now', '-5 minutes', 'localtime') 
        ORDER BY id DESC LIMIT ?
        """,
        (limit,)
    )
    rows = cursor.fetchall()
    conn.close()
    return rows[::-1]
    # --- SIRALAMA (LİDERLİK TABLOSU) FONKSİYONLARI ---
def get_top_players(limit=100):
    """Oyuncuların servetini (Nakit + Banka + Dükkan Değeri - Borç) hesaplayıp ilk 100'ü döndürür."""
    conn = sqlite3.connect(DB_FILE, timeout=10.0)
    cursor = conn.cursor()
    cursor.execute("SELECT username, game_data FROM users")
    rows = cursor.fetchall()
    conn.close()

    leaderboard = []
    for username, g_json in rows:
        try:
            data = json.loads(g_json)
            money = int(data.get("money", 0))
            bank = int(data.get("bank_balance", 0))
            debt = int(data.get("bank_debt", 0))

            # Dükkanların toplam satın alma değerini hesapla
            shops = data.get("shops", {})
            shop_val = 0
            if isinstance(shops, dict):
                for shop_info in shops.values():
                    if isinstance(shop_info, dict):
                        cnt = shop_info.get("count", 0)
                        cost = shop_info.get("cost", 0)
                        shop_val += cnt * cost

            # Toplam Servet = Nakit + Banka + Dükkan Yatırımı - Borç
            net_wealth = money + bank + shop_val - debt

            leaderboard.append({
                "username": username,
                "money": money,
                "bank": bank,
                "shop_value": shop_val,
                "total_wealth": net_wealth,
                "clan": data.get("user_clan") or "Klanı Yok"
            })
        except Exception:
            continue

    # Servete göre büyükten küçüğe sırala
    leaderboard.sort(key=lambda x: x["total_wealth"], reverse=True)
    return leaderboard[:limit]


def get_top_clans(limit=100):
    """Klanları XP değerine göre sıralar."""
    conn = sqlite3.connect(DB_FILE, timeout=10.0)
    cursor = conn.cursor()
    cursor.execute("SELECT clan_name, clan_data FROM clans")
    rows = cursor.fetchall()
    conn.close()

    clan_list = []
    for c_name, c_json in rows:
        try:
            c_data = json.loads(c_json)
            xp = int(c_data.get("xp", c_data.get("clan_xp", 0)))
            
            # Burada "leader" veya "owner" anahtarını kontrol ediyoruz, hiçbiri yoksa "Bilinmiyor" yazıyor
            leader = c_data.get("leader") or c_data.get("owner", "Bilinmiyor")
            
            members = c_data.get("members", [])
            member_count = len(members) if isinstance(members, list) else 1

            clan_list.append({
                "clan_name": c_name,
                "leader": leader,
                "member_count": member_count,
                "xp": xp
            })
        except Exception:
            continue

    # XP'ye göre büyükten küçüğe sırala
    clan_list.sort(key=lambda x: x["xp"], reverse=True)
    return clan_list[:limit]
    
    
def transfer_money(sender_username, receiver_username, amount):
    """Bir oyuncudan diğerine güvenli para transferi yapar."""
    if amount <= 0:
        return False, "Gönderilecek tutar 0'dan büyük olmalıdır!"
        
    if sender_username.lower() == receiver_username.lower():
        return False, "Kendine para gönderemezsin!"

    conn = sqlite3.connect(DB_FILE, timeout=10.0)
    cursor = conn.cursor()
    
    try:
        # 1. Gönderenin verilerini al
        cursor.execute("SELECT id, game_data FROM users WHERE username = ?", (sender_username,))
        sender_row = cursor.fetchone()
        if not sender_row:
            return False, "Gönderen hesap bulunamadı!"
            
        sender_id, sender_g_json = sender_row
        sender_data = json.loads(sender_g_json)
        
        sender_money = sender_data.get("money", 0)
        if sender_money < amount:
            return False, f"Yetersiz nakit! Cüzdanında {sender_money:,} TL var."
            
        # 2. Alıcının verilerini al (Böyle bir kullanıcı var mı kontrol et)
        cursor.execute("SELECT id, game_data FROM users WHERE username = ?", (receiver_username,))
        receiver_row = cursor.fetchone()
        if not receiver_row:
            return False, f"'{receiver_username}' adında kayıtlı bir oyuncu bulunamadı! Para boşa gitmedi."
            
        receiver_id, receiver_g_json = receiver_row
        receiver_data = json.loads(receiver_g_json)
        
        # 3. Bakiyeleri güncelle
        sender_data["money"] -= amount
        receiver_data["money"] = receiver_data.get("money", 0) + amount
        
        # 4. Veritabanına kaydet
        cursor.execute("UPDATE users SET game_data = ? WHERE id = ?", (json.dumps(sender_data, ensure_ascii=False), sender_id))
        cursor.execute("UPDATE users SET game_data = ? WHERE id = ?", (json.dumps(receiver_data, ensure_ascii=False), receiver_id))
        
        conn.commit()
        return True, f"Başarıyla {receiver_username} adlı oyuncuya {amount:,} TL gönderildi!"
        
    except Exception as e:
        conn.rollback()
        return False, f"Transfer sırasında bir hata oluştu: {e}"
    finally:
        conn.close()