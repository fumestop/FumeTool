import json
import asyncio
from datetime import datetime

import aiomysql

with open("config.json") as json_file:
    data = json.load(json_file)
    db_name = data["db_name"]
    db_user = data["db_user"]
    db_password = data["db_password"]
    db_host = data["db_host"]
    db_port = data["db_port"]


async def guild_exists(guild_id: int):
    pool = await aiomysql.create_pool(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password,
        db=db_name,
        autocommit=True,
        loop=asyncio.get_event_loop(),
    )

    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "select GUILD_ID from guilds where GUILD_ID = %s;", (guild_id,)
            )

            res = await cur.fetchone()

    pool.close()
    await pool.wait_closed()

    if not res:
        return False

    return True


async def add_guild(guild_id: int):
    pool = await aiomysql.create_pool(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password,
        db=db_name,
        autocommit=True,
        loop=asyncio.get_event_loop(),
    )

    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("insert into guilds (GUILD_ID) values (%s);", (guild_id,))

    pool.close()
    await pool.wait_closed()


async def is_premium_user(user_id: int):
    pool = await aiomysql.create_pool(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password,
        db=db_name,
        autocommit=True,
        loop=asyncio.get_event_loop(),
    )

    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "select PREMIUM from users where USER_ID = %s;", (user_id,)
            )

            res = await cur.fetchone()

    pool.close()
    await pool.wait_closed()

    if not res or not res[0]:
        return False

    return True


async def is_premium_guild(user_id: int):
    pool = await aiomysql.create_pool(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password,
        db=db_name,
        autocommit=True,
        loop=asyncio.get_event_loop(),
    )

    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "select PREMIUM from guilds where GUILD_ID = %s;", (user_id,)
            )

            res = await cur.fetchone()

    pool.close()
    await pool.wait_closed()

    if not res or not res[0]:
        return False

    return True


async def get_mod_log_channel(guild_id: int):
    pool = await aiomysql.create_pool(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password,
        db=db_name,
        autocommit=True,
        loop=asyncio.get_event_loop(),
    )

    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "select MOD_LOG_CHANNEL from guilds where GUILD_ID = %s;", (guild_id,)
            )

            res = await cur.fetchone()

    pool.close()
    await pool.wait_closed()

    return None if not res else res[0]


async def update_mod_log_channel(guild_id: int, channel_id: int):
    pool = await aiomysql.create_pool(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password,
        db=db_name,
        autocommit=True,
        loop=asyncio.get_event_loop(),
    )

    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "update guilds set MOD_LOG_CHANNEL = %s where GUILD_ID = %s;",
                (channel_id, guild_id),
            )

    pool.close()
    await pool.wait_closed()


async def get_member_log_channel(guild_id: int):
    pool = await aiomysql.create_pool(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password,
        db=db_name,
        autocommit=True,
        loop=asyncio.get_event_loop(),
    )

    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "select MEMBER_LOG_CHANNEL from guilds where GUILD_ID = %s;",
                (guild_id,),
            )

            res = await cur.fetchone()

    pool.close()
    await pool.wait_closed()

    return None if not res else res[0]


async def update_member_log_channel(guild_id: int, channel_id: int):
    pool = await aiomysql.create_pool(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password,
        db=db_name,
        autocommit=True,
        loop=asyncio.get_event_loop(),
    )

    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "update guilds set MEMBER_LOG_CHANNEL = %s where GUILD_ID = %s;",
                (channel_id, guild_id),
            )

    pool.close()
    await pool.wait_closed()


async def get_case_id(guild_id: int):
    pool = await aiomysql.create_pool(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password,
        db=db_name,
        autocommit=True,
        loop=asyncio.get_event_loop(),
    )

    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "select CASE_ID from guilds where GUILD_ID = %s;", (guild_id,)
            )

            res = await cur.fetchone()

    pool.close()
    await pool.wait_closed()

    return 1 if not res[0] else res[0]


async def update_case_id(guild_id: int):
    pool = await aiomysql.create_pool(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password,
        db=db_name,
        autocommit=True,
        loop=asyncio.get_event_loop(),
    )

    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "update guilds set CASE_ID = CASE_ID + 1 where GUILD_ID = %s;",
                (guild_id,),
            )

    pool.close()
    await pool.wait_closed()


async def get_welcome_message(guild_id: int):
    pool = await aiomysql.create_pool(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password,
        db=db_name,
        autocommit=True,
        loop=asyncio.get_event_loop(),
    )

    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "select WELCOME_MESSAGE from guilds where GUILD_ID = %s;", (guild_id,)
            )

            res = await cur.fetchone()

    pool.close()
    await pool.wait_closed()

    return None if not res else res[0]


async def update_welcome_message(guild_id: int, message: str):
    pool = await aiomysql.create_pool(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password,
        db=db_name,
        autocommit=True,
        loop=asyncio.get_event_loop(),
    )

    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "update guilds set WELCOME_MESSAGE = %s where GUILD_ID = %s;",
                (message, guild_id),
            )

    pool.close()
    await pool.wait_closed()


async def set_afk(user_id: int, guild_id: int, reason: str):
    pool = await aiomysql.create_pool(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password,
        db=db_name,
        autocommit=True,
        loop=asyncio.get_event_loop(),
    )

    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "insert into afk (USER_ID, GUILD_ID, START, REASON) values (%s, %s, %s, %s);",
                (user_id, guild_id, datetime.now(), reason),
            )

    pool.close()
    await pool.wait_closed()


async def is_afk(user_id: int, guild_id: int):
    pool = await aiomysql.create_pool(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password,
        db=db_name,
        autocommit=True,
        loop=asyncio.get_event_loop(),
    )

    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "select USER_ID from afk where USER_ID = %s and GUILD_ID = %s;",
                (user_id, guild_id),
            )
            res = await cur.fetchone()

    pool.close()
    await pool.wait_closed()

    return True if res else False


async def get_afk_details(user_id: int, guild_id: int):
    pool = await aiomysql.create_pool(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password,
        db=db_name,
        autocommit=True,
        loop=asyncio.get_event_loop(),
    )

    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "select * from afk where USER_ID = %s and GUILD_ID = %s;",
                (user_id, guild_id),
            )
            res = await cur.fetchone()

    pool.close()
    await pool.wait_closed()

    return {"user_id": res[0], "guild_id": res[1], "start": res[2], "reason": res[3]}


async def get_afk_members(guild_id: int):
    pool = await aiomysql.create_pool(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password,
        db=db_name,
        autocommit=True,
        loop=asyncio.get_event_loop(),
    )

    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "select USER_ID from afk where GUILD_ID = %s;", (guild_id,)
            )
            res = await cur.fetchall()

    pool.close()
    await pool.wait_closed()

    return res


async def remove_afk(user_id: int, guild_id):
    pool = await aiomysql.create_pool(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password,
        db=db_name,
        autocommit=True,
        loop=asyncio.get_event_loop(),
    )

    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "delete from afk where USER_ID = %s and GUILD_ID = %s;",
                (user_id, guild_id),
            )
            res = await cur.fetchone()

    pool.close()
    await pool.wait_closed()

    return res
