Workflows
=========

Workflows are the core abstraction in Kessel. A workflow defines a sequence of steps that need to be executed to accomplish a task, such as building and testing a project or deploying software environments.

Workflow Concepts
-----------------

A workflow consists of:

- **Steps**: Individual units of work (e.g., configure, build, test)
- **Environment State**: Variables that persist across steps
- **Shell Scripts**: Reusable scripts that implement common patterns
- **Python Logic**: Workflow orchestration and argument handling

Workflows bridge the gap between developer command-line usage and CI/CD automation by providing a consistent interface for both contexts.

Workflow Directory Structure
-----------------------------

Workflows are defined in the ``.kessel/workflows/`` directory:

.. code-block::

   .kessel/
   └── workflows/
       ├── default.py
       ├── debug.py
       └── release.py

Simple workflows are defined as ``.py`` files directly in the workflows directory. For workflows that need additional resources (scripts, requirements.txt, etc.), use a package structure:

.. code-block::

   .kessel/
   └── workflows/
       ├── default.py
       └── format/
           ├── __init__.py
           ├── requirements.txt
           └── format.sh

The old structure with ``<name>/workflow.py`` is still supported for backwards compatibility.

Defining a Workflow
-------------------

Basic Workflow Structure
~~~~~~~~~~~~~~~~~~~~~~~~

A workflow is defined as a Python class that inherits from ``Workflow`` or one of the built-in workflow base classes:

.. code-block:: python

   from kessel.workflows import Workflow

   class Default(Workflow):
       steps = ["setup", "build", "test"]
       
       def setup(self, args):
           """Setup Environment"""
           # Setup logic here
           pass
       
       def build(self, args):
           """Build Project"""
           # Build logic here
           pass
       
       def test(self, args):
           """Run Tests"""
           # Test logic here
           pass

Key components:

- **Class name**: Must match the workflow directory name (capitalized)
- **steps**: List of step names in execution order
- **Step methods**: Methods corresponding to each step name
- **Docstrings**: First line becomes the step title in status display

Environment Variables
~~~~~~~~~~~~~~~~~~~~~

Workflows can define persistent environment variables using the ``environment()`` decorator:

.. code-block:: python

   from kessel.workflows import Workflow, environment
   from pathlib import Path

   class Default(Workflow):
       steps = ["configure", "build"]
       
       # Define environment variables with defaults
       source_dir = environment(Path.cwd())
       build_dir = environment(Path.cwd() / "build")
       install_dir = environment(Path.cwd() / "install")
       
       def configure(self, args):
           """Configure Build"""
           # Access environment variables as properties
           self.print(f"Source: {self.source_dir}")
           self.print(f"Build: {self.build_dir}")

Environment variables:

- Persist across workflow steps
- Can be overridden via command-line arguments
- Are stored in shell environment variables (prefixed with ``KESSEL_``)
- Support type conversion (Path, str, int, etc.)

.. note::
   Use ``self.print()`` instead of Python's ``print()`` for outputting
   messages. Python's ``print()`` writes directly to stdout and appears
   immediately, while ``self.print`` commands are queued and
   executed in the parent shell after the Kessel command completes. This is
   achieved by writing commands to a pipe during execution and then evaluating
   the pipe's contents when the command finishes.

Step Arguments
~~~~~~~~~~~~~~

Steps can accept command-line arguments by defining an ``<step>_args`` method:

.. code-block:: python

   class Default(Workflow):
       steps = ["build"]
       
       build_dir = environment(Path.cwd() / "build")
       
       def build_args(self, parser):
           parser.add_argument("-B", "--build-dir", default=self.build_dir)
           parser.add_argument("-j", "--jobs", type=int, default=4)
       
       def build(self, args):
           """Build Project"""
           # args contains parsed command-line arguments
           self.print(f"Building in {args.build_dir} with {args.jobs} jobs")

Collapsed Steps
~~~~~~~~~~~~~~~

Steps can be marked with the ``@collapsed`` decorator to indicate that their output should be collapsed in GitLab CI pipeline views:

.. code-block:: python

   from kessel.workflows import Workflow, collapsed

   class Default(Workflow):
       steps = ["env", "build"]
       
       @collapsed
       def env(self, args):
           """Setup Environment"""
           # This step's output will be collapsed in GitLab CI
           self.print("Setting up environment...")
       
       def build(self, args):
           """Build Project"""
           # This step's output will be shown expanded by default
           self.print("Building project...")

The ``@collapsed`` decorator only affects the presentation of step output in GitLab CI pipelines and does not change the step's behavior or execution.

Executing Shell Commands
~~~~~~~~~~~~~~~~~~~~~~~~

