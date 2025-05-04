# Don't Remove Credit @CodeFlix_Bots, @rohit_1888
# Ask Doubt on telegram @CodeflixSupport
#
# Copyright (C) 2025 by Codeflix-Bots@Github, < https://github.com/Codeflix-Bots >.
#
# This file is part of < https://github.com/Codeflix-Bots/FileStore > project,
# and is released under the MIT License.
# Please see < https://github.com/Codeflix-Bots/FileStore/blob/master/LICENSE >
#
# All rights reserved.
#

import asyncio
import os
import random
import sys
import time
from datetime import datetime, timedelta
from pyrogram import Client, filters, __version__
from pyrogram.enums import ParseMode, ChatAction
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardMarkup, ChatInviteLink, ChatPrivileges
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, UserNotParticipant
from bot import Bot
from config import *
from helper_func import *
from database.database import *
from utils import verify_user, check_token

BAN_SUPPORT = f"{BAN_SUPPORT}"

@Bot.on_message(filters.command('start') & filters.private)
async def start_command(client: Client, message: Message):
    user_id = message.from_user.id

    # Ban Check
    banned_users = await db.get_ban_users()
    if user_id in banned_users:
        return await message.reply_text(
            "<b>⛔️ Tum BANNED ho is bot se.</b>\n\n<i>Agar yeh galti se hua hai to support se baat karo.</i>",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Support", url=BAN_SUPPORT)]])
        )

    # Force Subscription Check
    if not await is_subscribed(client, user_id):
        return await not_joined(client, message)

    # Agar /start ke sath argument hai
    if len(message.command) > 1:
        data = message.command[1]

        # Agar link verification ka hai
        if "-" in data and data.split("-", 1)[0] == "verify":
            try:
                userid = data.split("-", 2)[1]
                token = data.split("-", 3)[2]

                if str(user_id) != str(userid):
                    return await message.reply_text("<b>Link invalid ya expire ho chuka hai.</b>")

                if await check_token(client, userid, token):
                    await verify_user(client, userid, token)
                    return await message.reply_text(
                        f"<b>Hey {message.from_user.mention}, Verification complete!\nAb tumhe raat tak unlimited access milega.</b>"
                    )
                else:
                    return await message.reply_text("<b>Link invalid ya expire ho chuka hai.</b>")

            except Exception as e:
                print(f"Verify error: {e}")
                return await message.reply_text("<b>Verification me error aa gaya.</b>")

        # Agar file link hai
        try:
            string = await decode(data)
            argument = string.split("-")

            ids = []
            if len(argument) == 3:
                start = int(int(argument[1]) / abs(client.db_channel.id))
                end = int(int(argument[2]) / abs(client.db_channel.id))
                ids = range(start, end + 1) if start <= end else list(range(start, end - 1, -1))
            elif len(argument) == 2:
                ids = [int(int(argument[1]) / abs(client.db_channel.id))]
            else:
                return await message.reply_text("<b>Link galat hai ya expire ho gaya hai.</b>")

            temp = await message.reply("<b>⏳ File process ho rahi hai...</b>")
            messages = await get_messages(client, ids)
            await temp.delete()

            sent = []
            for msg in messages:
                caption = (CUSTOM_CAPTION.format(
                    previouscaption=msg.caption.html if msg.caption else "",
                    filename=msg.document.file_name) if CUSTOM_CAPTION and msg.document else msg.caption.html if msg.caption else ""
                )

                # Agar verify required hai
                if VERIFY and not await check_verification(client, user_id):
                    return await message.reply_text(
                        "<b>Tum verified nahi ho! Pehle verify karo.</b>",
                        reply_markup=InlineKeyboardMarkup([
                            [InlineKeyboardButton("Verify Now", url=await get_token(client, user_id, f"https://t.me/{BOT_USERNAME}?start="))],
                            [InlineKeyboardButton("How to verify?", url=VERIFY_TUTORIAL)]
                        ])
                    )

                sent_msg = await msg.copy(chat_id=user_id, caption=caption, parse_mode=ParseMode.HTML, protect_content=PROTECT_CONTENT)
                sent.append(sent_msg)

            # Auto Delete Timer
            FILE_AUTO_DELETE = await db.get_del_timer()
            if FILE_AUTO_DELETE > 0:
                note = await message.reply(f"<b>Yeh file {get_exp_time(FILE_AUTO_DELETE)} me delete ho jayegi. Save ya forward kar lo.</b>")
                await asyncio.sleep(FILE_AUTO_DELETE)

                for m in sent:
                    try: await m.delete()
                    except: pass

                reload_url = f"https://t.me/{client.username}?start={data}"
                await note.edit(
                    "<b>File delete ho gayi hai. Neeche button dabao firse pane ke liye:</b>",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Get Again", url=reload_url)]])
                )
            return

        except Exception as e:
            print(f"File fetch error: {e}")
            return await message.reply_text("<b>File link galat hai ya error aa gaya.</b>")

    # Default welcome message
    return await message.reply_photo(
        photo=START_PIC,
        caption=START_MSG.format(
            first=message.from_user.first_name,
            last=message.from_user.last_name,
            username='@' + message.from_user.username if message.from_user.username else None,
            mention=message.from_user.mention,
            id=message.from_user.id
        ),
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("• More Channels •", url="https://t.me/+UwsANaNOTWMxMGY1")],
            [InlineKeyboardButton("About", callback_data="about"), InlineKeyboardButton("Help", callback_data="help")]
        ])
                                                 )
        await message.reply_photo(
            photo=START_PIC,
            caption=START_MSG.format(
                first=message.from_user.first_name,
                last=message.from_user.last_name,
                username=None if not message.from_user.username else '@' + message.from_user.username,
                mention=message.from_user.mention,
                id=message.from_user.id
            ),
            reply_markup=reply_markup,
            message_effect_id=5104841245755180586)  # 🔥
        
        return



