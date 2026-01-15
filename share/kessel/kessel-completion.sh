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