Workflows typically execute one or more shell commands either by using the
``exec`` method or by sourcing entire scripts via the ``source`` method.

In addition, a convenience object ``environ`` gives access to your shell's
environment variables as writable dictionary.

.. code-block:: python

   class Default(Workflow):
       steps = ["build"]
       
       def build(self, args):
           """Build Project"""
           # Source a shell script
           self.source(self.kessel_root / "libexec/kessel/workflows/cmake/build.sh")
           
           # Execute a shell command
           self.exec("make -j$(nproc)")
           
           # Set environment variable
           self.environ["MY_VAR"] = "value"

Built-in Workflow Classes
-------------------------

Kessel provides several built-in workflow base classes that implement common patterns.

CMake Workflow
~~~~~~~~~~~~~~

The ``CMake`` workflow class provides steps for CMake-based projects:

.. code-block:: python

   from kessel.workflows import Workflow
   from kessel.workflows.base.cmake import CMake

   class Default(CMake):
       steps = ["configure", "build", "test", "install"]

Available methods:

- ``configure(args, cmake_args=[])``: Configure CMake project
- ``build(args, cmake_args=[])``: Run CMake build
- ``test(args, ctest_args=[])``: Run CTest
- ``install(args)``: Install built artifacts
- ``define(arg, value)``: Helper to create CMake -D arguments

Environment variables:

- ``source_dir``: Source directory (defaults to current directory)
- ``build_dir``: Build directory (defaults to ``./build``)
- ``install_dir``: Installation directory (defaults to ``./build/install``)

Example with custom CMake arguments:

.. code-block:: python

   from kessel.workflows.base.cmake import CMake

   class Default(CMake):
       steps = ["configure", "build", "test", "install"]
       
       def configure(self, args):
           """Configure Project"""
           cmake_args = [
               self.define("CMAKE_BUILD_TYPE", "Release"),
               self.define("BUILD_TESTING", True),
               self.define("CMAKE_INSTALL_PREFIX", "/opt/myapp")
           ]
           # Call parent class method with custom arguments
           super().configure(args, cmake_args)

Spack Build Environment Workflow
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``BuildEnvironment`` workflow class integrates with Spack for dependency management:

.. code-block:: python

   from kessel.workflows.base.spack import BuildEnvironment
   from kessel.workflows.base.cmake import CMake

   class Default(BuildEnvironment, CMake):
       steps = ["env", "configure", "build", "test", "install"]
       
       # Spack configuration
       spack_env = environment("default")
       project_spec = environment("myproject@main")

Available methods:

- ``env(args)``: Prepare and activate Spack environment
- ``configure(args)``: Configure build system within Spack environment

Environment variables:

- ``spack_env``: Name of the Spack environment to use
- ``source_dir``: Project source directory
- ``build_dir``: Build directory
- ``install_dir``: Installation directory
- ``project_spec``: Spack spec for the project

Command-line arguments:

.. code-block:: console

   $ kessel step env -e my-env -S /path/to/source -B /path/to/build myproject@develop

Spack Deployment Workflow
~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``Deployment`` workflow class creates Spack deployments:

.. code-block:: python

   from kessel.workflows.base.spack import Deployment

   class Default(Deployment):
       steps = ["setup", "bootstrap", "mirror", "envs", "finalize"]
       
       # Spack configuration
       spack_url = "https://github.com/spack/spack.git"
       spack_ref = "v1.1.0"
       
       # Deployment options
       build_roots = False
       env_views = True
       git_mirrors = []
       mirror_exclude = ["cmake", "ninja"]
       build_exclude = ["llvm"]

Steps:

- ``setup(args)``: Initialize deployment structure
- ``bootstrap(args)``: Bootstrap Spack installation
- ``mirror(args)``: Create source mirrors
- ``envs(args)``: Build all environments
- ``finalize(args)``: Clean up and finalize deployment

Configuration options:

- ``spack_url``: Git URL for Spack repository
- ``spack_ref``: Git branch/tag/commit to use
- ``site_configs_url``: Git URL for site-specific configuration repository (optional)
- ``site_configs_ref``: Git branch/tag/commit for site configs (default: ``main``)
- ``build_roots``: Whether to build compiler toolchains
- ``env_views``: Whether to create environment views
- ``git_mirrors``: List of Git repositories to mirror
- ``mirror_exclude``: Packages to exclude from source mirror
- ``build_exclude``: Packages to exclude from builds

Using Workflows
---------------

Listing Workflows
~~~~~~~~~~~~~~~~~

List all available workflows in the current project:

.. code-block:: console

   $ kessel list

The active workflow is highlighted.

