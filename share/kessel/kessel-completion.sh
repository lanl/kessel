_kessel() {
    # Variables
    local cur prev opts pipeline_opts

    # Keep track of whether we are in bash
    local is_bash
    if [[ $0 == "bash" ]]; then
        is_bash=true
    fi

    # Autocomplete variables
    opts="-h init activate snapshot system env bootstrap mirror clean finalize workflow pipeline"
    pipeline_opts="_setup status"
    system_opts="list activate"
    env_opts="list activate"
    snapshot_opts="create restore"
    workflow_opts="list activate status get"

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
        activate)
            COMPREPLY=($(compgen -W "$(ls)" -- ${cur}))
            if [[ $is_bash ]]; then
                compopt -o default
                COMPREPLY=()
            fi
            ;;
        snapshot)
            COMPREPLY=($(compgen -W "${snapshot_opts}" -- ${cur}))
            ;;
        system)
            COMPREPLY=($(compgen -W "${system_opts}" -- ${cur}))
            ;;
        env)
            COMPREPLY=($(compgen -W "${env_opts}" -- ${cur}))
            ;;
        bootstrap)
            COMPREPLY=($(compgen -W "create" -- ${cur}))
            ;;
        mirror)
            COMPREPLY=($(compgen -W "create" -- ${cur}))
            ;;
        pipeline)
            COMPREPLY=($(compgen -W "${pipeline_opts}" -- ${cur}))
            ;;
        workflow)
            COMPREPLY=($(compgen -W "${workflow_opts}" -- ${cur}))
            ;;
        esac
        ;;
    # Compounded commands
    3)
        # Other words in command
        second=${COMP_WORDS[1]}

        case ${second} in
        snapshot)
            COMPREPLY=($(compgen -W "$(ls)" -- ${cur}))
            if [[ $is_bash ]]; then
                compopt -o default
                COMPREPLY=()
            fi
            ;;
        system)
            case ${prev} in
            activate)
                COMPREPLY=($(compgen -W "$(kessel system list)" -- ${cur}))
                ;;
            esac
            ;;
        env)
            case ${prev} in
            activate)
                COMPREPLY=($(compgen -W "$(kessel env list)" -- ${cur}))
                ;;
            esac
            ;;
        workflow)
            case ${prev} in
            activate)
                COMPREPLY=($(compgen -W "$(kessel workflow list)" -- ${cur}))
                ;;
            esac
            ;;
        esac
        ;;
    *)
        # Other words in command
        second=${COMP_WORDS[1]}
        third=${COMP_WORDS[2]}

        case ${second} in
        snapshot)
            case ${third} in
            create)
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

complete -F _kessel kessel
