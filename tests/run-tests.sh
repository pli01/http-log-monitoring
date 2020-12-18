#!/bin/bash
#set -x
function clean() {
    ret=$?
    echo "# clean"
    kill -9 $monitoring_pid $generate_pid 2>&-
    rm -rf $test_output
    rm -rf $logfile
    exit $ret
}

function run_test() {
    set +e
    n=$1
    test_match=$2
    test_output=$3
    timeout=120;
    test_result=1
    echo "# Test $n: Waiting $timeout seconds to find '$test_match' in $test_output"
    until [ "$timeout" -le 0 -o "$test_result" -eq "0" ] ; do
       test -f $test_output && grep "$test_match" $test_output
       test_result=$?
       if [ "$test_result" -eq "0" ]; then
          break
       fi
       echo -n "."
       (( timeout-- ))
       sleep 1
    done
    if [ "$test_result" -gt "0" ] ; then
        ret=$test_result
        echo "# Test $n: '$test_match' FAILED"
        exit $ret
    else
        echo "# Test $n: '$test_match' SUCCESS"
    fi
}

# trap signal
trap clean EXIT KILL

# allows for log messages to be immediately dumped
export PYTHONUNBUFFERED=1

dirname=$(dirname $0)
bindir=..
timestamp="$(date "+%Y-%m-%d-%H:%M:%S")"

generate_logs="generate-logs.py"
http_log_monitoring="http-log-monitoring.py"
logfile="${dirname}/access_log_generated_${timestamp}.log"
test_output="${dirname}/test_output_${timestamp}.log"

# setup test
echo "# setup test"
threshold=20
duration=20
alert_time=30

echo "# starting $generate_logs: $threshold req/s during $duration"
> $logfile
${bindir}/$generate_logs -f $logfile -t $threshold -d $duration 2>&1 >&- &
generate_pid=$!

echo "# starting $http_log_monitoring -f $logfile (override alarm time detection to $alert_time seconds)"
${bindir}/$http_log_monitoring -f $logfile -a $alert_time  2>&1 >$test_output &
monitoring_pid=$!

# test 1
test_match='Summary stats last 10 seconds'
run_test "1" "$test_match" "$test_output" 

# test 2
test_match='total "sections" of the web site'
run_test "2" "$test_match" "$test_output" 

# test 3
test_match='^High traffic generated an alert'
run_test "3" "$test_match" "$test_output" 

# test 2
test_match='^Traffic back to normal'
run_test "4" "$test_match" "$test_output" 

exit 0
