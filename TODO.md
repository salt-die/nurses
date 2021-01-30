TODO
====
* Widgets
    * Textpad
    * Graph
    * File Explorer

* Docs

Notes
-----
* Colors
    Resizing windows terminal seems to do something strange to colors.  I can't quite nail it down - the behavior doesn't seem consistent for all colors.
    One can see an example of this when resizing the terminal for async_test.py:  The borders of the walking widgets turn blue.

* Off-by-1
    Stacks and Grids might not use entire screen space due to rounding from size-hints.  On the one hand we could add extra rows/cols to child widgets, but then
    widgets that are expected to be same size could be differently sized.  On the other hand we could do nothing and widgets with the same size hints will be the same size, but there may be a row or two of screen real-estate that isn't used.

* Repeating keys and Getching
    Often nurses can't getch fast enough if a key is being held down, so there're still key presses dispatched after a key is released.  We might flush input after
    each getch.