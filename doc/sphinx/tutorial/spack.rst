Tutorial Part 2: Using Spack Environments
==========================================

In this tutorial, you'll learn how to integrate Spack for dependency management. We'll extend the CMake workflow from Part 1 to use Spack environments, create a Spack package for the project, and add Boost as a dependency.

Prerequisites
-------------

- Completed :doc:`tutorial/cmake`
- Spack installed and available in your environment
- Your ``myapp`` project from Part 1

Adding Boost Dependency
-----------------------

First, let's modify our application to use Boost.

Update main.cpp
~~~~~~~~~~~~~~~

Edit ``main.cpp`` to use Boost:

.. code-block:: cpp

   #include <iostream>
   #include <boost/version.hpp>

   int main() {
       std::cout << "Hello, World!" << std::endl;
       std::cout << "Using Boost " 
                 << BOOST_VERSION / 100000 << "."
                 << BOOST_VERSION / 100 % 1000 << "."
                 << BOOST_VERSION % 100 << std::endl;
       return 0;
   }

Update CMakeLists.txt
~~~~~~~~~~~~~~~~~~~~~

Update ``CMakeLists.txt`` to find and link Boost:

.. code-block:: cmake

   cmake_minimum_required(VERSION 3.12)
   project(myapp VERSION 1.0.0 LANGUAGES CXX)

   find_package(Boost REQUIRED)

   add_executable(myapp main.cpp)
   target_link_libraries(myapp PRIVATE Boost::boost)

   enable_testing()
   add_test(NAME run_myapp COMMAND myapp)

Creating a Spack Package
------------------------

Now we'll create a Spack package for our project so Spack can manage it.

Create Spack Repository
~~~~~~~~~~~~~~~~~~~~~~~

Create a Spack repository directory in your project:

.. code-block:: console

   $ spack repo create . myapp

Create Package Recipe
~~~~~~~~~~~~~~~~~~~~~

Create ``spack_repo/packages/myapp/package.py``:

.. code-block:: console

   $ spack create -r spack_repo/myapp myapp

.. code-block:: python

   from spack_repo.builtin.build_systems.cmake import CMakePackage
   from spack.package import *
   
   class Myapp(CMakePackage):
       """A simple application demonstrating Kessel with Spack"""
   
       homepage = "https://example.com/myapp"
       git = "https://github.com/myapp/myapp.git"
   
       version("main", branch="main")
   
       depends_on("boost")

Your project structure should now look like:

.. code-block::

   myapp/
   ├── .kessel/
   │   └── workflows/
   │       └── default/
   │           └── workflow.py
   ├── spack_repo/
   │   └── myapp/
   │       ├── repo.yaml
   │       └── packages/
   │           └── myapp/
   │               └── package.py
   ├── CMakeLists.txt
   └── main.cpp

Updating the Workflow
---------------------

Now we'll update the Kessel workflow to use Spack.

Extend with BuildEnvironment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Edit ``.kessel/workflows/default/workflow.py``:

.. code-block:: python

   from kessel.workflows.spack import BuildEnvironment
   from kessel.workflows.cmake import CMake
   from kessel.workflows import *

   class Default(BuildEnvironment, CMake):
       steps = ["env", "configure", "build", "test"]
       
       spack_env = environment("myapp-dev")
       project_spec = environment("myapp@main")

This workflow:

- Inherits from both ``BuildEnvironment`` (for Spack) and ``CMake`` (for building)
- Adds an ``env`` step to set up the Spack environment
- Adds a ``configure`` step that installs dependencies and configures CMake
- Specifies the Spack environment name (``myapp-dev``)
- Specifies the project spec (``myapp@main``)

Running with Spack
------------------

First Run
~~~~~~~~~

Run the workflow with Spack:

.. code-block:: console

   $ kessel run

On the first run, Kessel will:

1. Create a new Spack environment named ``myapp-dev`` (if it doesn't exist)
2. Add ``myapp@main`` as a root spec to the environment
3. Register the ``myapp`` Spack repository in the environment
3. Install Boost and other dependencies
4. Configure the project with CMake
5. Build and test the application

Verifying the Build
~~~~~~~~~~~~~~~~~~~

Run the built executable:

.. code-block:: console

   $ ./build/myapp
   Hello, World!
   Using Boost 1.84.0

Subsequent Runs
~~~~~~~~~~~~~~~

On subsequent runs, Kessel will use the existing environment:

.. code-block:: console

   $ kessel run

This time, the environment already exists and dependencies are already installed, so the workflow runs much faster.

Working with the Spack Environment
----------------------------------

Modify Environment
~~~~~~~~~~~~~~~~~~

You can modify the environment and re-run:

.. code-block:: console

   $ spack add cmake@3.27
   $ kessel run

Using Different Environments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can specify a different environment at runtime:

.. code-block:: console

   $ kessel run -e myapp-test

This creates or uses an environment named ``myapp-test``.

Adding More Dependencies
~~~~~~~~~~~~~~~~~~~~~~~~

Update the Spack package to add more dependencies.

Edit ``spack_repo/packages/myapp/package.py``:

.. code-block:: python

   from spack.package import *

   class Myapp(CMakePackage):
       """A simple application demonstrating Kessel with Spack"""

       homepage = "https://example.com/myapp"
       git = "https://github.com/myapp/myapp.git"

       version("main", branch="main")

       depends_on("boost")
       
       # Add more dependencies
       variant("mpi", default=False, description="Enable MPI support")
       depends_on("mpi", when="+mpi")

       def cmake_args(self):
            args = [
               self.define_from_variant("ENABLE_MPI", "mpi")
            ]
            return args

Then rebuild:

.. code-block:: console

   $ kessel reset
   $ kessel run

Summary
-------

In this tutorial, you:

1. Extended your project to use Boost
2. Created a Spack package for your project
3. Updated the workflow to use ``BuildEnvironment`` and ``CMake``
4. Configured Spack environment name and project spec
5. Ran the workflow with automatic Spack environment creation
6. Learned to work with Spack environments

Next Steps
----------

In :doc:`tutorial/deployment`, you'll learn how to create a Spack deployment that can be used across systems, with pre-built environments and offline build capability.