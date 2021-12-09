aionotify
=========

.. image:: https://secure.travis-ci.org/rbarrois/aionotify.png?branch=master
    :target: http://travis-ci.org/rbarrois/aionotify/

.. image:: https://img.shields.io/pypi/v/aionotify.svg
    :target: https://pypi.python.org/pypi/aionotify/
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

This is a fork of aionotify. It includes long running PRs and improvments,
such as an async iterator. It should be fully backward-compatible with
aionotify, but we now support only python >= 3.7 (while aionotify supported
only 3.5 and 3.6).

``aionotify`` is a simple, asyncio-based inotify library.

Its use is quite simple:

.. code-block:: python

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

If one needs more control over the watcher (e.g. to add and remove watches
dynamically), it can be configured outside of the context manager

    import asyncio
    import aionotify

    watcher = aionotify.Watcher()

    async def work():
        watcher.watch(alias='logs', path='/tmp', flags=aionotify.Flags.MODIFY)
        # Run the main loop
        async for event in watcher:
            print(event)
            break

    asyncio.run(work())


Links
-----

* Code at https://github.com/rbarrois/aionotify
* Package at https://pypi.python.org/pypi/aionotify/
* Continuous integration at https://travis-ci.org/rbarrois/aionotify/


Events
------

An event is a simple object with a few attributes:

* ``name``: the path of the modified file
* ``flags``: the modification flag; use ``aionotify.Flags.parse()`` to retrieve a list of individual values.
* ``alias``: the alias of the watch triggering the event
* ``cookie``: for renames, this integer value links the "renamed from" and "renamed to" events.


Watches
-------

``aionotify`` uses a system of "watches", similar to inotify.

A watch may have an alias; by default, it uses the path name:

.. code-block:: python

    watcher = aionotify.Watcher()
    watcher.watch('/var/log', flags=aionotify.Flags.MODIFY)

    # Equivalent to:
    watcher.watch('/var/log', flags=aionotify.Flags.MODIFY, alias='/var/log')


A watch can be removed by using its alias:

.. code-block:: python

    watcher = aionotify.Watcher()
    watcher.watch('/var/log', flags=aionotify.Flags.MODIFY)

    watcher.unwatch('/var/log')
