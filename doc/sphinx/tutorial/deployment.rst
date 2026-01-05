Tutorial Part 3: Creating a Spack Deployment
=============================================

In this tutorial, you'll learn how to create a Spack deployment with pre-built environments. We'll create a deployment project, define environments for multiple systems, build the deployment, and use it with your project.

Prerequisites
-------------

- Completed :doc:`spack`
- Your ``myapp`` project from Parts 1 and 2

What is a Spack Deployment?
----------------------------

A Spack deployment is a complete, self-contained installation that includes:

- A specific version of Spack
- Pre-built software environments
- Source mirrors for offline builds (optional)
- System-specific configuration
- An activation script for easy use

Deployments are ideal for:

- Sharing compiled dependencies across development teams
- Creating consistent environments across multiple systems
- Enabling offline or air-gapped builds
- Providing reproducible CI/CD environments

Creating a Deployment Project
------------------------------

Let's create a deployment that includes our ``myapp`` application.

Initialize the Deployment
~~~~~~~~~~~~~~~~~~~~~~~~~

Create a new directory for the deployment:

.. code-block:: console

   $ mkdir myapp-deployment
   $ cd myapp-deployment
   $ kessel init --template spack-deployment

This creates the following structure:

.. code-block::

   myapp-deployment/
   ├── .kessel/
   │   └── workflows/
   │       └── default/
   │           └── workflow.py
   ├── config/
   │   ├── packages.yaml
   │   └── repos.yaml
   ├── environments/
   │   ├── ubuntu24.04/
   │   │   └── lammps/
   │   │       └── kokkos-cuda-ampere.yaml
   │   ├── macos_tahoe/
   │   │   └── lammps/
   │   │       └── kokkos-openmp.yaml
   │   └── darwin/
   │       └── lammps/
   │           └── kokkos-cuda-ampere.yaml
   └── .gitignore

Examining the Deployment Workflow
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let's look at the generated workflow:

.. code-block:: console

   $ cat .kessel/workflows/default/workflow.py

The workflow is simple:

.. code-block:: python

   from kessel.workflows.spack import Deployment

   class Default(Deployment):
       pass

The ``Deployment`` base class provides all the functionality needed to create deployments. It defines these steps:

1. **setup**: Initialize deployment structure and clone Spack
2. **bootstrap**: Bootstrap Spack (optionally create bootstrap mirror for offline use)
3. **mirror**: Optionally create source mirror of all packages
4. **envs**: Build all environments for the system
5. **finalize**: Clean up and set permissions

Configuring the Deployment
---------------------------

Now let's customize the deployment for our ``myapp`` application.

Customize the Workflow
~~~~~~~~~~~~~~~~~~~~~~

Edit ``.kessel/workflows/default/workflow.py``:

.. code-block:: python

   from kessel.workflows.spack import Deployment

   class Default(Deployment):
       steps = ["setup", "bootstrap", "mirror", "envs", "finalize"]

       # Spack version to use
       spack_url = "https://github.com/spack/spack.git"
       spack_ref = "v1.1.0"

       # Deployment options
       build_roots = True       # Build the root specs (not just dependencies)
       env_views = True         # Create unified views of installed packages
       bootstrap_mirror = False # Create bootstrap mirror

Key configuration options:

