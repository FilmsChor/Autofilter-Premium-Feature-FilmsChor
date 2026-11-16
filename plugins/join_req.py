# ─────────────────────────────────────────────
# Powered by Roaroic | Developer Channel: @roaroic0
# https://t.me/roaroic0
# ─────────────────────────────────────────────
#Join Telegram Channel - @roaroic0

import logging

from pyrogram import Client, filters
from pyrogram.types import ChatJoinRequest
from database.users_chats_db import db
from info import ADMINS, AUTH_CHANNELS, AUTH_REQ_CHANNELS
from pyrogram.filters import create

logger = logging.getLogger(__name__)

# Listen for requests from BOTH force-sub channel lists.
JOIN_REQUEST_CHANNELS = set(AUTH_CHANNELS) | set(AUTH_REQ_CHANNELS)

def is_auth_req_channel(_, __, update):
    return update.chat.id in JOIN_REQUEST_CHANNELS

@Client.on_chat_join_request(create(is_auth_req_channel))
async def join_reqs(client, message: ChatJoinRequest):
    try:
        await db.add_join_req(message.from_user.id, message.chat.id)
        logger.info(
            "FORCE JOIN REQUEST RECEIVED and saved: user=%s channel=%s",
            message.from_user.id, message.chat.id
        )
    except Exception:
        logger.exception(
            "FAILED saving force join request: user=%s channel=%s",
            message.from_user.id, message.chat.id
        )


@Client.on_message(filters.command("delreq") & filters.private & filters.user(ADMINS))
async def del_requests(client, message):
    await db.del_join_req()    
    await message.reply("<b>⚙ ꜱᴜᴄᴄᴇꜱꜱғᴜʟʟʏ ᴄʜᴀɴɴᴇʟ ʟᴇғᴛ ᴜꜱᴇʀꜱ ᴅᴇʟᴇᴛᴇᴅ</b>")
