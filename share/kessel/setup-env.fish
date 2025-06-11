set -l PARENT_DIR $(dirname (status current-filename))
set -x KESSEL_ROOT $(realpath $PARENT_DIR/../..)
set -x KESSEL_CONFIG_DIR $KESSEL_ROOT/etc/kessel

function kessel
    eval "$(command kessel $argv 3>&1 >&4 4>&- )"
end 4>&1

fish_add_path -p --path $KESSEL_ROOT/bin

# Set up autocomplete
source $KESSEL_ROOT/share/kessel/kessel-completion.fish
