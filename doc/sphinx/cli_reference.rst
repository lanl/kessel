CLI Reference
=============

This document provides a comprehensive reference for Kessel's command-line interface.

Basic Usage
-----------

The general syntax for Kessel commands is:

.. code-block:: console

   $ kessel [GLOBAL_OPTIONS] <COMMAND> [COMMAND_OPTIONS] [ARGUMENTS]

For help on any command:

.. code-block:: console

   $ kessel --help
   $ kessel <COMMAND> --help

Global Options
--------------

``--shell-debug``
  Output shell commands instead of executing them.

``--version``
  Display the version of Kessel.

Commands
--------

kessel init
~~~~~~~~~~~

Initialize a new Kessel project.

.. code-block:: console

   $ kessel init [--template TEMPLATE] [DIRECTORY]

Arguments:
  - ``DIRECTORY``: The directory to initialize (default: current directory)

Options:
  - ``-t, --template TEMPLATE``: The template to use (default: spack-project)

kessel run
~~~~~~~~~~

Run all steps in the active workflow.

.. code-block:: console

   $ kessel run [--until STEP] [STEP_OPTIONS]

Options:
  - ``-u, --until STEP``: Run until (and including) the specified step
  - All command-line options from the workflow's steps are also available

Example with step options:

.. code-block:: console

   $ kessel run --build-dir /tmp/build --jobs 8

kessel step
~~~~~~~~~~~

Run a specific step in the active workflow.

.. code-block:: console

   $ kessel step <STEP> [OPTIONS]

Arguments:
  - ``STEP``: The name of the step to run

Options depend on the specific step and workflow configuration.

kessel workflow
~~~~~~~~~~~~~~~

Manage workflows.

.. code-block:: console

   $ kessel workflow <SUBCOMMAND>

Subcommands:
  - ``list``: List available workflows
  - ``activate <NAME>``: Activate a workflow
  - ``status``: Show the status of the current workflow
  - ``edit``: Edit the current workflow

kessel deploy
~~~~~~~~~~~~~

Manage Spack deployments.

.. code-block:: console

   $ kessel deploy <SUBCOMMAND> [OPTIONS]

Subcommands:

``activate``
  Activate an existing deployment.

  .. code-block:: console

     $ kessel deploy activate [PATH]

  Arguments:
    - ``PATH``: Path to the deployment (default: current directory)

``replicate``
  Replicate an existing deployment to a new location.

  .. code-block:: console

     $ kessel deploy replicate [SRC] DEST

  Arguments:
    - ``SRC``: Source deployment folder (default: active deployment)
    - ``DEST``: Destination folder

kessel build-env
~~~~~~~~~~~~~~~~

Manage build environments.

.. code-block:: console

   $ kessel build-env <SUBCOMMAND>

Subcommands and options depend on the specific implementation.

kessel reset
~~~~~~~~~~~~

Reset the workflow state.

.. code-block:: console

   $ kessel reset

This command resets the workflow state by clearing environment variables and reloading the initial setup script. It allows you to re-run steps from the beginning.

Environment Variables
---------------------

``KESSEL_WORKFLOW``
  The name of the active workflow.

``KESSEL_DEPLOYMENT``
  The path to the active Spack deployment.

``KESSEL_SYSTEM``
  The name of the current system.

``KESSEL_CONFIG_DIR``
  The directory containing Kessel configuration files.

``KESSEL_ROOT``
  The root directory of the Kessel installation.

``KESSEL_RUN_STATE``
  The last completed step in the current workflow run.

Common Usage Patterns
---------------------

Initialize and Run a Project
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: console

   $ cd my-project
   $ kessel init
   $ kessel run

Run Specific Steps
~~~~~~~~~~~~~~~~~~

.. code-block:: console

   $ kessel step env
   $ kessel step configure
   $ kessel step build

Run Until a Specific Step
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: console

   $ kessel run --until build

Switch Between Workflows
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: console

   $ kessel workflow list
   $ kessel workflow activate release
   $ kessel run

Debug Shell Commands
~~~~~~~~~~~~~~~~~~~~

.. code-block:: console

   $ kessel --shell-debug run

Create a Deployment
~~~~~~~~~~~~~~~~~~~

.. code-block:: console

   $ cd my-deployment
   $ kessel init --template spack-deployment
   $ kessel run ubuntu24.04

Use a Deployment
~~~~~~~~~~~~~~~~

.. code-block:: console

   $ source /path/to/deployment/activate.sh
   $ cd my-project
   $ kessel run

Exit Codes
----------

- ``0``: Success
- ``1``: Error occurred during execution