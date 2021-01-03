TODO
----
* Widgets
    * Textpad -- difficulty will be implementing a non-blocking text pad

* Mix-Ins for Widgets:
    * Selectable (Tab bring-to-front selectable widgets)
    * Scrollable (Scroll contents up or down with arrow-keys)
    * Movable
    * Resizable

* Layouts
    * Grid - a `n * m` layout of widgets
    * Stack  - a row or column of widgets
    * Scrolling - a row or column of widgets that extends off-screen and can be scrolled


Notes
-----
Should Layouts inherit from Widget? Or should both Layout and Widget inherit from a common base?  This could allow to ScreenManager to be agnostic to
dispatching to or drawing either and probably is not much effort to implement.

`load_string` should probably return the outer-most Layout.
