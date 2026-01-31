import asyncio
from time import time
from pyrogram import filters
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    Message
)
from Oneforall import app
from Oneforall.core.mongo import mongodb

games = {}
xoxo_db = mongodb.xoxo_leaderboard

EMPTY = "⬜"
X = "❌"
O = "⭕"
TIMEOUT = 60  # seconds

WIN = [
    [0,1,2],[3,4,5],[6,7,8],
    [0,3,6],[1,4,7],[2,5,8]
]

# ───── HELPERS ─────

def check(board):
    for a,b,c in WIN:
        if board[a] == board[b] == board[c] != EMPTY:
            return board[a]
    if EMPTY not in board:
        return "draw"
    return None

def smart_bot(board):
    for i in range(9):
        if board[i] == EMPTY:
            board[i] = O
            if check(board) == O:
                return i
            board[i] = EMPTY
    for i in range(9):
        if board[i] == EMPTY:
            board[i] = X
            if check(board) == X:
                board[i] = EMPTY
                return i
            board[i] = EMPTY
    if board[4] == EMPTY:
        return 4
    for i in range(9):
        if board[i] == EMPTY:
            return i

def kb(gid, board):
    rows = []
    for i in range(0,9,3):
        rows.append([
            InlineKeyboardButton(board[i], callback_data=f"xoxo:{gid}:{i}"),
            InlineKeyboardButton(board[i+1], callback_data=f"xoxo:{gid}:{i+1}"),
            InlineKeyboardButton(board[i+2], callback_data=f"xoxo:{gid}:{i+2}")
        ])
    rows.append([
        InlineKeyboardButton("🔁 Rematch", callback_data=f"xoxo_rematch:{gid}"),
        InlineKeyboardButton("🛑 End", callback_data=f"xoxo_end:{gid}")
    ])
    return InlineKeyboardMarkup(rows)

async def add_win(uid):
    await xoxo_db.update_one(
        {"user_id": uid},
        {"$inc": {"wins": 1}},
        upsert=True
    )

# ───── /xoxo ─────

@app.on_message(filters.command("xoxo"))
async def start(_, m: Message):
    gid = m.chat.id
    uid = m.from_user.id

    games[gid] = {
        "board": [EMPTY]*9,
        "p1": uid,
        "p2": None,
        "turn": X,
        "mode": "friend",
        "last": time()
    }

    kb_start = InlineKeyboardMarkup([
        [InlineKeyboardButton("Join Game 🎮", callback_data=f"xoxo_join:{gid}")],
        [InlineKeyboardButton("Play vs Bot 🤖", callback_data=f"xoxo_bot:{gid}")]
    ])

    await m.reply(
        f"❌ **Tic-Tac-Toe Challenge! ⭕**\n\n"
        f"👤 Player 1: {m.from_user.mention}\n\n"
        f"Choose mode:",
        reply_markup=kb_start
    )

    asyncio.create_task(timeout_checker(gid))

# ───── TIMEOUT ─────

async def timeout_checker(gid):
    while gid in games:
        await asyncio.sleep(5)
        g = games.get(gid)
        if time() - g["last"] > TIMEOUT:
            winner = g["p2"] if g["turn"] == X else g["p1"]
            games.pop(gid, None)
            await app.send_message(
                gid,
                f"⏱ **Timeout!**\nWinner: <a href='tg://user?id={winner}'>Player</a>"
            )
            await add_win(winner)

# ───── JOIN ─────

@app.on_callback_query(filters.regex("^xoxo_join"))
async def join(_, q: CallbackQuery):
    gid = int(q.data.split(":")[1])
    g = games.get(gid)

    if not g or g["p2"]:
        return await q.answer("Game already started")

    if q.from_user.id == g["p1"]:
        return await q.answer("You are Player 1")

    g["p2"] = q.from_user.id
    g["last"] = time()

    await q.message.edit_text(
        f"🎮 **Game Started!**\n\n"
        f"❌ Player 1\n"
        f"⭕ Player 2\n\n"
        f"**Turn:** ❌",
        reply_markup=kb(gid, g["board"])
    )

# ───── BOT MODE ─────

@app.on_callback_query(filters.regex("^xoxo_bot"))
async def bot(_, q: CallbackQuery):
    gid = int(q.data.split(":")[1])
    g = games[gid]
    g["p2"] = 0
    g["mode"] = "bot"
    g["last"] = time()

    await q.message.edit_text(
        f"🤖 **Bot Mode Started**\n\n"
        f"❌ You | ⭕ Bot\n\n"
        f"Your Turn:",
        reply_markup=kb(gid, g["board"])
    )

# ───── MOVE ─────

@app.on_callback_query(filters.regex("^xoxo:"))
async def move(_, q: CallbackQuery):
    _, gid, pos = q.data.split(":")
    gid, pos = int(gid), int(pos)

    g = games.get(gid)
    if not g:
        return

    uid = q.from_user.id
    if g["board"][pos] != EMPTY:
        return await q.answer("Used")

    if g["turn"] == X and uid != g["p1"]:
        return await q.answer("Not your turn")
    if g["turn"] == O and g["mode"] == "friend" and uid != g["p2"]:
        return await q.answer("Not your turn")

    g["board"][pos] = g["turn"]
    g["last"] = time()

    res = check(g["board"])
    if res:
        return await finish(q, gid, res)

    g["turn"] = O

    if g["mode"] == "bot":
        bp = smart_bot(g["board"])
        g["board"][bp] = O
        res = check(g["board"])
        if res:
            return await finish(q, gid, res)
        g["turn"] = X
    else:
        g["turn"] = X

    await q.message.edit_text(
        f"❌ Player 1 | ⭕ {'Bot' if g['mode']=='bot' else 'Player 2'}\n\n"
        f"**Turn:** {g['turn']}",
        reply_markup=kb(gid, g["board"])
    )

# ───── FINISH ─────

async def finish(q, gid, res):
    g = games.pop(gid)
    if res != "draw":
        winner = g["p1"] if res == X else g["p2"]
        await add_win(winner)
        text = f"🏆 **Winner: {res}**"
    else:
        text = "🤝 **Draw Match**"

    await q.message.edit_text(text, reply_markup=kb(gid, g["board"]))

# ───── REMATCH ─────

@app.on_callback_query(filters.regex("^xoxo_rematch"))
async def rematch(_, q):
    gid = int(q.data.split(":")[1])
    if gid not in games:
        return

    games[gid]["board"] = [EMPTY]*9
    games[gid]["turn"] = X
    games[gid]["last"] = time()

    await q.message.edit_text(
        "🔁 **Rematch Started**\n❌ Turn",
        reply_markup=kb(gid, games[gid]["board"])
    )

# ───── END ─────

@app.on_callback_query(filters.regex("^xoxo_end"))
async def end(_, q):
    gid = int(q.data.split(":")[1])
    games.pop(gid, None)
    await q.message.edit_text("🛑 **Game Ended**")