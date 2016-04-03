aionotify
=========

.. image:: https://secure.travis-ci.org/rbarrois/aionotify.png?branch=master
    :target: http://travis-ci.org/rbarrois/aionotify/

.. image:: https://img.shields.io/pypi/v/aionotify.svg
    :target: http://aionotify.readthedocs.org/en/latest/changelog.html
    :alt: Latest Version

.. image:: https://img.shields.io/pypi/pyversions/aionotify.svg
    :target: https://pypi.python.org/pypi/aionotify/
    :alt: Supported Python versions

.. image:: https://img.shields.io/pypi/wheel/aionotify.svg
    :target: https://pypi.python.org/pypi/aionotify/
    :alt: Wheel status

.. image:: https://img.shields.io/pypi/l/aionotify.svg
    :target: https://pypi.python.org/pypi/aionotify/
    :alt: License


``aionotify`` is a simple, asyncio-based inotify library.


Its use is quite simple:

.. code-block:: python

    import asyncio
    import aionotify

    # Setup the watcher
    watcher = aionotify.Watcher()
    watcher.watch(alias='logs', path='/var/log', flags=aionotify.Flags.MODIFY)

    # Prepare the loop
    loop = asyncio.get_eventloop()

    async def work():
        await watcher.setup(loop)
        for _i in range(10):
            # Pick the 10 first events
            event = await watcher.get_event()
            print(event)
        watcher.close()

    loop.run_until_completed(work())
    loop.stop()
    loop.close()
