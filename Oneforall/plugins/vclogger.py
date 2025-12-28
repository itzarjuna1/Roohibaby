from pyrogram import Client, filters
from pyrogram.raw.types import (
    UpdateGroupCallParticipants,
    GroupCallParticipant
)

VC_LOGGER = {}

@Client.on_message(filters.command("vclogger") & filters.group)
async def vclogger_handler(client, message):
    if len(message.command) < 2:
        return await message.reply_text(
            "**Usage:**\n/vclogger on\n/vclogger off"
        )

    chat_id = message.chat.id
    option = message.command[1].lower()

    if option == "on":
        VC_LOGGER[chat_id] = True
        await message.reply_text("✅ **VC Logger Enabled**")
    elif option == "off":
        VC_LOGGER[chat_id] = False
        await message.reply_text("❌ **VC Logger Disabled**")
    else:
        await message.reply_text("❌ Invalid option")

@Client.on_message(filters.command("vcstatus") & filters.group)
async def vcstatus_handler(client, message):
    status = VC_LOGGER.get(message.chat.id, False)
    text = "🟢 **ON**" if status else "🔴 **OFF**"
    await message.reply_text(f"🎙️ **VC Logger Status:** {text}")

@Client.on_raw_update()
async def vc_join_logger(client, update, users, chats):
    if not isinstance(update, UpdateGroupCallParticipants):
        return

    chat_id = update.chat_id
    if not VC_LOGGER.get(chat_id):
        return

    for participant in update.participants:
        if isinstance(participant, GroupCallParticipant):
            user_id = participant.user_id
            user = users.get(user_id)

            if user:
                name = user.first_name
                username = f"@{user.username}" if user.username else "No Username"

                await client.send_message(
                    chat_id,
                    f"""
🎧 **VC Join Detected**
👤 **Name:** {name}
🆔 **ID:** `{user_id}`
🔗 **Username:** {username}
"""
                )