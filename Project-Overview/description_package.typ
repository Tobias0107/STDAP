= Description package functionality
== Use
/*
  The use of this package should become more elaborated. But this would be the big picture
*/
+ Specify path to CBS data
+ Import data (button that imports data from path to CBS)
+ Choose city to perform simulation on
 - From list of available cities
  - (Extract list of available cities from CBS)
+ Choose from available simulations:
 - Run simulation for a single f
  - Allows more detailed information, like map-image of transformation
 - Run simulation for a range of f
  - Stepsize should be set
+ Choose simulation specific options
 - What to visualize (might mean less time required)
 - How to visualize
 - Where to store results (path)
+ Run simulation (button)
 - Show progress bar (as simulation can take a long time)
 - Show succeeded / failed
 - Allow for a dropdown that shows debug/detailed information to program state

Some of the options might be included in the python package as arguments /
different functions/modules. 

== Package structure 
/*
  I did some basic / quick reading into creating packages in python.
  As our package would be super simpel I sugest creating it manually.
  https://www.freecodecamp.org/news/how-to-create-and-upload-your-first-python-package-to-pypi
  https://www.freecodecamp.org/news/how-to-build-and-publish-python-packages-with-poetry/

*/
#image("Typst_assets/folder_tree.png")
=== src
This should contain the functions and gui.py. This are the two modules we would want to offer. The gui should contain a single function called run(csv, geodata). This would spawn a gui. The functions module would contain all seperate functions used for simulation. This would allow for automised use of the gui. Both modules only exist to call the functions in scripts that we think the users of the package should be allowed to use.

=== tests
This should contain unit tests for every single function. This is simply good practice.

=== scripts
This should contain the true code of the package. This would be all non-public code. Thus the code that should not be available to users of the package. Even the code that should be visable for the users should be defined here. The idea is that the src will reference the correct functions from here, effectively making them public.


