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


async def add_tag(guild_id: int, user_id: int, name: str, content: str):
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
                "insert into Tags (GUILD_ID, USER_ID, NAME, CREATED_AT, CONTENT) "
                "values(%s, %s, %s, %s, %s);",
                (guild_id, user_id, name, datetime.now(), content),
            )

    pool.close()
    await pool.wait_closed()


async def get_tag_from_alias(guild_id: int, alias: str):
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
                "select * from Tags where GUILD_ID = %s and ALIASES like %s;",
                (guild_id, f"%{alias}%"),
            )

            res = await cur.fetchall()

    pool.close()
    await pool.wait_closed()

    if len(res) == 0:
        return []

    for _record in res:
        for _alias in _record[5].split("|"):
            if _alias == alias:
                return _record


async def get_tag(guild_id: int, name: str, check_alias: bool = True):
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
                "select * from Tags where GUILD_ID = %s and NAME = %s;",
                (guild_id, name),
            )

            res = await cur.fetchone()

    pool.close()
    await pool.wait_closed()

    return (
        res or await get_tag_from_alias(guild_id=guild_id, alias=name)
        if check_alias
        else res
    )


async def edit_tag(guild_id: int, name: str, content: str):
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
                "update Tags set CONTENT = %s where GUILD_ID = %s and NAME = %s;",
                (content, guild_id, name),
            )

    pool.close()
    await pool.wait_closed()


async def delete_tag(guild_id: int, name: str):
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
                "delete from Tags where GUILD_ID = %s and NAME = %s;", (guild_id, name)
            )

    pool.close()
    await pool.wait_closed()


async def all_tags(guild_id: int):
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
            await cur.execute("select NAME from Tags where GUILD_ID = %s;", (guild_id,))

            res = await cur.fetchall()

    pool.close()
    await pool.wait_closed()

    res = list(res)

    if len(res) != 0:
        for _index, _record in enumerate(res):
            res[_index] = _record[0]

        return res

    else:
        return []


async def search_tags(guild_id: int, query: str):
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
                "select NAME from Tags where GUILD_ID = %s and NAME like %s;",
                (guild_id, f"%{query}%"),
            )

            res1 = await cur.fetchall()

    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "select ALIASES from Tags where GUILD_ID = %s and ALIASES like %s;",
                (guild_id, f"%{query}%"),
            )

            res2 = await cur.fetchall()

    pool.close()
    await pool.wait_closed()

    if len(res1) != 0:
        for i, rec in enumerate(res1):
            res1[i] = rec[0]

    res2_new = []

    if len(res2) != 0:
        for rec in res2:
            if "|" in rec[0]:
                res2_new.extend(rec[0].split("|"))

            else:
                res2_new.append(rec[0])

    res1.extend(res2_new)

    return res1


async def get_tag_owner(guild_id: int, name: str):
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
                "select USER_ID from Tags where GUILD_ID = %s and NAME = %s;",
                (guild_id, name),
            )

            res = await cur.fetchone()

    pool.close()
    await pool.wait_closed()

    return None if not res else res[0]


async def update_tag_owner(guild_id: int, user_id: int, name: str):
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
                "update Tags set USER_ID = %s where GUILD_ID = %s and NAME = %s;",
                (user_id, guild_id, name),
            )

    pool.close()
    await pool.wait_closed()


async def get_tag_aliases(guild_id: int, name: str):
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
                "select ALIASES from Tags where GUILD_ID = %s and NAME = %s;",
                (guild_id, name),
            )

            res = await cur.fetchone()

    pool.close()
    await pool.wait_closed()

    return [] if not res[0] else res[0].split("|")


async def is_alias(guild_id: int, alias: str):
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
                "select ALIASES from Tags where GUILD_ID = %s;", (guild_id,)
            )

            res = await cur.fetchall()

    pool.close()
    await pool.wait_closed()

    for _item in res:
        item = _item[0]

        if not item:
            continue

        if "|" not in item:
            if alias == item:
                return True

        else:
            items = item.split("|")

            for __item in items:
                if alias == __item:
                    return True

    return False


async def update_tag_aliases(guild_id: int, name: str, alias: str):
    pool = await aiomysql.create_pool(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password,
        db=db_name,
        autocommit=True,
        loop=asyncio.get_event_loop(),
    )

    aliases = await get_tag_aliases(guild_id, name)
    aliases.append(alias)
    aliases = "|".join(aliases)

    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "update Tags set ALIASES = %s where GUILD_ID = %s and NAME = %s;",
                (aliases, guild_id, name),
            )

    pool.close()
    await pool.wait_closed()
