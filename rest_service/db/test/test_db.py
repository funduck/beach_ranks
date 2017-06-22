import pytest

from ..db import DB


@pytest.mark.asyncio
async def test_init():
    db = DB()
    await db.connect()


@pytest.mark.asyncio
async def test_select():
    db = DB()
    await db.connect()
    res = await db.execute(['select 1 as result', []])
    assert res[0][0] == 1


@pytest.mark.asyncio
async def test_call_procedure():
    db = DB()
    await db.connect()
    res = await db.execute(['select * from beach_ranks.test();', []])
    assert res[0][0] == 1
