
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer
from pyrogram import Client, filters
from pymongo import MongoClient
import os
import psutil

# Start dummy web server for Koyeb health check
def run_web():
    server = HTTPServer(("", 8080), SimpleHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=run_web, daemon=True).start()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
MONGO_URL = os.getenv("MONGO_URL")
OWNER_ID = int(os.getenv("OWNER_ID"))
LOG_CHANNEL = int(os.getenv("LOG_CHANNEL"))

# MongoDB setup
client = MongoClient(MONGO_URL)
db = client["telegram_bot"]
users_col = db["users"]

# Bot client
app = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.private & filters.command("start"))
async def start_cmd(client, message):
    user = message.from_user
    users_col.update_one({"_id": user.id}, {"$set": {"name": user.first_name}}, upsert=True)
    await message.reply_text("Welcome to the All URL Uploader Bot with MongoDB!")

    # Log to log channel
    try:
        await app.send_message(LOG_CHANNEL, f"#NewUser\nID: `{user.id}`\nName: {user.first_name}")
    except Exception as e:
        print(f"Log error: {e}")

@app.on_message(filters.private & filters.command("broadcast") & filters.user(OWNER_ID))
async def broadcast(client, message):
    if not message.reply_to_message:
        return await message.reply_text("Reply to a message to broadcast.")
    
    success, fail = 0, 0
    text = message.reply_to_message.text
    for user in users_col.find():
        try:
            await client.send_message(chat_id=user["_id"], text=text)
            success += 1
        except:
            fail += 1
    await message.reply_text(f"Broadcast complete.\nSuccess: {success}, Failed: {fail}")
    await app.send_message(LOG_CHANNEL, f"#Broadcast\nBy: {message.from_user.id}\nSuccess: {success}, Fail: {fail}")

@app.on_message(filters.private & filters.command("status") & filters.user(OWNER_ID))
async def status_cmd(client, message):
    total_users = users_col.count_documents({})
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    await message.reply_text(f"**Bot Status**\nUsers: {total_users}\nCPU: {cpu}%\nRAM: {ram}%")

app.run()
