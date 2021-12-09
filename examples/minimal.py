import asyncio
import aionotify


async def work():
    # Setup the watcher
    async with aionotify.Watcher() as watcher:
        watcher.watch(alias='logs', path='/tmp', flags=aionotify.Flags.MODIFY)
        # Run the main loop
        async for event in watcher:
            print(event)
            # We have to break at some point. Real code would cancel
            # the task, or break on a specific event.
            break

asyncio.run(work())
