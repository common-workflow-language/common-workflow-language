#!/bin/bash

read -rd "\000" helpmessage <<EOF
$(basename $0): Run common workflow tool description language conformance tests.

Syntax:
        $(basename $0) [RUNNER=/path/to/cwl-runner] [DRAFT=cwl-draft-version]
                       [EXTRA=--optional-arguments-to-cwl-runner]

Options:
  -nT                   Run a specific test.
  -l                    List tests
  -jJ                   Specifies the number of tests to run simultaneously
                        (defaults to one).
  --only-tools          Only test CommandLineTools
  --junit-xml=FILENAME  Store results in JUnit XML format using the given
                        FILENAME
  --classname=CLASSNAME In the JUnit XML, tag the results with the given
                        CLASSNAME
  --verbose             Print the cwltest invocation and pass --verbose to
                        cwltest
  --self                Test CWL and test .cwl files themselves. If this flag
                        is given, any other flags will be ignored.

Note:
  EXTRA is useful for passing --enable-dev to the CWL reference runner:
  Example: RUNNER=cwltool EXTRA=--enable-dev
EOF

DRAFT=v1.0
TEST_N=""
JUNIT_XML=""
RUNNER=cwl-runner
PLATFORM=$(uname -s)
COVERAGE="python"
EXTRA=""
CLASS=""
VERBOSE=""
SELF=""

while [[ -n "$1" ]]
do
    arg="$1"; shift
    case "$arg" in
        --help)
            echo >&2 "$helpmessage"
            echo >&2
            exit 1
            ;;
        -n*)
            TEST_N=$arg
            ;;
        -j*)
            TEST_J=$arg
            ;;
        -l)
            TEST_L=-l
            ;;
        --only-tools)
            ONLY_TOOLS=$arg
            ;;
        --junit-xml=*)
            JUNIT_XML=$arg
            ;;
        --classname=*)
            CLASS=$arg
            ;;
        --verbose)
            VERBOSE=$arg
            ;;
        --self)
            SELF=1
            ;;
        *=*)
            eval $(echo $arg | cut -d= -f1)=\"$(echo $arg | cut -d= -f2-)\"
            ;;
    esac
done

if [[ -n "${SELF}" ]]; then
    # Ensure schema-salad-tool command
    if [[ ! -x $(command -v schema-salad-tool) ]]; then
        if [[ ! -d ./schema_salad ]]; then
            echo >&2 "You need: git submodule update --init"
            exit 1
        fi
        # Install schema_salad to validate cwl files.
        cd ./schema_salad && pip install . --quiet && cd ..
    fi
    # This is how CWL should be written.
    DEFINITION=./schema_salad/schema_salad/tests/test_schema/CommonWorkflowLanguage.yml
    # Let's test each files
    for target in v1.0/v1.0/*.cwl; do
        schema-salad-tool ${DEFINITION} ${target} --quiet
        if [[ $? -ne 0 ]]; then echo "[INVALID] ${target}" && exit 1; fi
    done
    exit 0
fi

DRAFT_DIR="$(cd $(dirname $0); pwd)/${DRAFT}"

if ! runner="$(which $RUNNER)" ; then
    echo >&2 "$helpmessage"
    echo >&2
    echo >&2 "runner '$RUNNER' not found"
    exit 1
fi

runs=0
failures=0

checkexit() {
    if [[ "$?" != "0" ]]; then
        failures=$((failures+1))
    fi
}

runtest() {
    echo "--- Running conformance test $DRAFT on $1 ---"

    "$1" --version

    runs=$((runs+1))
    (cd $DRAFT_DIR
     COMMAND="cwltest --tool $1 \
	     --test=conformance_test_${DRAFT}.yaml ${CLASS} ${TEST_N} \
	     ${VERBOSE} ${TEST_L} ${TEST_J} ${ONLY_TOOLS} ${JUNIT_XML} \
	     --basedir ${DRAFT_DIR} -- ${EXTRA}"
     if [[ $VERBOSE == "--verbose" ]]; then echo ${COMMAND}; fi
     ${COMMAND}
    )
    checkexit
}

if [[ $PLATFORM == "Linux" ]]; then
    runtest "$(readlink -f $runner)"
else
    runtest "$(greadlink -f $runner)"
fi

if [[ -n "$TEST_L" ]] ; then
   exit 0
fi

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