Activating a Workflow
~~~~~~~~~~~~~~~~~~~~~

Switch to a different workflow:

.. code-block:: console

   $ kessel activate release

The active workflow is stored in the ``KESSEL_WORKFLOW`` environment variable and persists for the current shell session.

Running Workflows
~~~~~~~~~~~~~~~~~

Run all steps in the active workflow:

.. code-block:: console

   $ kessel run

Run a specific step:

.. code-block:: console

   $ kessel step build

Pass arguments to a step:

.. code-block:: console

   $ kessel step build --build-dir /tmp/build --jobs 8

Viewing Workflow Status
~~~~~~~~~~~~~~~~~~~~~~~

Display the workflow progress:

.. code-block:: console

   $ kessel status

This shows a visual progress bar with completed and pending steps.

Editing Workflows
~~~~~~~~~~~~~~~~~

Open the active workflow in your editor:

.. code-block:: console

   $ kessel edit

This opens the workflow file using your ``$EDITOR``.

Workflow Examples
-----------------

Default CMake Workflow
~~~~~~~~~~~~~~~~~~~~~~

A simple CMake project workflow:

.. code-block:: python

   from kessel.workflows import Workflow, environment
   from kessel.workflows.base.cmake import CMake
   from pathlib import Path

   class Default(CMake):
       steps = ["configure", "build", "test", "install"]
       
       build_dir = environment(Path.cwd() / "build")
       build_type = environment("Release")
       
       def configure_args(self, parser):
           parser.add_argument("--build-type", default=self.build_type,
                             choices=["Debug", "Release", "RelWithDebInfo"])
       
       def configure(self, args):
           """Configure Project"""
           cmake_args = [
               self.define("CMAKE_BUILD_TYPE", args.build_type),
               self.define("BUILD_TESTING", True)
           ]
           # Call parent class method with custom arguments
           super().configure(args, cmake_args)

Spack + CMake Workflow
~~~~~~~~~~~~~~~~~~~~~~

A workflow that uses Spack for dependencies and CMake for building:

.. code-block:: python

   from kessel.workflows.base.spack import BuildEnvironment
   from kessel.workflows.base.cmake import CMake

   class Default(BuildEnvironment, CMake):
       steps = ["env", "configure", "build", "test", "install"]
       
       spack_env = environment("dev")
       project_spec = environment("myapp@main")

Usage:

.. code-block:: console

   $ kessel step env -e production
   $ kessel step configure
   $ kessel step build
   $ kessel step test

Multiple Workflows
~~~~~~~~~~~~~~~~~~

You can define multiple workflows for different purposes:

.. code-block::

   .kessel/workflows/
   ├── default.py
   └── format/
       ├── __init__.py
       └── requirements.txt

``.kessel/workflows/default.py`` for building:

.. code-block:: python

   from kessel.workflows import environment
   from kessel.workflows.base.spack import BuildEnvironment
   from kessel.workflows.base.cmake import CMake

   class Default(BuildEnvironment, CMake):
       steps = ["env", "configure", "build", "test"]

       spack_env = environment("dev")
       project_spec = environment("myapp@main")

``.kessel/workflows/format/__init__.py`` for code formatting:

.. code-block:: python

   from kessel.workflows import Workflow, environment
   from pathlib import Path

   class Format(Workflow):
       steps = ["format"]
       
       source_dir = environment(Path.cwd() / "src")
       
       def format(self, args):
           """Format Code"""
           self.exec(f"clang-format -i {self.source_dir}/**/*.cpp")
           self.exec(f"clang-format -i {self.source_dir}/**/*.hpp")

Switch between workflows:

.. code-block:: console

   $ kessel run  # Uses default workflow

   $ kessel activate format
   $ kessel run  # Runs clang-format

   $ kessel activate default
   $ kessel run  # Back to building

Private Workflows and Shared Modules
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Workflows and modules starting with underscore (``_``) are "private" - they can be imported by other workflows but won't appear in ``kessel list``. This is useful for:

- Shared base classes
- Utility modules
- Common functionality that shouldn't be run directly

Example structure:

.. code-block::

   .kessel/workflows/
   ├── _shared.py      # Private base class
   ├── _utils.py       # Private utility functions
   ├── workflow1.py    # Public workflow
   └── workflow2.py    # Public workflow

``.kessel/workflows/_shared.py`` (private):

.. code-block:: python

   from kessel.workflows import Workflow

   class Shared(Workflow):
       def validate(self, args):
           """Validate Configuration"""
           # Common validation logic
           pass

``.kessel/workflows/workflow1.py`` (public):

