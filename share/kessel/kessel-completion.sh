_kessel() {
    # Variables
    local cur prev opts pipeline_opts

    # Autocomplete variables
    opts="-h init activate system env bootstrap mirror clean finalize pipeline run"
    pipeline_opts="setup env configure build test install submit"
    run_opts="-s --system -e --env"

    # Create empty COMPREPLY
    COMPREPLY=()

    # Current word
    cur="${COMP_WORDS[COMP_CWORD]}"

    # Previous word (COMP_CWORD is an integer!)
    prev="${COMP_WORDS[COMP_CWORD - 1]}"

    # Remove default completion
    compopt +o default

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
            compopt -o default
            COMPREPLY=()
            ;;
        activate)
            compopt -o default
            COMPREPLY=()
            ;;
        system)
            COMPREPLY=($(compgen -W "list activate" -- ${cur}))
            ;;
        env)
            COMPREPLY=($(compgen -W "list activate" -- ${cur}))
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
        run)
            COMPREPLY=($(compgen -W "${run_opts}" -- ${cur}))
            ;;
        *)
            COMPREPLY=($(compgen -W "${run_opts}" -- ${cur}))
            ;;
        esac
        ;;
    # Compounded commands
    *)
        case ${prev} in
        -e | --env)
            COMPREPLY=($(compgen -W "$(spack env list)" -- ${cur}))
            ;;
        -s | --system)
            COMPREPLY=($(compgen -W "local" -- ${cur}))
            ;;
        *)
            COMPREPLY=($(compgen -W "${run_opts}" -- ${cur}))
            ;;
        esac
        ;;
    esac
}

complete -F _kessel kessel
