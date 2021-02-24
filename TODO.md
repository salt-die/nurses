TODO
====
* DESTROY DEPENDENCY ON CURSES.
    This library is mostly intended for windows use for now, and curses support on windows is not the most consistent.
    There's a few options here:  Asciimatics has its own `Screen` class we can piggy-back off of, alternatively we could implement our own using `pywin32`.
    There's the ambitious `notcurses` library that has incomplete python bindings and it's not yet supported on windows, though I expect this will change
    soon™.  In any case, color management is a ridiculous pain with curses, where palettes are limited to 256 colors and re-initing colors on windows-curses
    doesn't always seem to work.

* Widgets
    * File Explorer

* Resizing Widget doesn't correct borders (ArrayWin does correct)

* Docs

Notes
-----
* Window sizes
    Windows in widgets are wider than they need to be by 1.  This is because writing to the lower-right corner of a curses window produces an error since the cursor
    can't advance.  There may be a more elegant solution...

* Colors
    Resizing windows terminal seems to do something strange to colors.  I can't quite nail it down - the behavior doesn't seem consistent for all colors.
    One can see an example of this when resizing the terminal for async_test.py:  The borders of the walking widgets turn blue.

* Off-by-1
    Stacks and Grids might not use entire screen space due to rounding from size-hints.  On the one hand we could add extra rows/cols to child widgets, but then
    widgets that are expected to be same size could be differently sized.  On the other hand we could do nothing and widgets with the same size hints will be the same size, but there may be a row or two of screen real-estate that isn't used.
