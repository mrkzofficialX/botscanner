import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

from scanner import scan

# ===== CONFIG =====
TOKEN = os.getenv("BOT_TOKEN")  # set di Render ENV
PREMIUM_USERS = []  # isi user_id kalau mau

# ===== BOT HANDLERS =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔍 Kirim URL untuk scan\nContoh: https://example.com\n\n"
        "Gunakan /scan untuk premium"
    )

async def scan_basic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    if not url.startswith("http"):
        url = "http://" + url

    result = scan(url, deep=False)

    if result.get("error"):
        await update.message.reply_text(f"❌ Error: {result['error']}")
        return

    msg = f"""🔍 BASIC SCAN

🌐 URL: {url}
📡 Status: {result['status']}
🖥 Server: {result['server']}

🛡 Security Headers:
"""

    for k, v in result['security'].items():
        status = "✅" if v != "Missing" else "❌"
        msg += f"{status} {k}: {v}\n"

    await update.message.reply_text(msg)


async def scan_premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in PREMIUM_USERS:
        await update.message.reply_text("🚫 Premium only")
        return

    if not context.args:
        await update.message.reply_text("Contoh: /scan https://example.com")
        return

    url = context.args[0]

    if not url.startswith("http"):
        url = "http://" + url

    result = scan(url, deep=True)

    if result.get("error"):
        await update.message.reply_text(f"❌ Error: {result['error']}")
        return

    msg = f"""🔥 PREMIUM SCAN

🌐 URL: {url}
📡 Status: {result['status']}
🖥 Server: {result['server']}

🛡 Security Headers:
"""

    for k, v in result['security'].items():
        status = "✅" if v != "Missing" else "❌"
        msg += f"{status} {k}: {v}\n"

    msg += "\n📂 Sensitive Paths:\n"

    for p, v in result.get("paths", {}).items():
        icon = "⚠️" if v == "FOUND" else "✅"
        msg += f"{icon} {p}: {v}\n"

    await update.message.reply_text(msg)

# ===== INIT BOT =====
def run_bot():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("scan", scan_premium))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, scan_basic))

    print("🤖 Bot jalan...")
    app.run_polling()

# ===== HTTP SERVER (biar Render gak kill) =====
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

def run_web():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"🌐 Web server jalan di port {port}")
    server.serve_forever()

# ===== MAIN =====
if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    run_web()
