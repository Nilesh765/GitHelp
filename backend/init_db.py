import asyncio
from app.core.database import engine
from app.common.base import Base
import app.modules.users.model

async def init_models():
    print("Connecting to the async database...")

    async with engine.begin() as conn:
        print("Dropping old synchronous tables...")

        await conn.run_sync(Base.metadata.drop_all)

        print("Building new async tables...")

        await conn.run_sync(Base.metadata.create_all)

    print("Success!, Your fully async, domain-driven database is alive")


if __name__ == "__main__":
    asyncio.run(init_models())