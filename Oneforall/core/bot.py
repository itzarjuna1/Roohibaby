from pyrogram import Client, errors
from pyrogram.enums import ChatMemberStatus

import config
from ..logging import LOGGER


class Hotty(Client):
    def __init__(self):
        LOGGER(__name__).info("Starting Bot...")

        super().__init__(
            name="Oneforall",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
            in_memory=True,
            max_concurrent_transmissions=7,
        )

    async def start(self):
        await super().start()

        # ─── BOT INFO ───
        self.id = self.me.id
        self.name = f"{self.me.first_name or ''} {self.me.last_name or ''}".strip()
        self.username = self.me.username or ""
        self.mention = self.me.mention

        # ─── SEND START MESSAGE ───
        try:
            await self.send_message(
                chat_id=config.LOGGER_ID,
                text=(
                    f"<u><b>» {self.mention} ʙᴏᴛ sᴛᴀʀᴛᴇᴅ :</b></u>\n\n"
                    f"ɪᴅ : <code>{self.id}</code>\n"
                    f"ɴᴀᴍᴇ : {self.name}\n"
                    f"ᴜsᴇʀɴᴀᴍᴇ : @{self.username}"
                ),
            )

        except (errors.ChannelInvalid, errors.PeerIdInvalid):
            LOGGER(__name__).error(
                "Bot cannot access LOGGER_ID. Add bot to log group/channel."
            )

        except Exception as ex:
            LOGGER(__name__).error(
                f"Failed to send log message → {type(ex).__name__}: {ex}"
            )

        # ─── CHECK ADMIN ───
        try:
            member = await self.get_chat_member(config.LOGGER_ID, self.id)

            if member.status != ChatMemberStatus.ADMINISTRATOR:
                LOGGER(__name__).error(
                    "Bot is not admin in log group/channel. Please promote it."
                )

        except Exception as ex:
            LOGGER(__name__).error(
                f"Failed to check admin status → {type(ex).__name__}: {ex}"
            )

        LOGGER(__name__).info(f"Bot started successfully as {self.name}")

    async def stop(self):
        LOGGER(__name__).info("Stopping Bot...")
        await super().stop()