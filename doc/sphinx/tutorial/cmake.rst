Tutorial Part 1: Basic CMake Project with Kessel
=================================================

In this tutorial, you'll learn how to add Kessel to a simple CMake project. We'll start with a basic C++ project, add Kessel workflows, and see how to run build and test steps.

Prerequisites
-------------

- Kessel installed and available in your PATH
- CMake 3.12 or higher
- A C++ compiler (gcc, clang, etc.)

Creating a Simple CMake Project
--------------------------------

First, let's create a basic C++ project.

Project Structure
~~~~~~~~~~~~~~~~~

Create a new directory for your project:

.. code-block:: console

   $ mkdir myapp
   $ cd myapp

Create the following files:

**main.cpp**:

.. code-block:: cpp

   #include <iostream>

   int main() {
       std::cout << "Hello, World!" << std::endl;
       return 0;
   }

**CMakeLists.txt**:

.. code-block:: cmake

   cmake_minimum_required(VERSION 3.12)
   project(myapp VERSION 1.0.0 LANGUAGES CXX)

   add_executable(myapp main.cpp)

   enable_testing()
   add_test(NAME run_myapp COMMAND myapp)

Your project structure should now look like:

.. code-block::

   myapp/
   ├── CMakeLists.txt
   └── main.cpp

Adding Kessel to the Project
-----------------------------

Now let's add Kessel to automate the build and test workflow.

Initialize Kessel
~~~~~~~~~~~~~~~~~

From the project root directory:

.. code-block:: console

   $ kessel init --template minimal-cmake-project
   Creating kessel configuration based on minimal-cmake-project template

This creates a ``.kessel`` directory with a default workflow:

.. code-block::

   myapp/
   ├── .kessel/
   │   └── workflows/
   │       └── default/
   │           └── workflow.py
   ├── CMakeLists.txt
   └── main.cpp

Examining the Workflow
~~~~~~~~~~~~~~~~~~~~~~

Let's look at the generated workflow:

.. code-block:: console

   $ cat .kessel/workflows/default/workflow.py

The workflow should look like:

.. code-block:: python

   from kessel.workflows import *

   class Default(Workflow):
       steps = ["configure", "build"]
   
       @collapsed
       def configure(self, args):
           """Configure"""
           self.exec("rm -rf build")
           self.exec("cmake -B build -S . -DCMAKE_BUILD_TYPE=Debug")
   
       def build(self, args):
           """Build"""
           self.exec("cmake --build build --parallel")

This simple workflow defines build steps using the ``exec`` method to run shell commands directly.

Running the Workflow
--------------------

Complete Build and Test
~~~~~~~~~~~~~~~~~~~~~~~

Run the entire workflow:

.. code-block:: console

   $ kessel run

You'll see output showing each step:

.. code-block:: console

   Configure
   
          ●▭▭▭▭▭▭▭▭○
   
      Configure  Build
   
   -- The CXX compiler identification is AppleClang 17.0.0.17000603
   -- Detecting CXX compiler ABI info
   -- Detecting CXX compiler ABI info - done
   -- Check for working CXX compiler: /usr/bin/c++ - skipped
   -- Detecting CXX compile features
   -- Detecting CXX compile features - done
   -- Configuring done (5.3s)
   -- Generating done (0.0s)
   -- Build files have been written to: /Users/User/kessel_test/myapp/build
   
   Build
   
          ●▬▬▬▬▬▬▬▬●
   
      Configure  Build
   
   [ 50%] Building CXX object CMakeFiles/myapp.dir/main.cpp.o
   [100%] Linking CXX executable myapp
   [100%] Built target myapp

Running Individual Steps
~~~~~~~~~~~~~~~~~~~~~~~~

You can run individual steps:

.. code-block:: console

   $ kessel reset  # Reset to start over
   $ kessel step build

This runs only the build step. The workflow progress shows:

.. code-block:: console

          ○▭▭▭▭▭▭▭▭○

      Configure  Build


Continue with the test step:

.. code-block:: console

   $ kessel step configure

Now the progress shows:

