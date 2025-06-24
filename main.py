import sqlite3
import uuid
import random
import hashlib
from datetime import datetime

DB_FILE = 'baza.sqlite3'
OUTPUT_SQL_FILE = 'output.sql'
USER_COUNT = 60
BYULLETEN_COUNT = 10
PASSWORD = 'password123'

UZB_MALE_NAMES = [
    "Anvar", "Botir", "Sanjar", "Javohir", "Olim", "Rustam", "Farrux", "Elyor", "Shavkat",
    "Zafar", "Akmal", "Sardor", "Nodir", "Behzod", "Ibrohim", "Qosim", "Ulug'bek", "Azamat"
]
UZB_FEMALE_NAMES = [
    "Madina", "Gulnora", "Sevara", "Dilnoza", "Nargiza", "Shahnoza", "Ziyoda", "Lola",
    "Kamola", "Feruza", "Aziza", "Iroda", "Nigora", "Dildora", "Mahliyo", "Go'zal"
]
UZB_SURNAMES = [
    "Karimov", "Abdullayev", "Yusupov", "Ibragimov", "Sodiqov", "Aliyev", "Rahmonov",
    "Jo'rayev", "Tursunov", "Saidov", "Qosimov", "To'rayev", "Ergashev", "Normatov"
]
UZB_JOBS = [
    "Professor", "Dotsent", "Katta o'qituvchi", "O'qituvchi", "Assistent", "Kafedra mudiri",
    "Laborant", "Ilmiy xodim", "Dekan muovini", "Bo'lim boshlig'i"
]
MASALA_TITLES = [
    "Dissertatsiya ishini himoyaga tavsiya etish to'g'risida",
    "O'quv rejasiga o'zgartirish kiritish masalasi",
    "Xalqaro konferensiyada ishtirok etish uchun xarajatlarni tasdiqlash",
    "Monografiyani nashrga tavsiya etish haqida",
    "Professor ilmiy unvonini olish uchun hujjatlarni ko'rib chiqish",
    "Fakultetning yillik hisobotini tasdiqlash",
    "Yangi o'quv dasturini tasdiqlash to'g'risida",
    "Iqtidorli talabalarni rag'batlantirish masalasi"
]
MASALA_DESCRIPTIONS = [
    "Kengash a'zolaridan ushbu masalani atroflicha muhokama qilib, o'z fikr-mulohazalarini bildirishlari so'raladi.",
    "Taqdim etilgan hujjatlar to'plami bilan tanishib chiqib, tegishli qaror qabul qilish kerak.",
    "Mas'ul shaxslarning ma'ruzalari tinglanadi va muhokamalar asosida yakuniy xulosa chiqariladi.",
    "Ushbu masala bo'yicha ovoz berish jarayoni yopiq tarzda o'tkaziladi. Iltimos, faol ishtirok eting."
]
KAFEDRALAR = [
    "Axborot texnologiyalari", "Dasturiy injiniring", "Amaliy matematika", "Fizika",
    "Iqtisodiyot nazariyasi", "Jahon tarixi", "O'zbek tili va adabiyoti"
]
LAVOZIMLAR = [
    "Fakultet dekani", "Kafedra mudiri", "O'quv ishlari bo'yicha prorektor",
    "Ilmiy ishlar va innovatsiyalar bo'yicha prorektor", "Yoshlar masalalari bo'yicha dekan o'rinbosari"
]
KENGASHLAR = [
    "Fizika-matematika fakulteti Ilmiy Kengashi", "Tarix fakulteti Ilmiy Kengashi",
    "Iqtisodiyot fakulteti Ilmiy Kengashi", "Universitet Ilmiy Kengashi"
]
ILMIY_UNVONLAR = ["Dotsent", "Professor"]
ILMIY_DARAJALAR = ["Fan nomzodi", "Fan doktori (PhD)", "Fan doktori (DSc)"]

def make_django_password(password):
    algo = 'pbkdf2_sha256'
    iterations = 320000
    salt = uuid.uuid4().hex[:16]
    hash_val = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), iterations)
    b64_hash = hashlib.sha256(hash_val).digest().hex()
    return f"{algo}${iterations}${salt}${b64_hash[:32]}"

