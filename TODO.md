TODO
====
* Widgets
    * Dispatch resize events; update widget geometries for any widgets using relative position / relative size.  If a size or position attribute is updated,
      set the corresponding hint to None?  I'm not sure how I want to approach this yet.
    * Textpad
    * Graph

* Mix-Ins for Widgets:
    * Scrollable (Scroll contents up or down with arrow-keys)
    * Resizable

* Layouts
    * call .update when `width` or `height` changes.
    * Grid - a `n * m` layout of widgets
    * Stack  - a row or column of widgets
    * Scrolling - a row or column of widgets that extends off-screen and can be scrolled

* Docs

Notes
-----
I hate the name ArrayWin.