.. code-block:: console

       ●▭▭▭▭▭▭▭▭○

   Configure  Build


Running Until a Specific Step
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can run the workflow until a specific step:

.. code-block:: console

   $ kessel reset
   $ kessel run --until configure

This runs the configure step, but skips build.

Checking Workflow Status
~~~~~~~~~~~~~~~~~~~~~~~~

At any time, check the workflow status:

.. code-block:: console

   $ kessel workflow status

This shows which steps have been completed.

Debugging with Shell Debug
~~~~~~~~~~~~~~~~~~~~~~~~~~

To see what shell commands Kessel executes without actually running them:

.. code-block:: console

   $ kessel --shell-debug run

This outputs all the shell commands that would be executed, useful for understanding what Kessel does or debugging issues.

Customizing the Workflow
------------------------

You can customize the workflow to change build behavior. Let's progressively add more features.

Editing the Workflow
~~~~~~~~~~~~~~~~~~~~

You can edit the workflow file directly, or use the convenient command:

.. code-block:: console

   $ kessel workflow edit

This opens the workflow in your default editor (``$EDITOR``).

Custom Build Directory
~~~~~~~~~~~~~~~~~~~~~~

First, let's make the build directory configurable. Edit ``.kessel/workflows/default/workflow.py`` (or run ``kessel workflow edit``):

.. code-block:: python

   from kessel.workflows import *

   class Default(Workflow):
       steps = ["configure", "build"]
       
       build_dir = environment("build-release")
       
       @collapsed
       def configure(self, args):
           """Configure"""
           self.exec(f"rm -rf {self.build_dir}")
           self.exec(f"cmake -B {self.build_dir} -S . -DCMAKE_BUILD_TYPE=Debug")
       
       def build(self, args):
           """Build"""
           self.exec(f"cmake --build {self.build_dir} --parallel")

Now running ``kessel run`` will use ``build-release`` instead of ``build``.

Adding Build Type
~~~~~~~~~~~~~~~~~

Now let's also make the build type configurable:

.. code-block:: python

   from kessel.workflows import *

   class Default(Workflow):
       steps = ["configure", "build"]
       
       build_dir = environment("build-release")
       build_type = environment("Release")
       
       @collapsed
       def configure(self, args):
           """Configure"""
           self.exec(f"rm -rf {self.build_dir}")
           self.exec(f"cmake -B {self.build_dir} -S . -DCMAKE_BUILD_TYPE={self.build_type}")
       
       def build(self, args):
           """Build"""
           self.exec(f"cmake --build {self.build_dir} --parallel")

Now the workflow uses Release builds by default.

Command-Line Arguments
~~~~~~~~~~~~~~~~~~~~~~

Finally, let's add command-line arguments so users can override the build type:

.. code-block:: python

   from kessel.workflows import *

   class Default(Workflow):
       steps = ["configure", "build"]
       
       build_dir = environment("build")
       build_type = environment("Release")
       
       def configure_args(self, parser):
           parser.add_argument(
               "-B", "--build-dir",
               default=self.build_dir
           )
           parser.add_argument(
               "--build-type",
               default=self.build_type,
               choices=["Debug", "Release", "RelWithDebInfo"]
           )
       
       @collapsed
       def configure(self, args):
           """Configure"""
           self.exec(f"rm -rf {self.build_dir}")
           self.exec(f"cmake -B {self.build_dir} -S . -DCMAKE_BUILD_TYPE={args.build_type}")
       
       def build(self, args):
           """Build"""
           self.exec(f"cmake --build {self.build_dir} --parallel")

Now you can override the build type at runtime:

.. code-block:: console

   $ kessel run -b build-debug --build-type Debug

Summary
-------

In this tutorial, you:

1. Created a simple CMake project with an executable and test
2. Added Kessel using ``kessel init --template minimal-cmake-project``
3. Ran the complete workflow with ``kessel run``
4. Learned to run individual steps with ``kessel step <name>``
5. Customized the workflow with environment variables and CMake arguments

Next Steps
----------

In :doc:`spack`, you'll learn how to integrate Spack for dependency management, allowing you to use external libraries like Boost in your project.