Quickstart
==========

This guide will help you get started with Kessel quickly, from installation to running your first workflow.

Installation
------------

Kessel can be installed directly from the repository:

.. code-block:: console

   $ git clone <repository-url>
   $ cd kessel
   $ source share/kessel/setup-env.sh

This adds Kessel to your PATH and sets up the necessary environment variables.

Verify the installation:

.. code-block:: console

   $ kessel --version

To make Kessel available in future shell sessions, add the source command to your shell configuration file (e.g., ``.bashrc`` or ``.zshrc``):

.. code-block:: console

   $ echo "source /path/to/kessel/share/kessel/setup-env.sh" >> ~/.bashrc

Prerequisites
-------------

- Python 3.6 or higher
- Git

Initializing a Project
----------------------

Kessel provides several project templates to help you get started. Navigate to your project directory and initialize it with:

.. code-block:: console

   $ cd /path/to/your/project
   $ kessel init

By default, this creates a ``.kessel`` directory with the ``spack-project`` template. To use a different template:

.. code-block:: console

   $ kessel init --template minimal-cmake-project

Available templates:

- ``spack-project``: For projects using Spack for dependency management
- ``spack-deployment``: For creating Spack deployment environments
- ``minimal-cmake-project``: For simple CMake-based projects

Project Structure
-----------------

After initialization, your project will contain:

.. code-block::

   your-project/
   ├── .kessel/
   │   └── workflows/
   │       └── default/
   │           └── workflow.py
   └── (your project files)

The ``.kessel/workflows/`` directory contains workflow definitions. Each workflow is a subdirectory with a ``workflow.py`` file that defines the steps.

Running Your First Workflow
----------------------------

Once initialized, you can run the default workflow:

.. code-block:: console

   $ kessel run

This executes all steps in the active workflow in sequence. Kessel will display a progress indicator showing which steps have been completed.

Running Individual Steps
------------------------

You can execute individual workflow steps using the ``step`` command:

.. code-block:: console

   $ kessel step env
   $ kessel step configure
   $ kessel step build
   $ kessel step test

To see available steps for the current workflow:

.. code-block:: console

   $ kessel workflow status

Working with Multiple Workflows
--------------------------------

List all available workflows:

.. code-block:: console

   $ kessel list

Activate a different workflow:

.. code-block:: console

   $ kessel activate my-workflow

The active workflow is highlighted in the workflow list and persisted across sessions.

Example: CMake Project Workflow
--------------------------------

For a typical CMake project, the workflow steps are:

1. **env**: Set up the build environment (activate Spack environment if using Spack)
2. **configure**: Run CMake configuration
3. **build**: Compile the project
4. **test**: Run tests with CTest
5. **install**: Install the built artifacts

Run the complete workflow:

.. code-block:: console

   $ kessel run

Or run steps individually:

.. code-block:: console

   $ kessel step env
   $ kessel step configure
   $ kessel step build

You can pass arguments to steps. For example, to specify a custom build directory:

.. code-block:: console

   $ kessel step env --build-dir /path/to/build

Example: Spack Deployment
--------------------------

To create a Spack deployment for your system:

.. code-block:: console

   $ mkdir my-deployment
   $ cd my-deployment
   $ kessel init --template spack-deployment
   $ kessel run ubuntu24.04

This will:

1. Set up the deployment structure
2. Bootstrap Spack
3. Create source mirrors
4. Build all specified environments
5. Finalize the deployment

Viewing Workflow Status
-----------------------

Check the current workflow status and progress:

.. code-block:: console

   $ kessel status

This displays a visual progress indicator showing completed and pending steps.

Resetting Workflow State
------------------------

If you need to start over or clear the workflow state:

.. code-block:: console

   $ kessel reset

This allows you to re-run steps from the beginning.

Debugging
---------

To see the shell commands that Kessel would execute without actually running them:

.. code-block:: console

   $ kessel --shell-debug run

This is useful for understanding what Kessel does or debugging issues.

Next Steps
----------

- Learn how to create custom workflows: :doc:`workflows`
- Set up Spack deployments: :doc:`deployments`
- Integrate Kessel with CI/CD pipelines

Common Commands Reference
-------------------------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Command
     - Description
   * - ``kessel init``
     - Initialize a new Kessel project
   * - ``kessel run``
     - Run the complete active workflow
   * - ``kessel step <name>``
     - Execute a specific workflow step
   * - ``kessel list``
     - List all available workflows
   * - ``kessel activate <name>``
     - Switch to a different workflow
   * - ``kessel status``
     - Show workflow progress
   * - ``kessel reset``
     - Reset workflow state
   * - ``kessel --help``
     - Show help for all commands
