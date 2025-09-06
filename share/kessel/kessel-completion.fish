function __seen_in_position
    set -l cmd (commandline -poc)
    set -e cmd[1]

    if not set -q cmd[$argv[1]]
        return 1
    end

    return (test $cmd[$argv[1]] = $argv[2])
end

function __total_numer_args
    set -l cmd (commandline -poc)
    set -e cmd[1]

    return (test (count $cmd) = $argv[1])
end

# Autocomplete variables
set -l kessel_commands "init activate snapshot system env bootstrap mirror clean finalize workflow pipeline"
set -l snapshot_commands "create restore"
set -l system_commands "list activate"
set -l env_commands "list activate"
set -l bootstrap_commands create
set -l mirror_commands create
set -l workflow_commands "list activate status get"
set -l pipeline_commands "status"

# Remove file autocompletion
complete -c kessel -f

# Add "help" autocompletion
complete -c kessel -s h
complete -c kessel -l help

# Add autocompletion for kessel_subcommands (without description)
complete -c kessel -n \
    "not __fish_seen_subcommand_from $kessel_commands" -a $kessel_commands

# Add subcommands that need a path
complete -c kessel -n "__seen_in_position 1 init" -Fr
complete -c kessel -n "__seen_in_position 1 activate" -F

complete -c kessel -n "__fish_seen_subcommand_from snapshot &&\
    not __fish_seen_subcommand_from $snapshot_commands" -a $snapshot_commands
complete -c kessel -n "__fish_seen_subcommand_from snapshot &&\
    __fish_seen_subcommand_from $snapshot_commands" -Fr

complete -c kessel -n "__fish_seen_subcommand_from system &&\
    not __fish_seen_subcommand_from $system_commands" -a $system_commands
complete -c kessel -n "__fish_seen_subcommand_from system &&\
    __fish_seen_subcommand_from activate &&\
    __total_numer_args 2" -a "$(kessel system list)"

complete -c kessel -n "__fish_seen_subcommand_from env &&\
    not __fish_seen_subcommand_from $env_commands" -a $env_commands
complete -c kessel -n "__fish_seen_subcommand_from env &&\
    __fish_seen_subcommand_from activate &&\
    __total_numer_args 2" -a "$(spack env list)"

complete -c kessel -n "__fish_seen_subcommand_from bootstrap &&\
    not __fish_seen_subcommand_from $bootstrap_commands" -a $bootstrap_commands

complete -c kessel -n "__fish_seen_subcommand_from mirror &&\
    not __fish_seen_subcommand_from $mirror_commands" -a $mirror_commands

complete -c kessel -n "__fish_seen_subcommand_from workflow &&\
    not __fish_seen_subcommand_from $workflow_commands" -a $workflow_commands

complete -c kessel -n "__fish_seen_subcommand_from workflow &&\
    __fish_seen_subcommand_from activate &&\
    __total_numer_args 2" -a "$(kessel workflow list)"

complete -c kessel -n "__fish_seen_subcommand_from pipeline &&\
    not __fish_seen_subcommand_from $pipeline_commands" -a $pipeline_commands
