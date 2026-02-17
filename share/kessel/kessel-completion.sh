# © 2026. Triad National Security, LLC. All rights reserved.
# This program was produced under U.S. Government contract 89233218CNA000001
# for Los Alamos National Laboratory (LANL), which is operated by Triad
# National Security, LLC for the U.S.  Department of Energy/National Nuclear
# Security Administration. All rights in the program are reserved by Triad
# National Security, LLC, and the U.S. Department of Energy/National Nuclear
# Security Administration. The Government is granted for itself and others
# acting on its behalf a nonexclusive, paid-up, irrevocable worldwide license
# in this material to reproduce, prepare derivative works, distribute copies to
# the public, perform publicly and display publicly, and to permit others to do
# so.

_kessel() {
    # Variables
    local cur prev opts pipeline_opts

    # Keep track of whether we are in bash
    local is_bash
    if [[ $0 == "bash" ]]; then
        is_bash=true
    fi

    # Autocomplete variables
    opts="-h --shell-debug --version init deploy build-env step run reset list activate status edit"
    deploy_opts="activate replicate"

    # Create empty COMPREPLY
    COMPREPLY=()

    # Current word
    cur="${COMP_WORDS[COMP_CWORD]}"

    # Previous word (COMP_CWORD is an integer!)
    prev="${COMP_WORDS[COMP_CWORD - 1]}"

    # Remove default completion
    # use "compopt" only if we are in bash
    if [[ $is_bash ]]; then
        compopt +o default
    fi

    # Do sub-command
    case ${COMP_CWORD} in
    # Complete for any command
    1)
        COMPREPLY=($(compgen -W "${opts}" -- ${cur}))
        ;;
    # Commands that require additional arguments
    2)
        case ${prev} in
        # Complete with filenames (as is the default)
        init)
            COMPREPLY=($(compgen -W "$(ls)" -- ${cur}))

            # Use the bash default if we are in bash
            if [[ $is_bash ]]; then
                compopt -o default
                COMPREPLY=()
            fi
            ;;
        deploy)
            COMPREPLY=($(compgen -W "${deploy_opts}" -- ${cur}))
            ;;
        activate)
            COMPREPLY=($(compgen -W "$(kessel list)" -- ${cur}))
            ;;
        esac
        ;;

    *)
        # Other words in command
        second=${COMP_WORDS[1]}
        third=${COMP_WORDS[2]}

        case ${second} in
        deploy)
            case ${third} in
            activate)
                COMPREPLY=($(compgen -W "$(ls)" -- ${cur}))
                if [[ $is_bash ]]; then
                    compopt -o default
                    COMPREPLY=()
                fi
                ;;
            esac
            ;;
        esac
        ;;
    esac
}

if command -v complete > /dev/null 2>/dev/null; then
  complete -F _kessel kessel
fi
