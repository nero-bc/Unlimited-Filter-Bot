import os

if bool(os.environ.get("WEBHOOK", False)):
    from sample_config import Config
else:
    from config import Config

from pyrogram import filters, Client
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from database.connections_mdb import add_connection, all_connections, if_active, delete_connection



@Client.on_message((filters.private | filters.group) & filters.command(Config.CONNECT_COMMAND))
async def addconnection(client,message):
    userid = message.from_user.id
    chat_type = message.chat.type

    if chat_type == "private":
        try:
            cmd, group_id = message.text.split(" ", 1)
        except:
            await message.reply_text(
                "<b>Enter In Correct Format!</b>\n\n"
                "<code>/connect GroupID</code>\n\n"
                "<i>Get Your Group Id By Adding This Bot To Your Group And Use  <code>/id</code></i>",
                quote=True
            )
            return

    elif (chat_type == "group") or (chat_type == "supergroup"):
        group_id = message.chat.id

    try:
        st = await client.get_chat_member(group_id, userid)
        if (st.status == "administrator") or (st.status == "creator") or (str(userid) in Config.AUTH_USERS):
            pass
        else:
            await message.reply_text("**You Should Be An Admin In Given Group!**", quote=True)
            return
    except Exception as e:
        print(e)
        await message.reply_text(
            "**🚮 Invalid Group ID**\n\n**🛃 If Correct, Make Sure I'm Present And Admin In Your Group !**",
            quote=True
        )
        return

    try:
        st = await client.get_chat_member(group_id, "me")
        if st.status == "administrator":
            ttl = await client.get_chat(group_id)
            title = ttl.title

            addcon = await add_connection(str(group_id), str(userid))
            if addcon:
                await message.reply_text(
                    f"**🛂 Sucessfully Connected To** **{title}**\n**🚼 Now, Manage Your Group From My PM (Bot)!**",
                    quote=True,
                    parse_mode="md"
                )
                if (chat_type == "group") or (chat_type == "supergroup"):
                    await client.send_message(
                        userid,
                        f"**Connected To** **{title}** !",
                        parse_mode="md"
                    )
            else:
                await message.reply_text(
                    "**🛂 You're Already Connected To This Chat !**",
                    quote=True
                )
        else:
            await message.reply_text("**🛂 Add Me As An Admin In Group 🛂**", quote=True)
    except Exception as e:
        print(e)
        await message.reply_text(
            "Some Error Occured! Try Again Later.",
            quote=True
        )
        return


@Client.on_message((filters.private | filters.group) & filters.command(Config.DISCONNECT_COMMAND))
async def deleteconnection(client,message):
    userid = message.from_user.id
    chat_type = message.chat.type

    if chat_type == "private":
        await message.reply_text("**🛂 Run /connections To View Or Disconnect From Groups !**", quote=True)

    elif (chat_type == "group") or (chat_type == "supergroup"):
        group_id = message.chat.id

        st = await client.get_chat_member(group_id, userid)
        if not ((st.status == "administrator") or (st.status == "creator") or (str(userid) in Config.AUTH_USERS)):
            return

        delcon = await delete_connection(str(userid), str(group_id))
        if delcon:
            await message.reply_text("**🚼 Successfully Disconnected From This Chat 🚼**", quote=True)
        else:
            await message.reply_text("**♿ This Chat Isn't Connected To Me !**\n**🚼Do /connect To Connect.**", quote=True)


@Client.on_message(filters.private & filters.command(["connections"]))
async def connections(client,message):
    userid = message.from_user.id

    groupids = await all_connections(str(userid))
    if groupids is None:
        await message.reply_text(
            "**🛂 There Are No Active Connections !\n🛂 **Connect To Some Groups First.**",
            quote=True
        )
        return
    buttons = []
    for groupid in groupids:
        try:
            ttl = await client.get_chat(int(groupid))
            title = ttl.title
            active = await if_active(str(userid), str(groupid))
            if active:
                act = " - ACTIVE"
            else:
                act = ""
            buttons.append(
                [
                    InlineKeyboardButton(
                        text=f"{title}{act}", callback_data=f"groupcb:{groupid}:{title}:{act}"
                    )
                ]
            )
        except:
            pass
    if buttons:
        await message.reply_text(
            "🛂 **Your Connected Group Details**;\n\n",
            reply_markup=InlineKeyboardMarkup(buttons),
            quote=True
        )
