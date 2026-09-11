devpod-down *args:
    devpod down . {{args}}

devpod-ssh *args:
    ssh gitbare.devpod {{args}}

devpod-up *args:
    devpod up . --ide none {{args}}

pre-commit:
    pre-commit run --all-files

setup:
    bin/check-requirements
    pre-commit install
    pre-commit install-hooks
