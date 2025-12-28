import asyncio
from pyrogram import filters
from Oneforall import userbot

VC_LOGGER = set()


@userbot.one.on_message(filters.command("vclogger") & filters.group)
async def vclogger_on(client, message):
    if len(message.command) < 2:
        return await message.reply_text(
            "Usage:\n/vclogger on\n/vclogger off"
        )

    chat_id = message.chat.id
    opt = message.command[1].lower()

    if opt == "on":
        VC_LOGGER.add(chat_id)
        await message.reply_text("✅ VC Logger Enabled")
    elif opt == "off":
        VC_LOGGER.discard(chat_id)
        await message.reply_text("❌ VC Logger Disabled")


@userbot.one.on_message(filters.video_chat_members_invited & filters.group)
async def fake_vc_join(client, message):
    chat_id = message.chat.id
    if chat_id not in VC_LOGGER:
        return

    await asyncio.sleep(2)

    for user in message.video_chat_members_invited.users:
        await message.reply_text(
            f"""🤖 **ROOHI VC LOGGER**

#JoinVideoChat
👤 NAME : {user.first_name}
🆔 ID : `{user.id}`
🔗 USER : @{user.username if user.username else "None"}
ACTION : IGNORED
"""
        )