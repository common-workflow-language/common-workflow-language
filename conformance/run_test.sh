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

runtest() {
    echo "--- Running $1 tests ---"

    echo " [draft 1]"
    runs=$((runs+1))
    ./conformance_test.py --test conformance_test_draft1.json --basedir draft-1 $1
    checkexit

    echo " [draft 2]"
    runs=$((runs+1))
    ./conformance_test.py --test conformance_test_draft2.json --basedir draft-2 $1
    checkexit
}

# Add your tool test here.
for t in "$CWLTOOL/cwltool/main.py" "$RABIX/rabix/cliche/main.py" ; do
    if [[ -x "$t" ]]; then
        runtest "$t"
    fi
done

# Final reporting

echo

if [[ $failures != 0 ]]; then
    echo "$failures tool tests failed"
else
    if [[ $runs == 0 ]]; then
        echo >&2 "$helpmessage"
        echo >&2
        exit 1
    else
        echo "All tool tests succeeded"
    fi
fi

exit $failures
