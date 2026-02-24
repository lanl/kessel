Spack Deployments
=================

Spack deployments are complete, self-contained installations of Spack with pre-built software environments for a specific system. They provide a standardized way to deploy and manage software stacks across HPC systems and development environments.

Overview
--------

A deployment project contains configuration for multiple systems. When you build a deployment for a specific system, it generates a complete deployment containing:

- A Spack installation at a specific version
- System-specific Spack configuration (project and system settings)
- Source mirrors for offline builds
- Spack environments with built software for that system only
- An activation script to use the deployment

Deployments are particularly useful for:

- Providing consistent software stacks across multiple systems
- Enabling offline or air-gapped builds
- Sharing compiled dependencies among development teams
- Creating reproducible CI/CD environments

Deployment Structure
--------------------

A typical deployment project has the following structure:

.. code-block::

   my-deployment/
   ├── .kessel/
   │   └── workflows/
   │       └── default/
   │           └── workflow.py
   ├── config/
   │   └── packages.yaml
   └── environments/
       ├── ubuntu24.04/
       │   └── myapp.yaml
       └── macos-tahoe/
           └── myapp.yaml

Key directories:

- ``.kessel/workflows/default/``: Deployment workflow definition
- ``config/``: Spack configuration files
- ``environments/``: System-specific Spack environment definitions

Creating a Deployment Project
------------------------------

Initialize a new deployment project:

.. code-block:: console

   $ mkdir my-deployment
   $ cd my-deployment
   $ kessel init --template spack-deployment

This creates the basic structure with a default workflow.

Configuring the Deployment Workflow
------------------------------------

Edit ``.kessel/workflows/default/workflow.py`` to configure your deployment:

.. code-block:: python

   from kessel.workflows.base.spack import Deployment

   class Default(Deployment):
       steps = ["setup", "bootstrap", "mirror", "envs", "finalize"]

       # Spack version to use
       spack_url = "https://github.com/spack/spack.git"
       spack_ref = "v1.1.0"

       # Deployment options
       build_roots = False
       env_views = True

       # Git repositories to mirror
       git_mirrors = []

       # Packages to exclude from source mirror
       mirror_exclude = [
           "cmake",
           "ninja",
           "python"
       ]

       # Packages to exclude from final deployment
       build_exclude = [
           "llvm"
       ]

Configuration Options
~~~~~~~~~~~~~~~~~~~~~

**spack_url**
  Git URL for the Spack repository. Default: ``https://github.com/spack/spack.git``

**spack_ref**
  Git branch, tag, or commit to use. Examples: ``v1.1.0``, ``develop``

**site_configs_url**
  Git URL for a site-specific configuration repository (optional). When provided, this repository is cloned into ``config/site/`` during deployment setup and included in the Spack configuration hierarchy. Default: ``""`` (disabled)

**site_configs_ref**
  Git branch, tag, or commit to use for the site configs repository. Default: ``"main"``

**build_roots**
  If ``True``, builds the root specs defined in environments. If ``False``, only builds dependencies. Default: ``False``

**env_views**
  If ``True``, creates unified views of installed packages in each environment. Default: ``False``

**git_mirrors**
  List of Git repository paths to mirror into the deployment. These mirrored repositories can be used for Spack installations when network access to the original Git repositories isn't available on the compute node where the deployment is installed.

**mirror_exclude**
  List of package names to exclude from the source mirror.

**build_exclude**
  List of package names to uninstall after building environments.

Configuring Spack
-----------------

Kessel uses Spack's configuration scope system to provide flexible, layered configuration. A deployment defines multiple configuration scopes that environments can include and combine.

Configuration Scopes
~~~~~~~~~~~~~~~~~~~~

Kessel deployments use the following configuration scopes, in order of increasing precedence:

- **Spack defaults**: Built-in Spack configurations (lowest priority)
- **Kessel defaults**: Built-in Kessel configurations
- **Site defaults**: Configuration from ``config/site/`` (if ``site_configs_url`` is set)
- **Site system defaults**: System-specific site configuration from ``config/site/<SYSTEM>/``
- **Project defaults**: Configuration in ``config/`` directory
- **Project system defaults**: Configuration in ``config/<SYSTEM>/`` directory
- **Environment-specific**: Configuration in the environment's ``spack.yaml`` (highest priority)

