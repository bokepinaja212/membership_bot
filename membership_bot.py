from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import sqlite3
from datetime import datetime


def is_member_allowed(user_id):
    conn = sqlite3.connect('membership.db')
    cursor = conn.cursor()

    # Cari pengguna berdasarkan ID
    cursor.execute('SELECT expiry_date FROM members WHERE id = ?', (user_id,))
    result = cursor.fetchone()

    if result:
        expiry_date = result[0]
        today = datetime.now().date()
        if datetime.strptime(expiry_date, '%Y-%m-%d').date() >= today:
            return True

    conn.close()
    return False


def add_member(user_id, username, expiry_date):
    conn = sqlite3.connect('membership.db')
    cursor = conn.cursor()

    cursor.execute('''
    INSERT OR REPLACE INTO members (id, username, expiry_date)
    VALUES (?, ?, ?)
    ''', (user_id, username, expiry_date))

    conn.commit()
    conn.close()


async def check_membership(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_id = user.id

    if is_member_allowed(user_id):
        await update.message.reply_text("Selamat datang, Anda memiliki akses!")
    else:
        await update.message.reply_text("Maaf, keanggotaan Anda sudah kadaluarsa atau tidak terdaftar.")
        try:
            # Keluarkan pengguna dari grup jika tidak memiliki akses
            await context.bot.ban_chat_member(update.message.chat_id, user_id)
        except Exception as e:
            await update.message.reply_text(f"Gagal mengeluarkan pengguna: {e}")


async def add_member_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Format: /addmember <user_id> <username> <expiry_date>
        args = context.args
        user_id = int(args[0])
        username = args[1]
        expiry_date = args[2]

        add_member(user_id, username, expiry_date)
        await update.message.reply_text(f"Berhasil menambahkan anggota {username} dengan ID {user_id} hingga {expiry_date}.")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")


def main():
    TOKEN = '7151330160:AAHhdnilrQG7J-U6cHijKWTNLfkREXJM6xg'  # Masukkan token bot Anda di sini
    application = Application.builder().token(TOKEN).build()

    # Tambahkan handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_membership))
    application.add_handler(CommandHandler('addmember', add_member_command))

    # Jalankan bot
    application.run_polling()


if __name__ == '__main__':
    main()