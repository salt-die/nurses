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
    * Grid - a n x m layout of widgets
    * Stack  - a row or column of widgets
    * Scrolling

* Colors
    * Support for redefining a color pair?  I'm unsure if I even want this feature and would require another refactor of colors.py.


Notes
-----
Should Layouts inherit from Widget? Or should both Layout and Widget inherit from a common base?  Doing either could allow for more flexibility positioning and dispatching to widgets.  And allow widgets to contain widgets.