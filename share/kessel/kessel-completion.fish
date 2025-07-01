# Autocomplete variables
set -l kessel_not_follow "list create init activate system env bootstrap mirror clean finalize pipeline run"
set -l kessel_subcommands "init activate system env bootstrap mirror clean finalize pipeline run"
set -l kessel_subcommands_dir "init activate"

# Commands that admit other commands
set -l kessel_sys_env "system env"
set -l kessel_sys_env_sub "list activate"
set -l kessel_bstr_mirr "bootstrap mirror"
set -l kessel_bstr_mirr_sub "create"
set -l kessel_pipeline "pipeline"
set -l kessel_pipeline_sub "setup env configure build test install submit"
set -l kessel_run "run"
set -l kessel_run_sub "-e --env -s --system"

# Remove file autocompletion
complete -c kessel -f

# Add "help" autocompletion
complete -c kessel -s h
complete -c kessel -l help

# Add autocompletion for kessel_subcommands (without description)
complete -c kessel -n \
    "not __fish_seen_subcommand_from $kessel_not_follow" -a $kessel_subcommands

# If it is one of the commands that require a secondary sub-command, autocomplete
complete -c kessel -n \
    "__fish_seen_subcommand_from $kessel_sys_env &&\
    not __fish_seen_subcommand_from $kessel_sys_env_sub" -a $kessel_sys_env_sub
complete -c kessel -n \
    "__fish_seen_subcommand_from $kessel_bstr_mirr &&\
    not __fish_seen_subcommand_from $kessel_bstr_mirr_sub" -a $kessel_bstr_mirr_sub
complete -c kessel -n \
    "__fish_seen_subcommand_from $kessel_pipeline &&\
    not __fish_seen_subcommand_from $kessel_pipeline_sub" -a $kessel_pipeline_sub
complete -c kessel -n \
    "__fish_seen_subcommand_from $kessel_run &&\
    not __fish_seen_subcommand_from $kessel_run_sub" -a $kessel_run_sub
complete -c kessel -n \
    "__fish_seen_subcommand_from -e --env" -a "$(spack env list)"

# If it is one of the commands that require a directory, re-enable file
# autocompletion and request the file name
complete -c kessel -n \
    "__fish_seen_subcommand_from $kessel_subcommands_dir" -Fr
