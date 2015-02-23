#!/bin/bash

read -rd "\000" helpmessage <<EOF
$(basename $0): Run common workflow tool description language conformance tests.

Syntax:
        $(basename $0) [CWLTOOL=/path/to/cwltool] [RABIX=/path/to/rabix]

Options:
EOF

while [[ -n "$1" ]]
do
    arg="$1"; shift
    case "$arg" in
        --help)
            echo >&2 "$helpmessage"
            echo >&2
            exit 1
            ;;
        *=*)
            eval $(echo $arg | cut -d= -f1)=\"$(echo $arg | cut -d= -f2-)\"
            ;;
    esac
done

runs=0
failures=0

checkexit() {
    if [[ "$?" != "0" ]]; then
        failures=$((failures+1))
    fi
}

DRAFT2="./conformance_test.py --test conformance_test_draft2.json --basedir draft-2"

# cwltool conformance test
if [[ -n "$CWLTOOL" ]]; then
    echo
    echo "--- Running cwltool tests ---"
    $DRAFT2 $CWLTOOL/cwltool/main.py
    runs=$((runs+1))
    checkexit
fi

# rabix conformance test
if [[ -n "$RABIX" ]]; then
    echo
    echo "--- Running rabix/cliche tests ---"
    $DRAFT2 $RABIX/rabix/cliche/main.py
    runs=$((runs+1))
    checkexit
fi

# Add your tool test here.



# Final reporting

echo

if [[ $failures != 0 ]]; then
    echo "$failures tool tests failed"
else
    if [[ $runs == 0 ]]; then
        echo "Usage: run_tests.sh [CWLTOOL=path] [RABIX=path]"
    else
        echo "All tool tests succeeded"
    fi
fi

exit $failures
