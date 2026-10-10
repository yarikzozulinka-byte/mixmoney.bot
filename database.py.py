import aiosqlite

DB_NAME = "bot_database.db"

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                balance REAL DEFAULT 0.0,
                referrer_id INTEGER DEFAULT NULL,
                total_referrals INTEGER DEFAULT 0,
                today_referrals INTEGER DEFAULT 0
            )
        """)
        await db.commit()

async def get_or_create_user(user_id: int, username: str, full_name: str, referrer_id: int = None):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor:
            user = await cursor.fetchone()
            
        if not user:
            valid_referrer = None
            if referrer_id and referrer_id != user_id:
                async with db.execute("SELECT user_id FROM users WHERE user_id = ?", (referrer_id,)) as cursor:
                    if await cursor.fetchone():
                        valid_referrer = referrer_id

            await db.execute(
                "INSERT INTO users (user_id, username, full_name, referrer_id) VALUES (?, ?, ?, ?)",
                (user_id, username, full_name, valid_referrer)
            )
            
            if valid_referrer:
                await db.execute(
                    "UPDATE users SET total_referrals = total_referrals + 1, today_referrals = today_referrals + 1 WHERE user_id = ?",
                    (valid_referrer,)
                )
            
            await db.commit()
            return await get_user(user_id)
        return user

async def get_user(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor:
            return await cursor.fetchone()
