# Autocomplete variables
set -l kessel_subcommands "init"
set -l kessel_subcommands_dir "init"

# Remove file autocompletion
complete -c kessel -f

# Add autocompletion for kessel_subcommands (without description)
complete -c kessel -n \
    "not __fish_seen_subcommand_from $kessel_subcommands" -a $kessel_subcommands

# If it is one of the commands that require a directory, re-enable file
# autocompletion and request the file name
complete -c kessel -n \
    "__fish_seen_subcommand_from $kessel_subcommands_dir" -Fr
