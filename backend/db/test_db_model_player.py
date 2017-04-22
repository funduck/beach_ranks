from db import DB
from db_model_player import Player
import pytest
import pytest_asyncio

@pytest.mark.asyncio
async def test_save():
    db = DB()
    await db.connect()
    p = Player()
    p.set_db(db)
    res = await p.save()
    print(res)