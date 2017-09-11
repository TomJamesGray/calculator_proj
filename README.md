# Calculator
A calculator written in python and kivy with a standard calculation mode and a graphing mode using reverse polish notation
and the shunting yard algorithm. Currently all the standard operators such as +,-,/,* (including unary - and +) and ^
are implemented as well as sin,cos and tan (in radians).

Also in the graphing mode there is support for animation by adding a variable and setting a maximum and minimum
then pressing the "play" button.

### Known Issues:
* In graphing mode equations like `(x+3)(x-2)` do not work as a * must be put in between them, similarly stuff
like 3x isn't handled as expected so a * must be put in making it `3*x`

### Todo:
* Add ability to remove lines in graphing mode
* Add handling for stuff like `3x`, ie remove need to write `3*x`
* Add automatic changing of the grid line frequency and labels on zoom in/out
