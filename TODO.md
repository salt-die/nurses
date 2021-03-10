TODO
====
* DESTROY DEPENDENCY ON CURSES.
    This library is mostly intended for windows use for now, and curses support on windows is not the most consistent.
    There's a few options here:  Asciimatics has its own `Screen` class we can piggy-back off of, alternatively we could implement our own using `pywin32`.
    There's the ambitious `notcurses` library that has incomplete python bindings and it's not yet supported on windows, though I expect this will change
    soon™.  In any case, color management is a ridiculous pain with curses, where palettes are limited to 256 colors and re-initing colors on windows-curses
    doesn't always seem to work.

* Docs

Notes
-----
* Colors
    Resizing windows terminal seems to do something strange to colors. One can see an example of this when resizing the terminal for async_test.py:  The borders of the walking widgets turn blue.
