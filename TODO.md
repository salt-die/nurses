TODO
====
* Widgets
    * Textpad

* Mix-Ins for Widgets:
    * Scrollable (Scroll contents up or down with arrow-keys)
    * Resizable

* Layouts
    * call .update when `width` or `height` changes.
    * Grid - a `n * m` layout of widgets
    * Stack  - a row or column of widgets
    * Scrolling - a row or column of widgets that extends off-screen and can be scrolled

* Color Manager
    * utility function to create gradients by providing just a start and end color (and number of colors)

Notes
-----
Possible bug if one cancels and immediately calls a task.  Task could be on queue multiple times.  This needs to be rectified asap.

I hate the name ArrayWin.
