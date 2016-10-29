# Calculator
A simple graphical calculator in Python with a graphing mode

### Known Issues:
* In graphing mode equations like `(x+3)(x-2)` do not work as a * must be put in between them
* Also equations similar to that above plot with the linear plot interval, this is because I've tried to ^^^badly
detect whether a equation is linear or not, and the equation above would come out as being linear due to the absence
of a power sign or a "special" function
* Nested special functions such as sin do not perform as expected

### Todo:
* Improve antialiasting of lines in graphing mode
* Improve styling overall
