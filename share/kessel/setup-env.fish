set -l PARENT_DIR $(dirname (status current-filename))
set -x KESSEL_ROOT $(realpath $PARENT_DIR/../..)
set -x KESSEL_CONFIG_DIR $KESSEL_ROOT/etc/kessel
set -x IN_FISH true

function kessel
    eval (command kessel $argv 3>/tmp/kessel_commands >/tmp/kessel_output)
    cat /tmp/kessel_output
    source /tmp/kessel_commands
end

fish_add_path -p --path $KESSEL_ROOT/bin

# Set up autocomplete
source $KESSEL_ROOT/share/kessel/kessel-completion.fish
