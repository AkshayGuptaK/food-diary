# Run the build process by running the command 'python setup.py build'
#
# If everything works well you should find a subdirectory in the build
# subdirectory that contains the files needed to run the application

import sys
import os.path
from cx_Freeze import setup, Executable

excludes = ['doctest', 'pdb', 'unittest', 'difflib', 'inspect', 
           'email', 'html', 'http', 'xml', 'decimal']
           # Unnecessary packages excluded to reduce size.

python_dir = os.path.dirname(os.path.dirname(os.__file__))
             #Directory in which python is installed

os.environ['TCL_LIBRARY'] = os.path.join(python_dir, 'tcl', 'tcl8.6')
os.environ['TK_LIBRARY'] = os.path.join(python_dir, 'tcl', 'tk8.6')           
#Set paths for tcl/tk as these are bugged in current release of cx_freeze
           
build_exe_options = {'include_files': [os.path.join(python_dir, 'DLLs', 'tk86t.dll'), 
                                       os.path.join(python_dir, 'DLLs', 'tcl86t.dll')],
                     'optimize': 1, 
                     'excludes': excludes}

base = None
if sys.platform == 'win32':
    base = 'Win32GUI'

executables = [
    Executable('FoodDiary.pyw', base=base),
    Executable('ResetDatabase.py', base=base)]

setup(name='Food Diary',
      version='0.35',
      description= "A diet logging and tracking application",
      options = {"build_exe": build_exe_options},
      executables=executables)