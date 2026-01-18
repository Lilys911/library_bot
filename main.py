from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler, \
    CallbackQueryHandler
import db
import re
TOKEN = "YOUR_TOKEN"
ADMIN_PASSWORD = "YOUR_PASSWORD"
ADMIN_IDS = set()
(
    STUDENT_ID,
    SEARCH_BOOKS,
    BORROW_BOOK,
    RETURN_BOOK,
    MY_BORROWED_BOOKS,
    MAIN_MENU,
    IZOH_YOZING,
    EDIT_STUDENT_ID,
    SETTINGS_MENU,
    CONFIRM_MENU
)=range(10)
(
    ADMIN_MENU, ADMIN_ADD_NAME, ADMIN_ADD_AUTHOR,
    ADMIN_ADD_GENRE, ADMIN_ADD_DESC, ADMIN_DELETE_BOOK_NAME,
    ADMIN_CONFIRM_DELETE,ADMIN_CHANGE_DATA, ALL_STATISTICS, OQUVCHILAR_SAVOLLARI


)=range(10, 20)
def start(update: Update, context: CallbackContext):
    user = db.get_user(update.effective_user.id)

    if user:
        return student_menu(update, context)
    update.message.reply_text("👤 Student Idni kiriting:\n\n"
                              "📌 Misol: something@aut-edu.uz")
    return STUDENT_ID

def is_valid_student_id(student_id: str):
    pattern = r'^[a-zA-Z0-9._]+@aut\-edu\.uz$'
    return re.fullmatch(pattern, student_id) is not None

def get_student_id(update, context):
    student_id = update.message.text.strip().lower()

    if not is_valid_student_id(student_id):
        update.message.reply_text(
            "❌ Student ID noto‘g‘ri formatda.\n\n"
            "To‘gri format:\n"
            "example@aut-edu.uz\n\n"
            "Iltimos, qaytadan kiriting:"
        )
        return STUDENT_ID

    # agar to‘g‘ri bo‘lsa
    db.add_user(update.effective_user.id, student_id)
    update.message.reply_text("✅ Student ID saqlandi!")
    student_menu(update, context)
    return MAIN_MENU

def student_menu(update, context):
    update.message.reply_text(
        "🏠 Asosiy menyu:",
        reply_markup=ReplyKeyboardMarkup(
            [
                ["📚 Search"],
                ["Borrow", "Return"],
                ["Izoh qoldirish","⚙️ Sozlamalar"]
            ],
            resize_keyboard=True
        )
    )
    return MAIN_MENU

def student_menu_select(update, context):
    text = update.message.text

    if text == "📚 Search":
        update.message.reply_text("Qidirmoqchi bolgan kitob nomini kiriting:")
        return SEARCH_BOOKS
    if text == "Borrow":
        update.message.reply_text("O'lmoqchi bolgan kitobingizni yozing: ")
        return BORROW_BOOK
    if text == "Return":
        update.message.reply_text("Qaytarmoqchi bolgan kitobingizni yozing: ")
        return RETURN_BOOK
    if text == "Izoh qoldirish":
        update.message.reply_text(
            "📝 Izoh yozib qoldiring (kitob haqida yoki taklif):"
        )
        return IZOH_YOZING

    if text == "⚙️ Sozlamalar":
        return settings_menu(update, context)
    return MAIN_MENU

def search_book(update, context):
    keyword = update.message.text.strip()
    books = db.search_books_in_db(keyword)

    if not books:
        update.message.reply_text("❌ Hech qanday kitob topilmadi")
        return MAIN_MENU

    for name, author, genre, desc, borrowed_by in books:
        if borrowed_by is None:
            status = "🟢 Bu kitob kutubxonada mavjud"
        else:
            status = f"🔴 Bu kitob hozir {borrowed_by} da"

        update.message.reply_text(
            f"📖 {name}\n"
            f"✍️ {author}\n"
            f"🏷 {genre}\n"
            f"📝 {desc}\n"
            f"{status}"
        )
    return MAIN_MENU