- ``spack_url``: Git URL for Spack (default: ``https://github.com/spack/spack.git``)
- ``spack_ref``: Spack version to use (branch, tag, or commit)
- ``build_roots``: Whether to build root specs (``True``) or just dependencies (``False``)
- ``env_views``: Whether to create unified environment views (``True`` or ``False``)
- ``bootstrap_mirror``: Whether to create a bootstrap mirror for offline bootstrapping (``True`` or ``False``, default: ``False``)

.. note::

   If you want to skip the source mirror creation, simply remove the ``mirror`` step from the ``steps`` list.

Project-Wide Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``config/`` directory contains project-wide configuration that applies to all environments and systems in the deployment. This is where you define common settings like package versions, compiler preferences, and repository configurations that should be consistent across your entire deployment.

Package Configuration
^^^^^^^^^^^^^^^^^^^^^

The ``config/packages.yaml`` file allows you to set project-wide defaults for packages. This is where you can specify version constraints, variants, and other build preferences that should apply across all environments in your deployment.

Edit ``config/packages.yaml`` to set project-wide defaults:

.. code-block:: yaml

   packages:
     myapp:
       require:
       - "@main"

     boost:
       require:
       - "@1.84.0"

     cmake:
       require:
       - "@3.27"

This configuration:

- Ensures ``myapp`` always uses the latest version from the main branch
- Locks Boost to version 1.84.0 across all environments
- Sets CMake to version 3.27 for consistency

By defining these in ``packages.yaml``, you maintain consistency and avoid version conflicts across your entire deployment.

Spack Repositories
^^^^^^^^^^^^^^^^^^

The ``config/repos.yaml`` file configures which Spack repositories should be used by the project. This includes both the default Spack recipes (builtin repository) and any custom repositories your project may need.

Edit ``config/repos.yaml`` to configure repositories:

.. code-block:: yaml

   repos:
     builtin:
       branch: releases/v2025.11.0

This configuration:

- Sets the builtin Spack repository (spack/spack-packages) to use the ``releases/v2025.11.0`` branch
- Ensures all environments use the same version of Spack package recipes

By carefully managing your repositories, you ensure that all environments in your deployment have access to the correct package recipes and versions. We'll add custom repositories later when we integrate our project's Spack package.

Defining Environments
---------------------

Now let's create an environment for our application.

Remove Example Environments
~~~~~~~~~~~~~~~~~~~~~~~~~~~

First, remove the example LAMMPS environments:

.. code-block:: console

   $ rm -rf environments/ubuntu24.04/lammps
   $ rm -rf environments/macos_tahoe/lammps
   $ rm -rf environments/darwin/lammps

Create Environment
~~~~~~~~~~~~~~~~~~

Create an environment for your workstation or laptop:

.. code-block:: console

   $ mkdir -p environments/workstation/myapp-dev

Create ``environments/workstation/myapp-dev.yaml``:

.. code-block:: yaml

   spack:
     include::
     - name: kessel
       path: $KESSEL_CONFIG_DIR

     specs:
     - myapp@main

     view: true

     concretizer:
       unify: true

This simple environment:

- Uses the Kessel configuration scope for system defaults
- Specifies only ``myapp@main`` as the root spec
- Spack will automatically resolve and install all dependencies (Boost, CMake, etc.)
- Creates a unified view of all installed packages

Your deployment structure should now look like:

.. code-block::

   myapp-deployment/
   ├── .kessel/
   │   └── workflows/
   │       └── default/
   │           └── workflow.py
   ├── config/
   │   ├── packages.yaml
   │   └── repos.yaml
   ├── environments/
   │   └── workstation/
   │       └── myapp-dev.yaml
   └── .gitignore

Adding Your Spack Repository
-----------------------------

The deployment needs access to your ``myapp`` Spack package recipe. In our case, the Spack recipe is part of the ``myapp`` repository itself, so we need to:

1. Clone the source repository
2. Make the Spack recipe visible to Spack

Configure Source Repository
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Edit ``.kessel/workflows/default/workflow.py`` to add logic for cloning your source repository:

.. code-block:: python
   :emphasize-lines: 16-30

   from kessel.workflows.spack import Deployment
   from kessel.workflows import *

   class Default(Deployment):
       steps = ["setup", "bootstrap", "mirror", "envs", "finalize"]

       # Spack version to use
       spack_url = "https://github.com/spack/spack.git"
       spack_ref = "v1.1.0"

       # Deployment options
       build_roots = True       # Build the root specs (not just dependencies)
       env_views = True         # Create unified views of installed packages
       bootstrap_mirror = False # Create bootstrap mirror (optional)

       # Source repository for myapp
       myapp_source_repo = environment("https://github.com/myorg/myapp.git")
       myapp_checkout = environment(variable="MYAPP_CHECKOUT")

       def setup(self, args):
           """Setup deployment and clone source repositories"""
           # Set checkout path
           self.myapp_checkout = self.deployment / "extern" / "myapp"

           # Call parent setup first
           super().setup(args)

           # Clone myapp source repository
           if not self.myapp_checkout.exists():
               self.exec(f"git clone {self.myapp_source_repo} {self.myapp_checkout}")

.. note::

   To make this work without creating a remote Git repository for our tutorial,
   first go to your ``myapp`` checkout and make it a real git repository.

   .. code-block:: console

      $ git init -b main
      $ git commit -m "Initial commit"

   With this local git repository we can now set our ``myapp_source_repo`` to use the folder location reported by the following command:

   .. code-block:: console

      $ git rev-parse --absolute-git-dir


.. note::

   If you do not need an installed version of your app and only need the
   environments for developments, set ``build_roots`` to ``False``.

Register Spack Repository
~~~~~~~~~~~~~~~~~~~~~~~~~

Edit ``config/repos.yaml`` to register the Spack package repository:

.. code-block:: yaml
   :emphasize-lines: 2

   repos:
     myapp: $MYAPP_CHECKOUT/spack_repo/myapp
     builtin:
       branch: releases/v2025.11.0

This will make all Spack environments use the Spack repository in
``$MYAPP_CHECKOUT/spack_repo/myapp``. While building the deployment
``MYAPP_CHECKOUT`` will point to ``$KESSEL_DEPLOYMENT/extern/myapp``. When using
the environment for development it might however point to  a different location
such as a local checkout of your ``myapp`` source code.

If this flexibility isn't needed, e.g. if you're only building deployments for
production binaries, you can instead always point to the deployment location:

.. code-block:: yaml
   :emphasize-lines: 2

   repos:
     myapp: $KESSEL_DEPLOYMENT/extern/myapp/spack_repo/myapp
     builtin:
       branch: releases/v2025.11.0

Building the Deployment
-----------------------

Now we're ready to build the deployment.

Build for your workstation
~~~~~~~~~~~~~~~~~~~~~~~~~~

Run the deployment workflow:

.. code-block:: console

   $ kessel run workstation

This will:

1. Clone your currently active Kessel version
2. Clone spack/spack and spack/spack-packages repositories
3. Bootstrap Spack (and optionally create a bootstrap mirror)
4. Optionally create source mirrors for offline builds
5. Build the ``myapp`` environment
6. Create environment views
7. Finalize the deployment

.. note::

   Notice that you don't need to have Spack pre-installed. The deployment process automatically clones and sets up Spack for you.

The process may take some time depending on your system, network speed, and the number of dependencies to build.

Customize Deployment Location
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default, deployments are created in ``build/``. You can specify a different location:

.. code-block:: console

   $ kessel run -D ~/deployments/myapp workstation

Using the Deployment
---------------------

Once built, the deployment is ready to use.

Activate the Deployment
~~~~~~~~~~~~~~~~~~~~~~~

Source the activation script:

.. code-block:: console

   $ source build/activate.sh

This sets up:

- ``KESSEL_DEPLOYMENT``: Path to the deployment
- ``KESSEL_SYSTEM``: System name (``workstation``)
- Spack environment variables
- Access to the Spack and Kessel installation

List Available Environments
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: console

   $ spack env list
   ==> 1 environment
       myapp

Activate an Environment
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: console

   $ spack env activate myapp
   $ which myapp
   /path/to/build/var/spack/environments/workstation/myapp/.spack-env/view/bin/myapp

Run the Application
~~~~~~~~~~~~~~~~~~~

.. code-block:: console

   $ myapp
   Hello, World!
   Using Boost 1.84.0

Using with Your Development Workflow
-------------------------------------

Now let's use the deployment with your ``myapp`` project workflow.

Adjusting our workflow for using the deployment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Given that our deployment environments depend on the ``MYAPP_CHECKOUT`` variable
being set, we have to make a small modification to our existing workflow from
Part 2 so that variable is set.

Our ``env`` step already has a ``source_dir`` property that can optionally be
set via the command-line option. To set the environment variable
``MYAPP_CHECKOUT`` to the same location, we simply add another environment
property and set it after the existing ``env`` logic. This also showcases how
you can extend existing step logic in your own workflows.

.. code-block:: python

   from kessel.workflows.spack import BuildEnvironment
   from kessel.workflows.cmake import CMake
   from kessel.workflows import *

   class Default(BuildEnvironment, CMake):
       steps = ["env", "configure", "build", "test"]

       spack_env = environment("myapp-dev")
       project_spec = environment("myapp@main")
       myapp_checkout = environment(variable="MYAPP_CHECKOUT")

       def env(self, args):
           """Prepare Environment"""
           super().env(args)
           self.myapp_checkout = self.source_dir

.. warning::

   When overriding existing step functions, make sure to also write a docstring for your step.

Build with Deployment
~~~~~~~~~~~~~~~~~~~~~

Activate the deployment and run your workflow:

.. code-block:: console

   $ source /path/to/myapp-deployment/build/activate.sh
   $ cd /path/to/myapp
   $ kessel run

Kessel will:

1. Activate the ``myapp-dev`` environment from the deployment
2. Configure CMake with the pre-built dependencies
3. Build and test your application

This is much faster than building dependencies from scratch!

Advanced: Multi-System Deployments
-----------------------------------

You can build deployments for multiple systems from the same configuration.

Build for macOS
~~~~~~~~~~~~~~~

First, create an environment for macOS:

.. code-block:: console

   $ mkdir -p environments/macos_tahoe/myapp

Create ``environments/macos_tahoe/myapp.yaml``:

.. code-block:: yaml

   spack:
     include::
     - name: kessel
       path: $KESSEL_CONFIG_DIR

     specs:
     - myapp@main

     view: true

     concretizer:
       unify: true

Then on a macOS system, build the deployment:

.. code-block:: console

   $ cd myapp-deployment
   $ kessel run macos_tahoe

This creates a separate deployment with macOS-specific builds.

System-Specific Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For system-specific settings, create ``config/<system>/`` directories:

.. code-block:: console

   $ mkdir -p config/ubuntu24.04
   $ mkdir -p config/macos_tahoe

**config/ubuntu24.04/packages.yaml**:

.. code-block:: yaml

   packages:
     gcc:
       require:
       - "@13.2.0"

**config/macos_tahoe/packages.yaml**:

.. code-block:: yaml

   packages:
     llvm:
       require:
       - "@17.0.0"

These configurations are automatically included when building for that system.

Advanced: Using Configuration Templates
---------------------------------------

Kessel provides reusable configuration templates for common configurations like compilers, MPI libraries, and GPU architectures.

Using Templates
~~~~~~~~~~~~~~~

You can include templates in your environment configuration. For example, to use GCC and MPICH:

``environments/workstation/myapp.yaml``:

.. code-block:: yaml

   spack:
     include::
     - $KESSEL_CONFIG_DIR/templates/gcc.yaml
     - $KESSEL_CONFIG_DIR/templates/mpich.yaml
     - name: kessel
       path: $KESSEL_CONFIG_DIR

     specs:
     - myapp@main

     view: true

Available templates include:

- **Compilers**:

  - ``gcc.yaml``
  - ``clang.yaml``
  - ``apple-clang.yaml``
  - ``oneapi.yaml``

- **MPI**:

  - ``mpich.yaml``
  - ``openmpi.yaml``
  - ``cray-mpich.yaml``

- **GPU**:

  - ``cuda-ampere.yaml``
  - ``cuda-volta.yaml``
  - ``rocm-gfx90a.yaml``
  - ``rocm-gfx942.yaml``

Templates provide sensible defaults that can be overridden in your environment's ``packages:`` section if needed.

Advanced: Deployment Options
----------------------------

Set Permissions
~~~~~~~~~~~~~~~

For shared deployments, set appropriate permissions:

.. code-block:: python

   class Default(Deployment):
       permissions = "775"
       user = "deployment_user"
       group = "dev_team"

Git Mirroring
~~~~~~~~~~~~~

Git clones or submodules of other repositories can not only serve as Spack
repositories, but can be used as mirror sources for Spack during package
installation.

.. code-block:: python

   class Default(Deployment):
      git_mirrors = ["extern/myapp"]

By adding subdirectories relative to the deployment folder to the
``git_mirrors`` list, the ``git`` property of each package is overwritten to
that location.

.. code-block:: yaml

   packages:
      myapp:
         package_attributes:
            git: file:///path/to/deployment/extern/myapp/.git

.. note::

   Names of the directories listed in ``git_mirrors`` must match the package names in Spack.

During ``setup``, a full clone will be made to its equivalent deployment destination if the
relative folder exists in the the deployment configuration (e.g. via a git
submodule). Otherwise, it is assumed to be manually created in other steps.

Summary
-------

In this tutorial, you:

1. Created a Spack deployment project with ``kessel init --template spack-deployment``
2. Configured the deployment workflow and project-wide settings
3. Defined multiple environments for different systems and purposes
4. Built the deployment with pre-compiled dependencies
5. Activated and used the deployment
6. Integrated the deployment with your development workflow
7. Explored advanced features like templates and multi-system support

Next Steps
----------

- Read the full :doc:`../deployments` documentation
- Explore :doc:`../workflows` for more workflow patterns
- Check the :doc:`../cli_reference` for all available commands
