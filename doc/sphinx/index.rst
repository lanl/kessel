Kessel documentation
====================

Kessel is a tool that helps bring together various components that make up the
build and testing pipeline of a code project. It was primarily developed with
Spack-based workflows in mind, but eventually evolved into a more generic
utility.

Its main goal is to bridge the gap between what happens in continuous
integration pipelines and what happens locally yon a developer workstation or
HPC system. We want to minimize the delta of what developers need to type on
either of them.

Developer Workflows
-------------------

At its core, Kessel is a wrapper around shell scripts used to drive developer
workflows. Such workflows consist of multiple steps that need to be executed in
sequence to achieve some result. Kessel defines workflows as folders of scripts
placed in ``.kessel/workflows``. Each step is contained within a shell script
whose name is prefixed with a sequeunce number.

.. code-block::
   
   .kessel
   └── workflows
       └── default
           ├── 0_init
           ├── 1_setup
           ├── 2_env
           ├── 3_configure
           ├── 4_build
           ├── 5_test
           └── 6_install

The above defines a ``default`` workflow with 6 steps. The 0th script is a
special initialization script that sets up the environment context for the
workflow, such as default settings for the subsequence steps. With the
following command:

.. code-block::

   kessel run

the entire workflow will be executed within the active user shell. Each step of
the workflow can also be executed individually via the ``kessel step <name>``
command. ``kessel run`` therefore is equivalent to running the following step
commands:

.. code-block::

   kessel step setup
   kessel step env
   kessel step configure
   kessel step build
   kessel step test
   kessel step install

While developers are free to define their own scripts for each step, Kessel
provides a library of reusable scripts that implement common workflow patterns.

Deployments
-----------

A deployment is an aggregation of build environments that are prebuilt for use
in workflows.


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   quickstart
   workflows
   deployments
