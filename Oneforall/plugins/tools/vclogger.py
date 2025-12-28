from pyrogram import filters
from pyrogram.raw.types import UpdateGroupCallParticipants, GroupCallParticipant
from Oneforall import app

VC_LOGGER = {}

@app.on_message(filters.command("vclogger") & filters.group)
async def vclogger_handler(_, message):
    if len(message.command) < 2:
        return await message.reply_text(
            "Usage:\n/vclogger on\n/vclogger off"
        )

    chat_id = message.chat.id
    option = message.command[1].lower()

    if option == "on":
        VC_LOGGER[chat_id] = True
        await message.reply_text("✅ **VC Logger Enabled**")
    elif option == "off":
        VC_LOGGER[chat_id] = False
        await message.reply_text("❌ **VC Logger Disabled**")

@app.on_message(filters.command("vcstatus") & filters.group)
async def vcstatus(_, message):
    status = VC_LOGGER.get(message.chat.id, False)
    await message.reply_text(
        f"🎙️ VC Logger Status: {'ON' if status else 'OFF'}"
    )

@app.on_raw_update()
async def vc_join_logger(_, update, users, chats):
    if not isinstance(update, UpdateGroupCallParticipants):
        return

    chat_id = update.chat_id
    if not VC_LOGGER.get(chat_id):
        return

    for p in update.participants:
        if isinstance(p, GroupCallParticipant):
            user = users.get(p.user_id)
            if not user:
                continue

            await app.send_message(
                chat_id,
                f"""
🎧 **VC Join Detected**
👤 Name: {user.first_name}
🆔 ID: `{user.id}`
🔗 Username: @{user.username if user.username else 'Ignored'}
"""
            )