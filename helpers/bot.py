# A Simple Telegram Bot, which will send you current playing song's lyrics from spotify to telegram

# Copyright(C) 2021-Present Gautam Kumar < https://github.com/gautamajay52 >

import html
import logging
import os
import re

from tekore._sender import client
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler, CommandHandler, Dispatcher
from telegraph import Telegraph

from helpers.spotify import mySpotify
logger = logging.getLogger(__name__)

client_id = os.environ.get("CLIENT_ID")
client_secret = os.environ.get("CLIENT_SECRET")
refresh_token = os.environ.get("REFRESH_TOKEN")
telegraph_token = os.environ.get("TELEGRAPH")
premium = os.environ.get("IS_PREMIUM", False)

tel = Telegraph(access_token=telegraph_token)

buttons = []

if premium:
    buttons.append(
        [
            InlineKeyboardButton("Prev", callback_data="prev"),
            InlineKeyboardButton("Pause", callback_data="pause"),
            InlineKeyboardButton("Play", callback_data="play"),
            InlineKeyboardButton("Next", callback_data="next"),
        ]
    )

buttons.append([InlineKeyboardButton("Lyrics", callback_data="lyrics")])




def start_handler(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text(
        text="💭 Select Your Option 💭",
        reply_markup=InlineKeyboardMarkup(buttons),
        quote=True,
        parse_mode="html",
    )


def button_press(update, context):
    """Function to handle the button press"""
    callback_query = update.callback_query
    callback_query.answer()
    pre = callback_query.message.text_html
    if pre == "💭 Select Your Option 💭":
        callback_query.delete_message()
    else:
        callback_query.edit_message_text(pre, parse_mode="html")

    data = callback_query.data

    spoti = mySpotify(client_id, client_secret, refresh_token)

    if data == "lyrics":
        title = spoti.my_song_title()
        if title:
            msg = callback_query.message.reply_text(
                f"⏳ <b>Searching for: {title}</b>", parse_mode="html"
            )
        else:
            msg = callback_query.message.reply_text(
                "💭 <b>Nothing is Playing</b>",
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode="html",
            )
            return
        try:
            lyrics = spoti.parse_lyrics()
        except Exception as g_a:
            callback_query.message.reply_text(
                g_a, reply_markup=InlineKeyboardMarkup(buttons), parse_mode="html"
            )
            return

        if lyrics:
            out = tel.create_page(
                title="🔊 " + title,
                author_name="mySPOTIFY",
                author_url="https://github.com/gautamajay52/mySPOTIFY",
                html_content=lyrics,
            )
            url = out["url"]
            msg.edit_text(
                f"""🔊 <a href="{url}">{title}</a>""",
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode="html",
            )
        else:
            msg.edit_text(
                "💭 <b>Are you Listening your own song ?</b>",
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode="html",
            )
    # not tested (all premium features)
    elif data == "pause":
        spoti.pause_song()
    elif data == "prev":
        spoti.prev_song()
    elif data == "next":
        spoti.next_song()
    elif data == "play":
        spoti.resume_song()


def get_dispatcher(bot):
    """Create and return dispatcher instances"""
    dispatcher = Dispatcher(bot, None, workers=0)

    dispatcher.add_handler(CommandHandler("start", start_handler))
    dispatcher.add_handler(CallbackQueryHandler(button_press))

    return dispatcher
