== Package structure 
/*
  I did some basic / quick reading into creating packages in python.
  As our package would be super simpel I sugest creating it manually.
  https://www.freecodecamp.org/news/how-to-create-and-upload-your-first-python-package-to-pypi
  https://www.freecodecamp.org/news/how-to-build-and-publish-python-packages-with-poetry/

*/
```
The_git_page/
│
├── pyproject.toml
├── README.md
├── LICENSE
├── .gitignore
│
├── src/
│   └── Package_name/
│       ├── __init__.py
│       │
│       ├── core/
│       │   ├── __init__.py
│       │   ├── main_class.py
│       │   ├── method1.py
│       │   ├── method2.py
│       │
│       ├── utils/
│       │   ├── __init__.py
│       │   ├── helper1.py
│       │   ├── helper2.py
│       │
│       ├── config/
│       │   ├── __init__.py
│       │   ├── settings.py
│       │
│       ├── gui/
│       │   ├── __init__.py
│       │   ├── name.py
│       │
│       └── exceptions.py
│
├── tests/
│   ├── test_main_class.py
│   ├── test_utils.py
│
└── examples/
    ├── basic_usage.py
    └── gui_demo.py
```
== Comments:
=== Generated structure
This was suggested by chat-gpt, but I did read into the basics of python packages, and it does seem like a good structure. I suggest making the folder structure at least, but most files and folders can start of empty (toml, readme, LICENSE, gui, tests, examples, ...).

=== Core and main class
Main_class would be the class that users will import when using the package. The main class has methods for every functionality provided by the package. It's methods are actually written in separate files, to support maintainability. 

=== Gui
The gui should use the main_class to implement a gui for that main_class. This should be build only when the main class is finished. Python packages exist to build gui dashboards (Tkinder)

=== config
settings.py should contain all the general settings that are not important enough to be given as parameters. Think of default paths, the names of the csv headers (for if CBS decides to change this), ...

=== utils
The core folder is reserved for the main class and its methods only. This means that if a method becomes so big you want to define helper functions in another file, you should define those helper functions in utils. It als allows helper functions that could be used in multiple methods.

=== tests
It is always good practice to test every single function to make. All methods / helper functions that can be tested individually should be tested individually.

=== examples
This has two functions.
1. It will contribute to the documentation. (Documentation will contain screenshots/references to these examples)
2. It provides better communication to each other.

== UML main class


