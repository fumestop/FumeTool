from __future__ import annotations

from datetime import datetime

import aiomysql


async def guild_exists(pool: aiomysql.Pool, guild_id: int):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "select GUILD_ID from guilds where GUILD_ID = %s;", (guild_id,)
            )

            res = await cur.fetchone()

    if not res:
        return False

    return True


async def add_guild(pool: aiomysql.Pool, guild_id: int):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "insert into guilds (GUILD_ID) values (%s);", (guild_id,)
            )


async def is_premium_user(pool: aiomysql.Pool, user_id: int):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "select PREMIUM from users where USER_ID = %s;", (user_id,)
            )

            res = await cur.fetchone()

    if not res or not res[0]:
        return False

    return True


async def is_premium_guild(pool: aiomysql.Pool, user_id: int):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "select PREMIUM from guilds where GUILD_ID = %s;", (user_id,)
            )

            res = await cur.fetchone()

    if not res or not res[0]:
        return False

    return True


async def is_blacklisted_user(pool: aiomysql.Pool, user_id: int):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "select USER_ID from user_blacklist where USER_ID = %s;", (user_id,)
            )

            res = await cur.fetchone()

    if not res or not res[0]:
        return False

    return True


async def is_blacklisted_guild(pool: aiomysql.Pool, guild_id: int):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "select GUILD_ID from guild_blacklist where GUILD_ID = %s;",
                (guild_id,),
            )

            res = await cur.fetchone()

    if not res or not res[0]:
        return False

    return True


async def count_tags(pool: aiomysql.Pool, guild_id: int, user_id: int = None):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            if not user_id:
                await cur.execute(
                    "select count(*) from Tags where GUILD_ID = %s;", (guild_id,)
                )

            else:
                await cur.execute(
                    "select count(*) from Tags where GUILD_ID = %s and USER_ID = %s;",
                    (guild_id, user_id),
                )

            res = await cur.fetchone()

    return res[0]


async def create_tag(
    pool: aiomysql.Pool, guild_id: int, user_id: int, name: str, content: str
):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "insert into Tags (GUILD_ID, USER_ID, NAME, CREATED_AT, CONTENT) "
                "values(%s, %s, %s, %s, %s);",
                (guild_id, user_id, name, datetime.now(), content),
            )


async def get_tag_from_alias(pool: aiomysql.Pool, guild_id: int, alias: str):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "select * from Tags where GUILD_ID = %s and ALIASES like %s;",
                (guild_id, f"%{alias}%"),
            )

            res = await cur.fetchall()

    if len(res) == 0:
        return []

    for _record in res:
        for _alias in _record[5].split(","):
            if _alias == alias:
                return _record


async def get_tag(
    pool: aiomysql.Pool, guild_id: int, name: str, check_alias: bool = True
):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "select * from Tags where GUILD_ID = %s and NAME = %s;",
                (guild_id, name),
            )

            res = await cur.fetchone()

    res = (
        res or await get_tag_from_alias(pool, guild_id=guild_id, alias=name)
        if check_alias
        else res
    )

    return (
        {
            "guild_id": res[0],
            "user_id": res[1],
            "name": res[2],
            "created_at": res[3],
            "content": res[4],
            "aliases": res[5],
        }
        if res
        else None
    )


async def edit_tag(pool: aiomysql.Pool, guild_id: int, name: str, content: str):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "update Tags set CONTENT = %s where GUILD_ID = %s and NAME = %s;",
                (content, guild_id, name),
            )


async def delete_tag(pool: aiomysql.Pool, guild_id: int, name: str = None):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "delete from Tags where GUILD_ID = %s and NAME = %s;",
                (guild_id, name),
            )


async def purge_tags(pool: aiomysql.Pool, guild_id: int, user_id: int):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "delete from Tags where GUILD_ID = %s and USER_ID = %s;",
                (guild_id, user_id),
            )


async def get_all_tags(pool: aiomysql.Pool, guild_id: int, user_id: int = None):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            if not user_id:
                await cur.execute(
                    "select NAME, USER_ID from Tags where GUILD_ID = %s;",
                    (guild_id,),
                )

            else:
                await cur.execute(
                    "select NAME, USER_ID from Tags where GUILD_ID = %s and USER_ID = %s;",
                    (guild_id, user_id),
                )

            res = await cur.fetchall()

    _res = list(res)
    res = list()

    if len(_res) != 0:
        for _index, _record in enumerate(_res, 1):
            res.append({"index": _index, "name": _record[0], "user_id": _record[1]})

        return res

    else:
        return []


async def search_tags(pool: aiomysql.Pool, guild_id: int, query: str):
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


async def get_tag_owner(pool: aiomysql.Pool, guild_id: int, name: str):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "select USER_ID from Tags where GUILD_ID = %s and NAME = %s;",
                (guild_id, name),
            )

            res = await cur.fetchone()

    return None if not res else res[0]


async def update_tag_owner(
    pool: aiomysql.Pool, guild_id: int, user_id: int, name: str
):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "update Tags set USER_ID = %s where GUILD_ID = %s and NAME = %s;",
                (user_id, guild_id, name),
            )


async def get_tag_aliases(pool: aiomysql.Pool, guild_id: int, name: str):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "select ALIASES from Tags where GUILD_ID = %s and NAME = %s;",
                (guild_id, name),
            )

            res = await cur.fetchone()

    return [] if not res[0] else res[0].split("|")


async def is_alias(pool: aiomysql.Pool, guild_id: int, alias: str):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "select ALIASES from Tags where GUILD_ID = %s;", (guild_id,)
            )

            res = await cur.fetchall()

    for _item in res:
        item = _item[0]

        if not item:
            continue

        if "," not in item:
            if alias == item:
                return True

        else:
            items = item.split(",")

            for __item in items:
                if alias == __item:
                    return True

    return False


async def update_tag_aliases(
    pool: aiomysql.Pool, guild_id: int, name: str, alias: str
):
    aliases = await get_tag_aliases(pool, guild_id, name)
    aliases.append(alias)
    aliases = ",".join(aliases)

    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "update Tags set ALIASES = %s where GUILD_ID = %s and NAME = %s;",
                (aliases, guild_id, name),
            )
