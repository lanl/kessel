set -l PARENT_DIR $(dirname (status current-filename))
set -x KESSEL_ROOT $(realpath $PARENT_DIR/../..)
set -x KESSEL_CONFIG_DIR $KESSEL_ROOT/etc/kessel

function kessel
    eval "$(command kessel $argv 3>&1 >&4 4>&- )"
end 4>&1

fish_add_path -p --path $KESSEL_ROOT/bin

# Set up autocomplete

# Autocomplete variables
set -l kessel_subcommands "init"
set -l kessel_subcommands_dir "init"

# Remove file autocompletion
complete -c kessel -f

# Add autocompletion for kessel_subcommands
complete -c kessel -n \
    "not __fish_seen_subcommand_from $kessel_subcommands" -a $kessel_subcommands

# If it is one of the commands that require a directory, re-enable file
# autocompletion and request the file name
complete -c kessel -n \
    "__fish_seen_subcommand_from $kessel_subcommands_dir" -Fr
