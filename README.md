# Kessel

Kessel is a tool to **create and drive continuous integration (CI) and developer
workflows** through a unified interface across multiple code projects and
environments.

It serves as a driver and integration layer for build systems and package
managers such as CMake and Spack, providing a flexible library of reusable
shell scripts to build and execute complex workflows consistently.

Modern developer and CI pipelines often need to run multi-step processes, such
as setting up environments, generating and configuring build systems, compiling
and testing software, or deploying dependencies. Kessel streamlines these
workflows by defining them in a consistent, composable way that works for both
**interactive development** and **automated pipelines**.

A key goal of Kessel is to **bridge the gap between YAML-based CI definitions and
developer command-line workflows**. By offering a common abstraction for running
sequences of steps, it reduces redundancy, simplifies maintenance, and ensures
alignment between what developers do locally and what CI executes remotely.

As part of its adoption, Kessel-based Spack deployment workflows have
established a **baseline Spack configuration for LANL and LLNL systems**, enabling
a shared foundation for software deployment and development across multiple
code teams.