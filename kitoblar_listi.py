import db

db.create_table()

# 2️⃣ Kitoblar ro'yxati
books = [
    {"name": "Ikkki eshik orasi", "author": "Otkir Hoshimov", "genre": "Romantika", "description": "Roman qissalari..."},
    {"name": "O‘tkan kunlar", "author": "Said Ahmad", "genre": "Tarixiy", "description": "O‘zbekiston tarixi..."},
]

for b in books:
    db.add_books(b["name"], b["author"], b["genre"], b["description"])

print("Kitoblar DBga qo‘shildi!")
