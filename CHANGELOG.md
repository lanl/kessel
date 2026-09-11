# Changelog

## Unreleased

### CI/CD
- Add `workflows/base/spack/deployment/use.sh` with reusable
  `kessel_detect_system`, `kessel_activate_deployment` and `kessel_alloc`
  helpers, so projects no longer copy the system-detection, clone-or-activate and
  node-allocation logic into their `.gitlab/kessel.sh`. The spack-project
  template now sources these from the deployment's kessel, and the deployment's
  `activate.sh` sources them too so they are available in any activated
  environment.
- Add `workflows/base/spack/deployment/alloc-init.sh`, the wrapper `kessel_alloc`
  hands to the scheduler to activate the deployment on an allocated node.
- Add a `--persist PATH` option (via `kessel_parse_persist`) to the deployment
  entry-point scripts, so users can create a reusable writable deployment without
  having to know about the `KESSEL_WORKFLOW_DEPLOYMENT` environment variable.

### Workflows
- Add an optional `alloc` parameter to `default_ci_message` (and
  `BuildEnvironment.ci_message`) to override the allocation line.

## 0.3.0

### Spack Integration
- Add workaround for Spack changing how configuration scopes are overriden.
  See https://github.com/spack/spack/issues/52016. This adds a requirement to
  Spack develop-2026-03-01 or newer.
- Fix spack includes operating differently (#2)
- Fix handling of empty root specs in spack (#11)
- Preserve misc and python cache during spack finalize (#10)

### Build Environment
- Add `kessel build-env --inplace` option (#18)
- Add option to disable tests in build_environment workflow (#12)
- Only update user build cache index when explicitly requested
- Fix how KESSEL_ENABLE_VIEW is set (#6)

### Mirrors and Deployments
- Add metadata for local mirror support (#16)
- Default to mirroring private packages in deployments
- Fix spack deployments finalize when using padding (#5)
- Propagate environment step errors in spack deployments

### Workflows
- Improve error handling and early exits in workflows (#8)
- Consolidate base workflow files (#1)

### CI/CD
- Enable CI PR checks (#3)

## 0.2.0
- first public release
