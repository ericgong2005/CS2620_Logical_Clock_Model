# May need to run chmod +x start.sh

# Exit immediately if a command fails
set -e  

# Control C kills all models
trap "kill 0" SIGINT SIGTERM

# Check commandline arguments
if [ "$#" -ne 4 ]; then
    echo "Usage: $0 HOSTNAME PORT1 PORT2 PORT3"
    exit 1
fi

# Start the models all at once
python model.py "$1" "$2" "$3" "$4" &
python model.py "$1" "$3" "$2" "$4" &
python model.py "$1" "$4" "$2" "$3" &

wait

