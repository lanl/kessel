set -l PARENT_DIR (dirname (status current-filename))
set -x KESSEL_ROOT (realpath $PARENT_DIR/../..)
set -x KESSEL_CONFIG_DIR $KESSEL_ROOT/etc/kessel
set -x IN_FISH true

function kessel
    # Create safe temp files for the evaluation of kessel
    set -f kessel_commands (mktemp -p $KESSEL_ROOT/share/kessel/.tmp)
    set -f kessel_output (mktemp -p $KESSEL_ROOT/share/kessel/.tmp)

    eval (command kessel $argv 3>$kessel_commands >$kessel_output)

    cat $kessel_output
    source $kessel_commands

    rm $kessel_commands
    rm $kessel_output
end

fish_add_path -p --path $KESSEL_ROOT/bin

# Set up autocomplete
source $KESSEL_ROOT/share/kessel/kessel-completion.fish
