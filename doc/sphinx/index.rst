Kessel Documentation
====================

Kessel is a workflow orchestration tool designed to **create and drive continuous integration (CI) and developer workflows** through a unified interface across multiple code projects and environments.

It serves as a driver and integration layer for build systems and package managers, providing a flexible library of reusable components to build and execute complex processes consistently.

Key Features
------------

**Unified Workflows**
  Define workflows once and use them in both development and CI environments. Kessel bridges the gap between CI definitions and developer command-line workflows.

**Multi-System Support**
  Create deployments and workflows that work across different HPC systems, development workstations, and CI runners.

**Spack Integration**
  First-class support for Spack-based dependency management, including deployment creation, environment management, and offline builds.

**Flexible & Extensible**
  Built-in workflows with easy customization through Python classes and environment variables.

**Shell Execution Model**
  Commands are executed in the parent shell, preserving environment changes across workflow steps.

Quick Example
-------------

Initialize a project with a workflow:

.. code-block:: console

   $ cd my-project
   $ kessel init --template spack-project
   $ kessel run

Define a custom workflow in ``.kessel/workflows/default.py``:

.. code-block:: python

   from kessel.workflows.base.spack import BuildEnvironment
   from kessel.workflows.base.cmake import CMake

   class Default(BuildEnvironment, CMake):
       steps = ["env", "configure", "build", "test"]
       
       spack_env = environment("dev")
       project_spec = environment("myapp@main")

Run the workflow:

.. code-block:: console

   $ kessel run              # Run all steps
   $ kessel step build       # Run a single step
   $ kessel status           # Check progress

Core Concepts
-------------

**Workflows**
  Python classes that define a sequence of steps for building, testing, or deploying software. Each workflow can have configurable environment variables and command-line arguments.

**Steps**
  Individual units of work (e.g., configure, build, test) that execute shell commands or scripts. Steps maintain state and can be run individually or as part of the complete workflow.

**Deployments**
  Complete, self-contained Spack installations with pre-built software environments for specific systems. Deployments enable offline builds and consistent software stacks.

**Configuration Scopes**
  Layered Spack configuration system that combines global, system, project, and environment-specific settings for flexible package management.

Use Cases
---------

**Development Workflows**
  Streamline daily development tasks with consistent commands for configuring, building, and testing code across different environments.

**CI/CD Pipelines**
  Use the same workflows in GitLab CI, GitHub Actions, or other CI systems that developers use locally, reducing maintenance and ensuring consistency.

**HPC System Deployments**
  Create standardized Spack deployments for multiple HPC systems from a single configuration, with offline build capability.

**Multi-Project Coordination**
  Share common workflows and deployments across multiple related projects, establishing baseline configurations for teams.

Getting Started
---------------

New to Kessel? Start with the :doc:`quickstart` guide to get up and running quickly.

Prefer hands-on learning? Follow our step-by-step tutorials:

- :doc:`tutorial/cmake` - Add Kessel to a CMake project
- :doc:`tutorial/spack` - Integrate Spack for dependency management
- :doc:`tutorial/deployment` - Create and use Spack deployments

Want to understand workflows? See :doc:`workflows` for detailed information on creating and using workflows.

Need to create Spack deployments? Check out :doc:`deployments` for comprehensive deployment documentation.

----

*This documentation was created with the assistance of Claude (Anthropic).*


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   quickstart
   workflows
   deployments
   cli_reference

.. toctree::
   :maxdepth: 2
   :caption: Tutorials:

   tutorial/cmake
   tutorial/spack
   tutorial/deployment
