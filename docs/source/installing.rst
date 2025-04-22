Installing the Application
=============================

There are two methods of installing the application:

1. Installing the Python application and supporting modules
2. Installing with an .exe file

Users with Python already installed on their system, running pip with the virtual environment and requirement file will ensure all programs are installed and of the correct version. The .exe file should be used by those interested only in the functional front end of PyGTAPAgg, without any of the Python source code or development capabilities. Given the widespread use of Python (it is installed by default on many Apple and Linux machines), most users will want to consider this as a first opportunity to start their learning path with Python by installing the full version.

System Minimums
---------------

Most Windows computers (laptop or desktop) running a version of Windows 10 or higher should be capable of running PyGTAPAgg. The installation of Python and the required modules will require close to 1 GB of space for the complete installation. Note, an exe file may be downloaded, which includes only the required bytecode and interpreter which requires 200 MB or less. However, the limited installation will not permit development.

+----------------+-------------+
| Program        | Size        |
+================+=============+
| Python 3.7     | ~600 MB     |
+----------------+-------------+
| PyQT           | 160 MB      |
+----------------+-------------+
| Numpy          | 61.5 MB     |
+----------------+-------------+
| HARPY          | 7.0 MB      |
+----------------+-------------+
| PIP            | 11.0 MB     |
+----------------+-------------+

System RAM of 4GB is required. 8 GB is recommended.

Installing as a Python Application
----------------------------------

The application can be run by typing::

    c:> python .\PyGTAPAgg.py

at the prompt in the directory in which you installed PyGTAPAgg. The file with that name must be present in the directory you type the name, PyGTAPAgg does not install itself in the system path at this time.

Installing with .exe file
-------------------------

A ".exe" file may be downloaded from the ImpactECON web site at (xxxxx). The exe file will load files required by python and those required by the PyGTAPApp. Users will not be able to see or change the source code with this approach.