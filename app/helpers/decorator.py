import asyncio
from functools import wraps, partial


def run_async(func):
    @wraps(func)
    async def run(*args, loop=None, executor=None, **kwargs):
        if loop is None:
            loop = asyncio.get_event_loop()
        # OR use partial
        pfunc = partial(func, *args, **kwargs)
        result = await loop.run_in_executor(executor, pfunc)

        return result

    return run
