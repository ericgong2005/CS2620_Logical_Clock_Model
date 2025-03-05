# May need to run chmod +x Variation_start.sh

# Exit immediately if a command fails
set -e  

# Control C kills all models
trap "kill 0" SIGINT SIGTERM

# Check commandline arguments
if [ "$#" -ne 6 ]; then
    echo "Usage: $0 HOSTNAME PORT1 PORT2 PORT3 EVENT_NUM MAX_TICKS"
    exit 1
fi

time=$(($6 * 2))

mkdir "Variation_Logs/Trials/T${time}N${5}"

python Variation_Model.py "$1" "$2" "$3" "$4" "$5" "1" "$time"&
python Variation_Model.py "$1" "$3" "$2" "$4" "$5" "$6" "$time"& 
python Variation_Model.py "$1" "$4" "$2" "$3" "$5" "$time" "$time"&

wait


