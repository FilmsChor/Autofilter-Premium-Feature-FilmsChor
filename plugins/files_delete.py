# ─────────────────────────────────────────────
# Powered by Roaroic | Developer Channel: @roaroic0
# https://t.me/roaroic0
# ─────────────────────────────────────────────
import re
import logging
from pyrogram import Client, filters
from info import DELETE_CHANNELS, MOVIE_UPDATE_CHANNEL
from database.ia_filterdb import Media, Media2, unpack_new_file_id
from database import db
logger = logging.getLogger(__name__)

media_filter = filters.document | filters.video | filters.audio


@Client.on_message(filters.chat(DELETE_CHANNELS) & media_filter)
async def deletemultiplemedia(bot, message):
    """Delete Multiple files from database"""

    for file_type in ("document", "video", "audio"):
        media = getattr(message, file_type, None)
        if media is not None:
            break
    else:
        return

    file_id, file_ref = unpack_new_file_id(media.file_id)
    if await Media.count_documents({'file_id': file_id}):
        result = await Media.collection.delete_one({
            '_id': file_id,
        })
    else:
        result = await Media2.collection.delete_one({
            '_id': file_id,
        })
    if result.deleted_count:
        logger.info('File is successfully deleted from database.')
    else:
        file_name = re.sub(r"(_|\-|\.|\+)", " ", str(media.file_name))
        result = await Media.collection.delete_many({
            'file_name': file_name,
            'file_size': media.file_size,
            'mime_type': media.mime_type
            })
        if result.deleted_count:
            logger.info('File is successfully deleted from database.')
        else:
            result = await Media2.collection.delete_many({
                'file_name': file_name,
                'file_size': media.file_size,
                'mime_type': media.mime_type
                })
            if result.deleted_count:
                logger.info('File is successfully deleted from database.')
            else:
                result = await Media.collection.delete_many({
                    'file_name': media.file_name,
                    'file_size': media.file_size,
                    'mime_type': media.mime_type
                })
                if result.deleted_count:
                    logger.info('File is successfully deleted from database.')
                else:
                    result = await Media2.collection.delete_many({
                        'file_name': media.file_name,
                        'file_size': media.file_size,
                        'mime_type': media.mime_type
                    })
                    if result.deleted_count:
                        logger.info('File is successfully deleted from database.')
                    else:
                        logger.info('File not found in database.')

    if result.deleted_count:
        try:
            filename = (
                getattr(media, "file_name", None)
                or getattr(media, "title", None)
                or ((message.caption or "").splitlines()[0].strip() if (message.caption or "").strip() else None)
                or f"Telegram_{media.file_unique_id}"
            )
            from plugins.channel import extract_media_info, update_movie_message
            base_name = extract_media_info(filename, message.caption or "")["base_name"]
            movie_doc = await db.movie_updates.find_one({"_id": base_name})
            if movie_doc:
                # A delete-channel action resets this title's announcement cycle.
                # This lets the same movie/file be announced again immediately,
                # even when its previous post was less than 24 hours old.
                old_message_id = movie_doc.get("message_id")
                if old_message_id:
                    try:
                        await bot.delete_messages(MOVIE_UPDATE_CHANNEL, old_message_id)
                    except Exception:
                        logger.warning("[MOVIE UPDATE] Could not delete old announcement %s", old_message_id)

                # Cancel any delayed update so it cannot recreate the old post.
                try:
                    from plugins.channel import pending_updates
                    pending = pending_updates.pop(base_name, None)
                    if pending and not pending.cancelled():
                        pending.cancel()
                except Exception:
                    logger.exception("[MOVIE UPDATE] Could not cancel pending update for %s", base_name)

                # Remove the complete announcement record, including its 24-hour
                # timestamp and file list. Search database deletion remains unchanged.
                await db.movie_updates.delete_one({"_id": base_name})
                logger.info(
                    "[MOVIE UPDATE] Reset announcement cycle for deleted file %s (%s)",
                    filename, base_name
                )
        except Exception:
            logger.exception("[MOVIE UPDATE] Could not sync deleted file with movie announcement")