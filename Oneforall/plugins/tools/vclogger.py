from pyrogram import filters
from Oneforall import app

VC_LOGGER = set()


@app.on_message(filters.command("vclogger") & filters.group)
async def vclogger_handler(_, message):
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


# 🔥 VC START
@app.on_message(filters.video_chat_started & filters.group)
async def vc_started(_, message):
    if message.chat.id not in VC_LOGGER:
        return

    await message.reply_text("🎧 **Video Chat Started**")


# 🔥 VC INVITE (THIS IS WHAT YOU WANT)
@app.on_message(filters.video_chat_members_invited & filters.group)
async def vc_invite(_, message):
    if message.chat.id not in VC_LOGGER:
        return

    invited = message.video_chat_members_invited.users
    for user in invited:
        await message.reply_text(
            f"""🤖 **ROOHI VC LOGGER**

#JoinVideoChat
👤 NAME : {user.first_name}
🆔 ID : `{user.id}`
🔗 USER : @{user.username if user.username else "None"}
ACTION : IGNORED
"""
        )