def borrow_book(update, context):
    book_name = update.message.text.strip()
    context.user_data['book_name'] = book_name

    result = db.get_book_by_name(book_name)
    if not result:
        update.message.reply_text("❌ Bunday kitob topilmadi.")
        return MAIN_MENU

    book_id, borrowed_by = result
    if borrowed_by is not None:
        update.message.reply_text(f"🔴 Bu kitob hozir {borrowed_by} da. Boshqa kitob qarab ko‘rasizmi?")
        return MAIN_MENU

    keyboard = [["✅ Ha", "❌ Yo'q"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    update.message.reply_text(f"🟢 Siz **{book_name}** kitobini olmoqchimisiz?", reply_markup=reply_markup, parse_mode="Markdown")
    return CONFIRM_MENU

def confirm_borrow(update, context):
    text = update.message.text
    book_name = context.user_data.get("book_name")
    student_id = update.effective_user.id

    if text == "✅ Ha":
        update_rows = db.borrow_book_in_db(book_name, student_id)
        if update_rows:
            update.message.reply_text(f"✅ Siz **{book_name}** kitobini muvaffaqiyatli oldingiz 📚", parse_mode="Markdown")
        else:
            update.message.reply_text("⚠️ Kitob olishda xatolik yuz berdi yoki kitob allaqachon olingan.")
    else:
        update.message.reply_text("❌ Kitob olish bekor qilindi.")

    return student_menu(update, context)


def return_book(update, context):
    book_name = update.message.text.strip()
    student_id = update.effective_user.id

    update_rows = db.return_book_in_db(book_name, student_id)

    if update_rows == 0:
        update.message.reply_text("❌ Bunday kitob sizda emas yoki mavjud emas.")
    else:
        update.message.reply_text(f"✅ Rahmat oshna yana kelib turin. {book_name} oqiganingiz uchun rahmat.")
    return MAIN_MENU

def izoh_yozing(update, context):
    comment = update.message.text.strip()
    student_id = update.effective_user.id

    db.izoh_yozish(student_id, comment)
    update.message.reply_text("Izohingiz qabul qilindi. Yana kelib turin!")
    return MAIN_MENU

def settings_menu(update, context):
    update.message.reply_text(
        "Student Id o'zgartirish: ",
        reply_markup=ReplyKeyboardMarkup(
            [["Student Id"]],
        resize_keyboard=True
        )
    )
    return SETTINGS_MENU

def settings_select(update, context):
    text = update.message.text

    if text == "Student Id":
        update.message.reply_text("Yangi Student Id kiriting:",)
        return EDIT_STUDENT_ID

def edit_student_id(update, context):
    student_id = update.message.text.strip().lower()


    if not is_valid_student_id(student_id):
        update.message.reply_text(
            "❌ Student ID noto‘g‘ri formatda.\n\n"
            "To‘g‘ri format:\n"
            "example@aut-edu.uz\n\n"
            "Iltimos, qaytadan kiriting:"
        )
        return EDIT_STUDENT_ID

    db.update_student_id(update.effective_user.id, student_id)
    update.message.reply_text("✅ Student ID muvaffaqiyatli yangilandi")
    return student_menu(update, context)

def is_admin(user_id):
    return user_id in ADMIN_IDS

def admin_login(update, context):
    if not context.args:
        update.message.reply_text("Parol kiriting: /admin parol")
        return ConversationHandler.END

    password = context.args[0]

    if password != ADMIN_PASSWORD:
        update.message.reply_text(" ❌ NOTOGRI PAROL KIRITNGIZ !")
        return ConversationHandler.END

    ADMIN_IDS.add(update.effective_user.id)
    update.message.reply_text(
        "Admin panelga xush kelibsiz",
        reply_markup=ReplyKeyboardMarkup(
            [
                ["📚 Kitob qoshish", "❌ Kitob ochirish"],
                ["✏️ Ma'lumotlarni o'zgartirish", "📊 Statistika"],
                ["📩 Savollar"]
            ],
            resize_keyboard=True
        )
    )
    return ADMIN_MENU

def admin_menu_select(update, context):
    text = update.message.text

    if text == "📚 Kitob qoshish":
        update.message.reply_text("Kitob nomini kiriting:")
        return ADMIN_ADD_NAME
    if text == "❌ Kitob ochirish":
        update.message.reply_text("Ochirmoqchi bolgan kitobingiz nomini yozing: ")
        return ADMIN_DELETE_BOOK_NAME
    if text == "✏️ Ma'lumotlarni o'zgartirish":
        update.message.reply_text("Ozgartirmochi bolgan kitobingiz nomini kiriting: ")
        return ADMIN_CHANGE_DATA
    if text == "📊 Statistika":
        return ALL_STATISTICS
    if text == "📩 Savollar":
        return OQUVCHILAR_SAVOLLARI
    update.message.reply_text("Admin menyu")
    return ADMIN_MENU

def get_book_name(update, context):
    context.user_data["name"] = update.message.text
    update.message.reply_text("Kitob muallifi kiriting: ")
    return ADMIN_ADD_AUTHOR

def get_book_author(update, context):
    context.user_data["author"] = update.message.text
    update.message.reply_text("Kitob janrini kiriting: ")
    return ADMIN_ADD_GENRE

def get_book_genre(update, context):
    context.user_data["genre"] = update.message.text
    update.message.reply_text("Kitob haqida(description) kiriting: ")
    return ADMIN_ADD_DESC

def get_book_desc(update, context):
    context.user_data["description"] = update.message.text

    db.add_books(
        context.user_data["name"],
        context.user_data["author"],
        context.user_data["genre"],
        context.user_data["description"]
    )

    update.message.reply_text(
        "✅ Kitob qo‘shildi",
        reply_markup=ReplyKeyboardMarkup(
            [
                ["📚 Kitob qoshish", "❌ Kitob ochirish"],
                ["✏️ Ma'lumotlarni o'zgartirish", "📊 Statistika"],
                ["📩 Savollar"]
            ],
            resize_keyboard=True
        )
    )

    return ADMIN_MENU

def admin_delete_book_by_name(update, context):
    name = update.message.text.strip()
    deleted = db.delete_book_by_name(name)

    if not deleted:  # to‘g‘ri tekshirish
        update.message.reply_text("❌ Bunday kitob topilmadi")
        return ADMIN_MENU

    context.user_data["delete_book"] = name

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Ha, ochirish", callback_data="confirm_delete"),
         InlineKeyboardButton("Yo‘q, qoldirish", callback_data="cancel_delete")]
    ])
    update.message.reply_text(
        f"Rostdan ham *{name}* kitobini ochirmoqchimisiz?",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    return ADMIN_CONFIRM_DELETE


def admin_confirm_delete_book(update, context):
    query = update.callback_query
    query.answer()

    name = context.user_data.get("delete_book")

    if query.data == "confirm_delete":
        db.delete_book_by_name(name)
        query.edit_message_text("✅ Kitob to‘liq o‘chirildi")
    else:
        query.edit_message_text("❌ O‘chirish bekor qilindi")

    context.user_data.pop("delete_book", None)
    return ADMIN_MENU


def admin_comments(update, context):
    comments = db.get_all_comments()

    if not comments:
        update.message.reply_text("📭 Hozircha xabarlar yo‘q")
        return ADMIN_MENU

    text = "📩 Talabalar xabarlari:\n\n"

    for student_id, comment, date in comments:
        text += (
            f"👤 {student_id}\n"
            f"🕒 {date}\n"
            f"💬 {comment}\n"
            f"-------------------\n"
        )

    update.message.reply_text(text)
    return ADMIN_MENU


def admin_statistics(update, context):
    total_books = db.count_books()
    borrowed_books = db.count_borrowed_books()
    available_books = db.count_available_books()
    users_count = db.count_users()
    comments_count = db.count_comments()

    text = (
        "📊 *Kutubxona statistikasi*\n\n"
        f"📚 Jami kitoblar: *{total_books}*\n"
        f"📕 Olingan kitoblar: *{borrowed_books}*\n"
        f"📗 Mavjud kitoblar: *{available_books}*\n\n"
        f"👤 Foydalanuvchilar: *{users_count}*\n"
        f"💬 Izohlar soni: *{comments_count}*"
    )

    update.message.reply_text(text, parse_mode="Markdown")
    return ADMIN_MENU


def main():
    db.create_table()

    updater = Updater(TOKEN)
    dp = updater.dispatcher

    conv = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CommandHandler("admin", admin_login)
        ],
        states={
            STUDENT_ID: [MessageHandler(Filters.text & ~Filters.command, get_student_id)],

            MAIN_MENU: [MessageHandler(Filters.text & ~Filters.command, student_menu_select)],

            EDIT_STUDENT_ID: [MessageHandler(Filters.text & ~Filters.command, edit_student_id)],
            SEARCH_BOOKS: [MessageHandler(Filters.text & ~Filters.command, search_book)],
            BORROW_BOOK: [MessageHandler(Filters.text & ~Filters.command, borrow_book)],
            CONFIRM_MENU: [MessageHandler(Filters.text & ~Filters.command, confirm_borrow)],
            RETURN_BOOK: [MessageHandler(Filters.text & ~Filters.command, return_book)],
            IZOH_YOZING: [MessageHandler(Filters.text & ~Filters.command, izoh_yozing)],
            SETTINGS_MENU: [MessageHandler(Filters.text & ~Filters.command, settings_select)],

            ADMIN_MENU: [MessageHandler(Filters.text & ~Filters.command, admin_menu_select)],
            ADMIN_ADD_NAME: [MessageHandler(Filters.text & ~Filters.command, get_book_name)],
            ADMIN_ADD_AUTHOR: [MessageHandler(Filters.text & ~Filters.command, get_book_author)],
            ADMIN_ADD_GENRE: [MessageHandler(Filters.text & ~Filters.command, get_book_genre)],
            ADMIN_ADD_DESC: [MessageHandler(Filters.text & ~Filters.command, get_book_desc)],
            ADMIN_DELETE_BOOK_NAME: [MessageHandler(Filters.text & ~Filters.command, admin_delete_book_by_name)],
            ADMIN_CONFIRM_DELETE: [CallbackQueryHandler(admin_confirm_delete_book)],
            OQUVCHILAR_SAVOLLARI: [MessageHandler(Filters.text &~Filters.command, admin_comments)],
            ALL_STATISTICS: [MessageHandler(Filters.text &~Filters.command, admin_statistics)]
        },
        fallbacks=[]
    )


    dp.add_handler(conv)
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
