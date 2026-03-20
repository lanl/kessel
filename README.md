![logo](doc/sphinx/_static/images/kessel.svg)

Kessel is a tool to create and drive continuous integration (CI) and developer
workflows through a unified interface across multiple code projects and
environments.

It serves as a driver and integration layer for build systems and package
managers, providing a flexible library of reusable components to build and
execute complex workflows consistently.

![kessel_demo](https://github.com/user-attachments/assets/c4c67a8b-0417-499f-a3e8-602d4bcd3433)

## Documentation

📚 **[Full Documentation](https://lanl.github.io/kessel)**

## Quick Start

### Installation

```bash
git clone https://github.com/lanl/kessel
cd kessel
source share/kessel/setup-env.sh
```

### Initialize a Project

```bash
cd your-project
kessel init
kessel run
```

### Create a Spack Deployment

```bash
mkdir my-deployment
cd my-deployment
kessel init --template spack-deployment
kessel run ubuntu24.04
```

## Key Features

- **Unified Workflows**: Define once, use in both development and CI
- **Multi-System Support**: Works across HPC systems, workstations, and CI runners
- **Spack Integration**: First-class support for Spack deployments and environments
- **Flexible & Extensible**: Built-in workflows with easy customization

## Overview

Modern developer and CI pipelines often need to run multi-step processes, such
as setting up environments, generating and configuring build systems, compiling
and testing software, or deploying dependencies. Kessel streamlines these
workflows by defining them in a consistent, composable way that works for both
**interactive development** and **automated pipelines**.

A key goal of Kessel is to bridge the gap between CI pipeline definitions and
developer command-line workflows. By offering a common abstraction for running
sequences of steps, it reduces redundancy, simplifies maintenance, and ensures
alignment between what developers do locally and what CI executes remotely.

As part of its adoption, Kessel-based deployment workflows have established a
baseline dependency configuration for commonly used HPC systems, enabling a
shared foundation for software deployment and development across multiple code
teams.

## Learn More

For detailed documentation, see:

- [Quickstart Guide](https://lanl.github.io/kessel/quickstart.html)
- [Workflows](https://lanl.github.io/kessel/workflows.html)
- [Deployments](https://lanl.github.io/kessel/deployments.html)
- [CLI Reference](https://lanl.github.io/kessel/cli_reference.html)

## Developers

- Richard Berger, CAI-1 (rberger@lanl.gov)
- Andres Yague Lopez, CAI-1 (ayaguelopez@lanl.gov)

## Acknowledgements

This project was orignally started in support of the following LANL ASC projects:

- FleCSI
- XCAP
- IC DevOps

Special thanks go to Davis Herring for encouraging the project's inception,
proposing the project's name, and constructive critique that helped shape the
direction of the project into its current form.

This research used the LANL AI Portal and resources provided by the Information
Technology (IT) Division at Los Alamos National Laboratory (Supported by the
U.S. Department of Energy, National Nuclear Security Administration under
Contract No. 89233218CNA000001).

# Release

This software has been approved for open source release and has been assigned
O5070 by the Feynman Center for Innovation at Los Alamos National Laboratory.

# Copyright

© 2026. Triad National Security, LLC. All rights reserved.
This program was produced under U.S. Government contract 89233218CNA000001 for
Los Alamos National Laboratory (LANL), which is operated by Triad National
Security, LLC for the U.S.  Department of Energy/National Nuclear Security
Administration. All rights in the program are reserved by Triad National
Security, LLC, and the U.S. Department of Energy/National Nuclear Security
Administration. The Government is granted for itself and others acting on its
behalf a nonexclusive, paid-up, irrevocable worldwide license in this material
to reproduce, prepare derivative works, distribute copies to the public,
perform publicly and display publicly, and to permit others to do so.
