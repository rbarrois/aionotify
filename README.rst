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

    # Similar to:
    watcher.watch('/var/log', flags=aionotify.Flags.MODIFY, alias='/var/log')


A watch can be removed by using its alias:

.. code-block:: python

    watcher = aionotify.Watcher()
    watcher.watch('/var/log', flags=aionotify.Flags.MODIFY)

    watcher.unwatch('/var/log')