def generate_full_name():
    surname = random.choice(UZB_SURNAMES)
    if random.random() > 0.5:
        name = random.choice(UZB_FEMALE_NAMES)
        patronymic = random.choice(UZB_MALE_NAMES) + " qizi"
    else:
        name = random.choice(UZB_MALE_NAMES)
        patronymic = random.choice(UZB_MALE_NAMES) + " o'g'li"
    return f"{surname} {name} {patronymic}"

def generate_uzbek_phone():
    return f"+998 ({random.choice(['90', '91', '93', '94', '97', '99'])}) {random.randint(100,999)}-{random.randint(10,99)}-{random.randint(10,99)}"

def generate_and_insert_data(cursor):
    # Kafedra, Lavozim, Kengash
    for kafedra in KAFEDRALAR: cursor.execute("INSERT OR IGNORE INTO professors_kafedra (name) VALUES (?)", (kafedra,))
    for lavozim in LAVOZIMLAR: cursor.execute("INSERT OR IGNORE INTO professors_lavozim (name) VALUES (?)", (lavozim,))
    for kengash in KENGASHLAR: cursor.execute("INSERT OR IGNORE INTO professors_kengash (name) VALUES (?)", (kengash,))

    kafedra_ids = [r[0] for r in cursor.execute("SELECT id FROM professors_kafedra").fetchall()]
    lavozim_ids = [r[0] for r in cursor.execute("SELECT id FROM professors_lavozim").fetchall()]
    kengash_ids = [r[0] for r in cursor.execute("SELECT id FROM professors_kengash").fetchall()]

    # Django content type uchun idlarni olish
    cursor.execute("SELECT id FROM django_content_type WHERE app_label='professors' AND model='ilmiyunvon'")
    ilmiyunvon_ct_id = cursor.fetchone()[0]
    cursor.execute("SELECT id FROM django_content_type WHERE app_label='professors' AND model='boshqamasala'")
    boshqamasala_ct_id = cursor.fetchone()[0]

    # Foydalanuvchilar va profillar
    user_ids = []
    hashed_password = make_django_password(PASSWORD)
    for i in range(USER_COUNT):
        first_name, last_name = random.choice(UZB_MALE_NAMES + UZB_FEMALE_NAMES), random.choice(UZB_SURNAMES)
        patronymic = random.choice(UZB_MALE_NAMES) + "ovich"
        last_name_clean = last_name.lower().replace("'", "")
        username = f"{first_name.lower()}.{last_name_clean}{i}"
        email = f"{username}@university.uz"
        cursor.execute("""INSERT INTO auth_user (password, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined)
            VALUES (?, 0, ?, ?, ?, ?, 1, 1, ?)""", (hashed_password, username, first_name, last_name, email, datetime.now()))
        user_id = cursor.lastrowid
        user_ids.append(user_id)
        cursor.execute("""INSERT INTO professors_userprofile (id, surname, academic_degree, position, phone_number, kafedra_id, user_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)""", (uuid.uuid4().hex, patronymic, random.choice(ILMIY_DARAJALAR),
            random.choice(UZB_JOBS), generate_uzbek_phone(), random.choice(kafedra_ids), user_id))

    # Saylov va nomzodlar
    saylov_ids, unvon_ids, masala_ids = [], [], []
    for _ in range(15):
        lavozim_id = random.choice(lavozim_ids)
        l_name = cursor.execute("SELECT name FROM professors_lavozim WHERE id=?", (lavozim_id,)).fetchone()[0]
        cursor.execute("INSERT INTO professors_saylov (title, lavozim_id) VALUES (?, ?)", (f"'{l_name}' lavozimi uchun saylov", lavozim_id))
        saylov_id = cursor.lastrowid
        saylov_ids.append(saylov_id)
        for _ in range(random.randint(2, 4)):
            cursor.execute("INSERT INTO professors_tanlov (candidate_name, saylov_id) VALUES (?, ?)",(generate_full_name(), saylov_id))
    for _ in range(20):
        cursor.execute("INSERT INTO professors_ilmiyunvon (candidate_name, title, title_code) VALUES (?, ?, ?)",
                       (generate_full_name(), random.choice(ILMIY_UNVONLAR), f"{random.randint(10,99)}.00.{random.randint(10,99)}"))
        unvon_ids.append(cursor.lastrowid)
    for _ in range(20):
        cursor.execute("INSERT INTO professors_boshqamasala (title, description) VALUES (?, ?)",
                       (random.choice(MASALA_TITLES), random.choice(MASALA_DESCRIPTIONS)))
        masala_ids.append(cursor.lastrowid)

    # Byulleten va ko‘p-ko‘pligi
    for i in range(BYULLETEN_COUNT):
        cursor.execute("INSERT INTO professors_byulleten (title, created_at, is_active, kengash_id) VALUES (?, ?, ?, ?)",
                       (f"{i+1}-sonli Ilmiy Kengash byulleteni", datetime.now(), True, random.choice(kengash_ids)))
        byulleten_id = cursor.lastrowid
        for s_id in random.sample(saylov_ids, k=min(len(saylov_ids), 2)): cursor.execute("INSERT INTO professors_byulleten_saylovlar (byulleten_id, saylov_id) VALUES (?, ?)", (byulleten_id, s_id))
        for u_id in random.sample(unvon_ids, k=min(len(unvon_ids), 5)): cursor.execute("INSERT INTO professors_byulleten_unvonlar (byulleten_id, ilmiyunvon_id) VALUES (?, ?)", (byulleten_id, u_id))
        for m_id in random.sample(masala_ids, k=min(len(masala_ids), 8)): cursor.execute("INSERT INTO professors_byulleten_boshqa_masalalar (byulleten_id, boshqamasala_id) VALUES (?, ?)", (byulleten_id, m_id))

    # Saylov ovozlari
    for saylov_id in saylov_ids:
        candidate_ids = [r[0] for r in cursor.execute("SELECT id FROM professors_tanlov WHERE saylov_id=?", (saylov_id,)).fetchall()]
        if not candidate_ids: continue
        for user_id in random.sample(user_ids, k=random.randint(30, USER_COUNT)):
            try: cursor.execute("INSERT INTO professors_saylovvote (user_id, saylov_id, chosen_candidate_id) VALUES (?, ?, ?)", (user_id, saylov_id, random.choice(candidate_ids)))
            except sqlite3.IntegrityError: pass

    # Standart ovozlar
    ovoz_choices = ['ha', 'yoq', 'betaraf']
    for unvon_id in unvon_ids:
        for user_id in random.sample(user_ids, k=random.randint(30, USER_COUNT)):
            try: cursor.execute("INSERT INTO professors_vote (ovoz, user_id, content_type_id, object_id) VALUES (?, ?, ?, ?)", (random.choice(ovoz_choices), user_id, ilmiyunvon_ct_id, unvon_id))
            except sqlite3.IntegrityError: pass
    for masala_id in masala_ids:
        for user_id in random.sample(user_ids, k=random.randint(30, USER_COUNT)):
            try: cursor.execute("INSERT INTO professors_vote (ovoz, user_id, content_type_id, object_id) VALUES (?, ?, ?, ?)", (random.choice(ovoz_choices), user_id, boshqamasala_ct_id, masala_id))
            except sqlite3.IntegrityError: pass

def export_to_sql(connection):
    print(f"Bosqich 5/5: Ma'lumotlar '{OUTPUT_SQL_FILE}' fayliga eksport qilinmoqda...")
    with open(OUTPUT_SQL_FILE, 'w', encoding='utf-8') as f:
        f.write("-- Faqat ma'lumotlar (INSERT) eksport qilindi.\n")
        for line in connection.iterdump():
            if line.startswith("INSERT INTO"):
                f.write('%s\n' % line)
    print("SQL eksport muvaffaqiyatli yakunlandi.")

def main():
    print("--- Ma'lumotlar bazasini yaratish skripti ishga tushdi ---")
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        generate_and_insert_data(cursor)
        conn.commit()
        print(f"\n✅ Ma'lumotlar '{DB_FILE}' fayliga muvaffaqiyatli yozildi.")
        export_to_sql(conn)
    except sqlite3.Error as e:
        print(f"\n❌ Baza bilan ishlashda xatolik yuz berdi: {e}")
    finally:
        if conn:
            conn.close()
            print("\n--- Skript o'z ishini yakunladi. ---")

if __name__ == '__main__':
    main()