.. code-block:: python

   from kessel.workflows._shared import Shared

   class Workflow1(Shared):
       steps = ["validate", "build"]

       def build(self, args):
           """Build Project"""
           self.exec("make build")

When you run ``kessel list``, only ``workflow1`` and ``workflow2`` will be shown. The private modules ``_shared`` and ``_utils`` remain hidden but importable.

Custom Workflow with External Tools
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A workflow that integrates custom tools:

.. code-block:: python

   from kessel.workflows import Workflow
   from pathlib import Path

   class Default(Workflow):
       steps = ["format", "lint", "build", "test", "docs"]
       
       source_dir = environment(Path.cwd())
       
       def format(self, args):
           """Format Code"""
           self.exec(f"clang-format -i {self.source_dir}/**/*.cpp")
       
       def lint(self, args):
           """Run Linter"""
           self.exec(f"clang-tidy {self.source_dir}/**/*.cpp")
       
       def build(self, args):
           """Build Project"""
           self.exec("cmake --build build")
       
       def test(self, args):
           """Run Tests"""
           self.exec("ctest --test-dir build")
       
       def docs(self, args):
           """Generate Documentation"""
           self.exec("doxygen Doxyfile")

Advanced Topics
---------------

Dynamic Step Execution
~~~~~~~~~~~~~~~~~~~~~~

Workflows can conditionally execute steps based on runtime conditions:

.. code-block:: python

   import os
   from kessel.workflows import Workflow

   class Default(Workflow):
       steps = ["test"]
       
       def test(self, args):
           """Run Tests"""
           if os.environ.get("CI") == "true":
               # Run full test suite in CI
               self.exec("ctest --output-on-failure")
           else:
               # Run quick tests locally
               self.exec("ctest -L quick")

CI/CD Integration
~~~~~~~~~~~~~~~~~

When running ``kessel run`` in a GitLab CI pipeline, a highlighted message is displayed at the beginning showing how to reproduce the CI job execution on the same system. The ``ci_message()`` method generates the content of this message.

The message typically includes steps such as:

1. SSH to the system where the CI job is running
2. Change to a project checkout directory
3. Run pre-allocation initialization commands (specified in ``pre_alloc_init``)
4. Allocate a compute node with the batch system (if applicable)
5. Run post-allocation commands on the compute node (specified in ``post_alloc_init``)
6. Execute the kessel command with all its arguments

The ``default_ci_message()`` helper function provides a useful default implementation, and the ``BuildEnvironment`` class offers a simplified interface:

.. code-block:: python

   from kessel.workflows.base.spack import BuildEnvironment

   class Default(BuildEnvironment):
       steps = ["env", "build"]
       
       def ci_message(self, parsed_args, pre_alloc_init="", post_alloc_init=""):
           # Customize the CI reproduction instructions
           return super().ci_message(
               parsed_args, 
               pre_alloc_init="module load python",
               post_alloc_init="export MY_VAR=value"
           )

This helps developers reproduce CI runs by providing the exact commands a GitLab runner would execute on that system.

Best Practices
--------------

1. **Use descriptive step names**: Choose clear, action-oriented names like ``configure``, ``build``, ``test``
2. **Write clear docstrings**: The first line becomes the step title in status displays
3. **Leverage environment variables**: Use them for paths and configuration that persist across steps
4. **Provide command-line arguments**: Allow users to override defaults without editing workflow files
5. **Use built-in workflow classes**: Inherit from ``CMake``, ``BuildEnvironment``, etc. for common patterns
6. **Keep workflows simple**: Complex logic should go in shell scripts, not Python
7. **Test workflows locally**: Use ``--shell-debug`` to verify commands before execution
8. **Document custom workflows**: Add comments explaining non-obvious configuration
9. **Use self.print for output**: Don't use ``print()`` - it bypasses the shell execution queue

Troubleshooting
---------------

Workflow Not Found
~~~~~~~~~~~~~~~~~~

If Kessel can't find a workflow:

1. Verify the workflow file exists in ``.kessel/workflows/``
2. Check for either ``<name>.py``, ``<name>/__init__.py``, or ``<name>/workflow.py`` (legacy)
3. Ensure the class name matches the workflow name (capitalized)

.. code-block:: console

   $ ls .kessel/workflows/
   $ cat .kessel/workflows/default.py

Step Fails
~~~~~~~~~~

If a step fails:

1. Use ``--shell-debug`` to see the commands being executed
2. Check environment variables with ``env | grep KESSEL``
3. Run the step in isolation to identify the issue

.. code-block:: console

   $ kessel --shell-debug step build

Reset and Retry
~~~~~~~~~~~~~~~

To reset workflow state and start over:

.. code-block:: console

   $ kessel reset
   $ kessel run
