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
set -l kessel_commands "init deploy build-env step run reset list activate status edit"
set -l deploy_commands "activate replicate"

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
complete -c kessel -n "__seen_in_position 1 activate" -a "$(kessel list)"

complete -c kessel -n "__fish_seen_subcommand_from deploy &&\
    not __fish_seen_subcommand_from $deploy_commands" -a $deploy_commands