#=====================================================================================##
# Don't Remove Credit @CodeFlix_Bots, @rohit_1888
# Ask Doubt on telegram @CodeflixSupport



# Create a global dictionary to store chat data
chat_data_cache = {}

async def not_joined(client: Client, message: Message):
    temp = await message.reply("<b><i>ᴡᴀɪᴛ ᴀ sᴇᴄ..</i></b>")

    user_id = message.from_user.id
    buttons = []
    count = 0

    try:
        all_channels = await db.show_channels()  # Should return list of (chat_id, mode) tuples
        for total, chat_id in enumerate(all_channels, start=1):
            mode = await db.get_channel_mode(chat_id)  # fetch mode 

            await message.reply_chat_action(ChatAction.TYPING)

            if not await is_sub(client, user_id, chat_id):
                try:
                    # Cache chat info
                    if chat_id in chat_data_cache:
                        data = chat_data_cache[chat_id]
                    else:
                        data = await client.get_chat(chat_id)
                        chat_data_cache[chat_id] = data

                    name = data.title

                    # Generate proper invite link based on the mode
                    if mode == "on" and not data.username:
                        invite = await client.create_chat_invite_link(
                            chat_id=chat_id,
                            creates_join_request=True,
                            expire_date=datetime.utcnow() + timedelta(seconds=FSUB_LINK_EXPIRY) if FSUB_LINK_EXPIRY else None
                            )
                        link = invite.invite_link

                    else:
                        if data.username:
                            link = f"https://t.me/{data.username}"
                        else:
                            invite = await client.create_chat_invite_link(
                                chat_id=chat_id,
                                expire_date=datetime.utcnow() + timedelta(seconds=FSUB_LINK_EXPIRY) if FSUB_LINK_EXPIRY else None)
                            link = invite.invite_link

                    buttons.append([InlineKeyboardButton(text=name, url=link)])
                    count += 1
                    await temp.edit(f"<b>{'! ' * count}</b>")

                except Exception as e:
                    print(f"Error with chat {chat_id}: {e}")
                    return await temp.edit(
                        f"<b><i>! Eʀʀᴏʀ, Cᴏɴᴛᴀᴄᴛ ᴅᴇᴠᴇʟᴏᴘᴇʀ ᴛᴏ sᴏʟᴠᴇ ᴛʜᴇ ɪssᴜᴇs @Prime_Movie_Request_bot</i></b>\n"
                        f"<blockquote expandable><b>Rᴇᴀsᴏɴ:</b> {e}</blockquote>"
                    )

        # Retry Button
        try:
            buttons.append([
                InlineKeyboardButton(
                    text='♻️ Tʀʏ Aɢᴀɪɴ',
                    url=f"https://t.me/{client.username}?start={message.command[1]}"
                )
            ])
            
        except IndexError:
            pass

        await message.reply_photo(
            photo=FORCE_PIC,
            caption=FORCE_MSG.format(
                first=message.from_user.first_name,
                last=message.from_user.last_name,
                username=None if not message.from_user.username else '@' + message.from_user.username,
                mention=message.from_user.mention,
                id=message.from_user.id
            ),
            reply_markup=InlineKeyboardMarkup(buttons),
        )

    except Exception as e:
        print(f"Final Error: {e}")
        await temp.edit(
            f"<b><i>! Eʀʀᴏʀ, Cᴏɴᴛᴀᴄᴛ ᴅᴇᴠᴇʟᴏᴘᴇʀ ᴛᴏ sᴏʟᴠᴇ ᴛʜᴇ ɪssᴜᴇs @Prime_Movie_Request_bot</i></b>\n"
            f"<blockquote expandable><b>Rᴇᴀsᴏɴ:</b> {e}</blockquote>"
        )

#=====================================================================================##

@Bot.on_message(filters.command('commands') & filters.private & admin)
async def bcmd(bot: Bot, message: Message):        
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("• ᴄʟᴏsᴇ •", callback_data = "close")]])
    await message.reply(text=CMD_TXT, reply_markup = reply_markup, quote= True)