The available scopes are defined in ``etc/kessel/spack-deployment/include.yaml`` within the Kessel installation.

Site Configuration Scope
^^^^^^^^^^^^^^^^^^^^^^^^

The site configuration scope is optional and enabled by setting ``site_configs_url`` in your deployment workflow. When enabled, Kessel clones the specified Git repository into ``config/site/`` during the setup step.

Site configurations can include both general settings (``config/site/*.yaml``) and system-specific settings (``config/site/<SYSTEM>/*.yaml``). This allows organizations to:

- Maintain site-wide or facility-wide Spack configurations separately from deployment projects
- Define system-specific defaults that apply across all deployments at a site
- Share common configuration across multiple deployment projects
- Version control site-specific settings independently
- Separate proprietary or sensitive configurations from public deployment configs

The site configuration has higher precedence than Spack and Kessel defaults but lower precedence than project-specific configuration, allowing projects to override site settings when needed.

Using Configuration Scopes
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Environments reference configuration scopes using the ``include::`` key in their ``spack.yaml``:

.. code-block:: yaml

   spack:
     include::
     - name: kessel
       path: $KESSEL_CONFIG_DIR

     specs:
     - myapp

The ``include::`` syntax (with double colon) overrides Spack's default ``include:`` behavior and allows specifying named configuration scopes with paths.

Configuration Templates
~~~~~~~~~~~~~~~~~~~~~~~

Kessel provides reusable configuration templates that can be combined to build environment configurations. These templates define common settings for compilers, MPI libraries, and hardware accelerators.

Templates are available in:

- ``$KESSEL_CONFIG_DIR/templates/`` - General templates usable across all systems
- ``$KESSEL_CONFIG_DIR/<SYSTEM>/templates/`` - System-specific templates

Example using templates:

.. code-block:: yaml

   spack:
     include::
     - $KESSEL_CONFIG_DIR/templates/gcc.yaml
     - $KESSEL_CONFIG_DIR/templates/mpich.yaml
     - $KESSEL_CONFIG_DIR/templates/cuda-ampere.yaml
     - name: kessel
       path: $KESSEL_CONFIG_DIR

     specs:
     - flecsi

     packages:
       flecsi:
         require:
         - "backend=mpi build_type=Debug +flog +hdf5 %c,cxx=clang"
       kokkos:
         require:
         - "+cuda cuda_arch=80 +hwloc ~wrapper %cxx=clang"
       cuda:
         require:
         - "+allow-unsupported-compilers"

This approach allows you to:

1. Include general compiler settings (``gcc.yaml``)
2. Include MPI library configuration (``mpich.yaml``)
3. Include GPU architecture settings (``cuda-ampere.yaml``)
4. Include the base Kessel configuration
5. Override specific package requirements in the environment

Project Configuration
~~~~~~~~~~~~~~~~~~~~~

The ``config/`` directory in your deployment project provides project-wide defaults. A common use case is locking down specific dependency versions:

**config/packages.yaml** - Lock dependency versions:

.. code-block:: yaml

   packages:
     cmake:
       require:
       - "@3.22.1"

     openmpi:
       require:
       - "@4.1.5"

System-Specific Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For system-specific settings, create ``config/<SYSTEM>/`` directories:

.. code-block::

   config/
   ├── packages.yaml          # Project defaults
   ├── ubuntu24.04/
   │   └── packages.yaml      # Ubuntu-specific settings
   └── macos-tahoe/
       └── packages.yaml      # System-specific settings

These system-specific configurations are automatically included when building environments for that system.

Site-Specific Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~

For organization-wide or facility-wide settings that should be shared across multiple deployment projects, use the site configuration feature. This is particularly useful when:

- Managing deployments across multiple HPC facilities with shared policies
- Maintaining proprietary configurations separately from public deployment configs
- Standardizing compiler and package preferences across an organization
- Sharing mirror locations or upstream installations

Configuring Site Configs
^^^^^^^^^^^^^^^^^^^^^^^^

Enable site configs in your deployment workflow:

.. code-block:: python

   from kessel.workflows.base.spack import Deployment

   class Default(Deployment):
       spack_url = "https://github.com/spack/spack.git"
       spack_ref = "v1.1.0"

       # Site-specific configuration
       site_configs_url = "https://github.com/myorg/spack-site-configs.git"
       site_configs_ref = "v1.0.0"  # Can use branch, tag, or commit

Relative URLs are supported for repositories in the same organization:

.. code-block:: python

   # If deployment config is at github.com/myorg/deployment-config
   # This resolves to github.com/myorg/spack-site-configs
   site_configs_url = "../spack-site-configs.git"

Site Config Repository Structure
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A site configuration repository should follow the standard Spack configuration structure and can include both general and system-specific settings:

.. code-block::

   spack-site-configs/
   ├── packages.yaml           # Site-wide package preferences
   ├── mirrors.yaml            # Site-wide mirror locations
   ├── config.yaml             # Site-wide general settings
   ├── modules.yaml            # Site-wide module generation
   ├── upstreams.yaml          # Site-wide upstream installations
   ├── ubuntu24.04/            # System-specific site settings
   │   └── packages.yaml
   └── macos-tahoe/            # Another system's site settings
       └── packages.yaml

Example site ``packages.yaml``:

.. code-block:: yaml

   packages:
     # Organization-wide compiler preference
     all:
       compiler: [gcc@13.2.0, clang@17.0.0]
       target: [x86_64_v3]

     # Prefer system packages for utilities
     openssl:
       externals:
       - spec: openssl@3.0.2
         prefix: /usr
       buildable: false

     curl:
       externals:
       - spec: curl@7.81.0
         prefix: /usr
       buildable: false

     # Organization standard versions
     cmake:
       require: ["@3.27:"]

     python:
       require: ["@3.11:"]

Example site ``mirrors.yaml``:

.. code-block:: yaml

   mirrors:
     facility-cache:
       url: https://cache.facility.org/spack
       signed: true

     facility-source:
       url: file:///facility/mirrors/source

Configuration Priority
^^^^^^^^^^^^^^^^^^^^^^

When site configs are enabled, the full configuration hierarchy is:

1. Spack defaults (lowest priority)
2. Kessel defaults
3. **Site defaults** (``config/site/``)
4. **Site system defaults** (``config/site/<SYSTEM>/``)
5. Project defaults (``config/``)
6. Project system defaults (``config/<SYSTEM>/``)
7. Environment-specific (highest priority)

This allows:

- Site configs to override Spack and Kessel defaults
- Site system configs to provide system-specific site-wide settings
- Project configs to override site-wide policies when needed
- Project system configs to provide final system-specific overrides
- Environments to have ultimate control

Example: Multi-Facility Deployment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Suppose you manage deployments for multiple HPC facilities:

**Site config repository** (shared across facilities):

.. code-block:: yaml

   # packages.yaml
   packages:
     all:
       target: [x86_64_v3]

     cmake:
       require: ["@3.27:"]

     python:
       require: ["@3.11:"]

**Deployment workflow** (references site configs):

.. code-block:: python

   from kessel.workflows.base.spack import Deployment

   class Default(Deployment):
       spack_url = "https://github.com/spack/spack.git"
       spack_ref = "v1.1.0"

       # Shared configuration for all facilities
       site_configs_url = "https://github.com/hpc-facilities/spack-configs.git"
       site_configs_ref = "v2024.1"

**Site system-specific settings** in site config repository (``config/site/facility-a/packages.yaml``):

.. code-block:: yaml

   packages:
     # Facility A uses Cray MPI across all deployments
     mpi:
       require: ["cray-mpich@8.1.27"]

**Project system-specific overrides** in deployment project (``config/facility-a/packages.yaml``):

.. code-block:: yaml

   packages:
     # This specific deployment uses a newer Cray MPI
     mpi:
       require: ["cray-mpich@8.1.28"]

Best Practices for Site Configs
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. **Version your site configs**: Use tags for ``site_configs_ref`` to ensure reproducibility
2. **Keep minimal**: Only include truly site-wide settings in site configs
3. **Document thoroughly**: Include a README explaining the purpose of each configuration
4. **Test changes**: Test site config updates in development before production
5. **Use appropriate scopes**:

   - Site configs: Settings shared across all deployments
   - Project configs: Deployment-specific settings
   - System configs: System-specific overrides
   - Environment configs: Environment-specific requirements

Defining Environments
---------------------

Environments are defined as YAML files under ``environments/<system>/``.

Directory Structure
~~~~~~~~~~~~~~~~~~~

.. code-block::

   environments/
   ├── ubuntu24.04/
   │   ├── myapp.yaml
   │   └── dev-tools.yaml
   └── macos-tahoe/
       └── myapp.yaml

Each ``<system>/<env-name>.yaml`` file defines a Spack environment. During deployment, Kessel automatically generates the Spack-compliant folder structure (``<env-name>/spack.yaml``) from these files.

Example Environment File
~~~~~~~~~~~~~~~~~~~~~~~~

``environments/ubuntu24.04/myapp.yaml``:

.. code-block:: yaml

   spack:
     include::
     - name: kessel
       path: $KESSEL_CONFIG_DIR

     specs:
     - myapp@main +mpi
     - cmake@3.27
     - openmpi@4.1.5

     view: true

     concretizer:
       unify: true

The ``include::`` directive ensures the environment uses Kessel's configuration scopes. The ``specs`` list defines what packages to install in this environment. During deployment, this file is converted to the standard Spack environment structure (``myapp/spack.yaml``).

Creating a Deployment
---------------------

Once configured, create the deployment for a specific system:

.. code-block:: console

   $ kessel run ubuntu24.04

You can specify a custom deployment location:

.. code-block:: console

   $ kessel run -D /path/to/deployment ubuntu24.04
   # or
   $ kessel run --deployment /path/to/deployment ubuntu24.04

This executes the deployment workflow:

1. **setup**: Initialize deployment structure and clone Spack
2. **bootstrap**: Bootstrap Spack and create bootstrap mirror for offline use
3. **mirror**: Create source mirror of all required packages
4. **envs**: Build all environments defined for the system
5. **finalize**: Clean up and set permissions

The deployment is created in the ``build/`` directory by default.

Deployment Steps in Detail
---------------------------

Setup
~~~~~

The setup step:

- Creates the deployment directory structure
- Clones Spack at the specified version
- Clones spack/spack-packages repository
- Generates an ``activate.sh`` script
- Mirrors any Git repositories specified in ``git_mirrors``
- Copies configuration files from ``config/`` and ``config/<SYSTEM>/`` to the deployment

Bootstrap
~~~~~~~~~

The bootstrap step:

- Bootstraps Spack so it can function properly
- Creates a bootstrap mirror for offline use
- Finds system compilers

Mirror
~~~~~~

The mirror step:

- Creates a source mirror of all packages needed by all environments
- Excludes packages listed in ``mirror_exclude``

This enables offline builds and faster rebuilds.

Environments
~~~~~~~~~~~~

The envs step:

- Builds all environments found in ``environments/<system>/``
- Installs all specs defined in each environment's ``spack.yaml``
- If ``build_roots=True``, installs the root specs; if ``False``, only installs their dependencies
- Creates environment views if ``env_views=True``

Finalize
~~~~~~~~

The finalize step:

- Uninstalls packages listed in ``build_exclude``
- Runs garbage collection to remove unused dependencies
- Sets file permissions according to ``permissions`` setting
- Creates a final deployment marker

Using a Deployment
------------------

Activating a Deployment
~~~~~~~~~~~~~~~~~~~~~~~

To use a deployment, source its activation script directly:

.. code-block:: console

   $ source /path/to/deployment/activate.sh

This sets up:

- ``KESSEL_DEPLOYMENT``: Path to the deployment
- ``KESSEL_SYSTEM``: System name
- Spack environment variables
- Access to the Spack installation

The activation script is generated during the deployment creation process and provides everything needed to use the deployment.

Using Environments
~~~~~~~~~~~~~~~~~~

Once activated, you can use any environment in the deployment:

.. code-block:: console

   $ spack env activate myapp
   $ which myapp
   /path/to/deployment/environments/ubuntu24.04/myapp/.spack-env/view/bin/myapp

Building Projects with Deployments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use a deployment in your project's workflow:

.. code-block:: python

   from kessel.workflows.base.spack import BuildEnvironment
   from kessel.workflows.base.cmake import CMake

   class Default(BuildEnvironment, CMake):
       steps = ["env", "configure", "build", "test"]

       spack_env = environment("myapp")
       project_spec = environment("myproject@main")

Then activate the deployment and run:

.. code-block:: console

   $ source /path/to/deployment/activate.sh
   $ cd /path/to/my-project
   $ kessel run

Advanced Topics
---------------

Multi-System Deployments
~~~~~~~~~~~~~~~~~~~~~~~~

You can create deployments for multiple systems from the same deployment project configuration. Each deployment must be created on its respective target system:

.. code-block:: console

   # On Ubuntu system:
   $ kessel run ubuntu24.04

   # On macOS system:
   $ kessel run macos-tahoe

   # On RHEL system:
   $ kessel run rhel8

Each system gets its own deployment with the appropriate environments.

Incremental Updates
~~~~~~~~~~~~~~~~~~~

To update an existing deployment with new packages:

1. Modify the environment's ``spack.yaml``
2. Rerun the deployment:

.. code-block:: console

   $ kessel run ubuntu24.04

The deployment process is idempotent and will only build new packages.

Git Repository Mirroring
~~~~~~~~~~~~~~~~~~~~~~~~

To mirror Git repositories into the deployment, you must first ensure the repositories exist in your deployment project, then specify them in ``git_mirrors``:

**Option 1: Using Git Submodules**

.. code-block:: console

   $ cd my-deployment
   $ git submodule add https://github.com/myorg/my-repo.git repos/my-repo

Then in your workflow:

.. code-block:: python

   class Default(Deployment):
       git_mirrors = ["repos/my-repo"]

**Option 2: Custom Setup Step**

Override the ``setup`` step to clone repositories:

.. code-block:: python

   class Default(Deployment):
       git_mirrors = ["repos/my-repo"]

       def setup(self, args):
           """Setup"""
           # Clone repositories before calling parent setup
           repo_path = self.deployment / "repos/my-repo"
           if not repo_path.exists():
               self.exec(
                   f"git clone https://github.com/myorg/my-repo.git {repo_path}"
               )

           # Call parent setup to complete deployment initialization
           super().setup(args)

The ``git_mirrors`` list specifies paths (relative to the deployment project) that will be cloned into the deployment during the setup step. These mirrored repositories can be used for package installations when network access is unavailable on compute nodes.

Deployment Best Practices
--------------------------

1. **Pin Spack versions**: Use specific tags (e.g., ``v1.1.0``) rather than ``develop`` for reproducibility
2. **Test locally first**: Create deployments on a local system before deploying to production
3. **Use external packages**: Mark system packages as external to avoid rebuilding them
4. **Exclude build dependencies**: Use ``build_exclude`` to remove packages only needed during builds
5. **Version control**: Keep deployment configurations in Git
6. **Document environment purposes**: Use clear names for environments (e.g., ``dev-tools``, ``production``)
7. **Mirror sources**: Always create source mirrors for offline capability
8. **Set appropriate permissions**: Configure ``permissions`` based on whether the deployment is shared

Troubleshooting
---------------

Build Failures
~~~~~~~~~~~~~~

If a package fails to build:

1. Check the Spack build log
2. Check for missing system dependencies
3. Verify compiler configuration with ``spack compiler list``
4. Try building the package manually with Spack to debug

.. code-block:: console

   $ source build/activate.sh
   $ spack install --verbose <package-spec>

Mirror Issues
~~~~~~~~~~~~~

If source mirroring fails:

1. Check network connectivity
2. Add problematic packages to ``mirror_exclude``
3. Manually download sources if needed
4. Verify mirror configuration

Permission Errors
~~~~~~~~~~~~~~~~~

If you encounter permission errors:

1. Check the ``permissions`` setting in the workflow
2. Ensure you have write access to the deployment directory
3. Verify file ownership matches ``user`` and ``group`` settings

Example: Complete Deployment
----------------------------

Here's a complete example for a deployment with LAMMPS:

``.kessel/workflows/default/workflow.py``:

.. code-block:: python

   from kessel.workflows.base.spack import Deployment

   class Default(Deployment):
       steps = ["setup", "bootstrap", "mirror", "envs", "finalize"]

       spack_url = "https://github.com/spack/spack.git"
       spack_ref = "v1.1.0"

       build_roots = True
       env_views = True

``config/packages.yaml``:

.. code-block:: yaml

   packages:
     cmake:
       require:
       - "@3.22.1"

     openmpi:
       require:
       - "@4.1.5"

``environments/ubuntu24.04/lammps.yaml``:

.. code-block:: yaml

   spack:
     include::
     - name: kessel
       path: $KESSEL_CONFIG_DIR

     specs:
     - lammps@20251210 +mpi +kokkos

     view: true

Create the deployment:

.. code-block:: console

   $ kessel run ubuntu24.04
