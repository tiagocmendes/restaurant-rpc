#!/bin/bash
echo "Starting drive-through.py background process"
source venv/bin/activate ; python3 drive-through.py 2>/dev/null &
echo "Starting clerk.py background process"
source venv/bin/activate ; python3 clerk.py 2>/dev/null &
echo "Starting chef.py background process"
source venv/bin/activate ; python3 chef.py 2>/dev/null &
echo "Starting waiter.py background process"
source venv/bin/activate ; python3 waiter.py 2>/dev/null &
for ((i = 1; i <= $1; i++)); do
    echo "Starting client.py No. $i background process"
    source venv/bin/activate ; python3 client.py 2>/dev/null &
    sleep 5
done
