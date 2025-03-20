#!/bin/bash

DATASETS=("reddit_50k" "reddit_100k" "reddit_200k" "reddit_400k" "reddit_800k")
SLAVE_CONFIGS=("1" "2" "4")
CSV_FILE="benchmark_results.csv"
LOG_DIR="logs"

# Create logs dir if it doesn't exist
mkdir -p "$LOG_DIR"

# Initialize CSV file
echo "Dataset,Slaves,Execution Time (s),CPU Time (s),Memory Usage (MB-seconds),CPU Usage (vcore-seconds),CPU (%),Total Memory Used (MB)" > $CSV_FILE

# Function to enable/disable nodes
set_active_slaves() {
    local num_slaves=$1
    echo "Setting up cluster with $num_slaves slaves..."

    # Stop all slaves
    for slave in slave1 slave2 slave3 slave4; do
        ssh $slave "/usr/local/hadoop/sbin/hadoop-daemon.sh stop datanode"
        ssh $slave "/usr/local/hadoop/sbin/yarn-daemon.sh stop nodemanager"
    done

    # Start only the required number of slaves
    for ((i=1; i<=$num_slaves; i++)); do
        ssh slave$i "/usr/local/hadoop/sbin/hadoop-daemon.sh start datanode"
        ssh slave$i "/usr/local/hadoop/sbin/yarn-daemon.sh start nodemanager"
    done

    sleep 15  # Give Hadoop some time to reconfigure

    echo "Checking if HDFS is in safe mode..."
    SAFE_MODE_STATUS=$(hdfs dfsadmin -safemode get | grep "Safe mode is ON")

    if [[ -n "$SAFE_MODE_STATUS" ]]; then
	echo "HDFS is in safe mode. Attempting to exit..."
	hdfs dfsadmin -safemode leave
	sleep 5 
    fi

    echo "Running HDFS Balancer to distribute data..."
    hdfs balancer -threshold 10 &
}

# Benchmark loop
for slaves in "${SLAVE_CONFIGS[@]}"; do
    for dataset in "${DATASETS[@]}"; do
        # Set active slaves
        set_active_slaves $slaves

        # Define input and output directories
        INPUT_DIR="/input/$dataset"
        OUTPUT_DIR="/output_$dataset_${slaves}slaves"

        # Ensure output directory is removed before running the job
        if hdfs dfs -test -d $OUTPUT_DIR; then
            echo "Removing existing output directory: $OUTPUT_DIR"
            hdfs dfs -rm -r $OUTPUT_DIR
        fi

        # Create log directory for this specific run
        RUN_LOG_DIR="${LOG_DIR}/${dataset}_${slaves}"
        mkdir -p "$RUN_LOG_DIR"

        # Define log file paths
        LOG_FILE="${RUN_LOG_DIR}/final_report.log"
        NODE_USAGE_FILE="${RUN_LOG_DIR}/node_usage.log"
        APPLICATION_STATUS_FILE="${RUN_LOG_DIR}/application_status.log"
        EXECUTION_TIME_FILE="${RUN_LOG_DIR}/execution_time.log"
        JOB_LOGS_FILE="${RUN_LOG_DIR}/job_logs.log"

	# Ensure they all exist
	touch "$NODE_USAGE_FILE" "$APPLICATION_STATUS_FILE" "$EXECUTION_TIME_FILE" "$JOB_LOGS_FILE"

        # Remove existing output directory
        hdfs dfs -rm -r $OUTPUT_DIR 2>/dev/null

        # Start timer
        START_TIME=$(date +%s)

        # Run Hadoop job
        (time hadoop jar /usr/local/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.3.6.jar \
          -input $INPUT_DIR \
          -output $OUTPUT_DIR \
          -mapper mapper.py \
          -reducer reducer.py \
          -file mapper.py \
          -file reducer.py) 2>&1 | tee "$EXECUTION_TIME_FILE"

        # Capture execution time
        END_TIME=$(date +%s)
        ELAPSED_TIME=$((END_TIME - START_TIME))

        # Get Application ID
        APP_ID=$(yarn application -list -appStates FINISHED | awk 'NR==3 {print $1}')

        # If APP_ID is empty, job likely failed
        if [[ -z "$APP_ID" ]]; then
            echo "Error: Job failed for dataset $dataset with $slaves slaves" >> $CSV_FILE
            continue
        fi

        # Get job stats
        yarn application -status $APP_ID > "$APPLICATION_STATUS_FILE"
        MEMORY_USAGE=$(grep "Aggregate Resource Allocation" "$APPLICATION_STATUS_FILE" | awk '{print $5}')
        CPU_USAGE=$(grep "Aggregate Resource Allocation" "$APPLICATION_STATUS_FILE" | awk '{print $7}')

        # Get user/system CPU time
        CPU_TIME=$(grep "user" "$EXECUTION_TIME_FILE" | awk '{print $2}' | sed 's/s//')

        # Capture Node CPU & Memory Usage
        echo "===== NODE CPU & MEMORY USAGE =====" > "$NODE_USAGE_FILE"
        for slave in slave1 slave2 slave3 slave4; do
            echo "Stats for $slave:" >> "$NODE_USAGE_FILE"
            ssh $slave "top -b -n 1 | head -20" >> "$NODE_USAGE_FILE"
        done

        # Generate Final Report
        (
          echo "===== EXECUTION TIME ====="
          cat "$EXECUTION_TIME_FILE"
          echo "===== YARN APPLICATION STATS ====="
          cat "$APPLICATION_STATUS_FILE"
          echo "===== JOB LOGS (CPU/MEMORY) ====="
          cat "$JOB_LOGS_FILE" | grep "CPU\|Memory\|Elapsed"
          echo "===== NODE CPU & MEMORY USAGE ====="
          cat "$NODE_USAGE_FILE"
        ) > "$LOG_FILE"

        # Resource Configuration
        TOTAL_CORES_PER_NODE=1
        TOTAL_MEMORY_PER_NODE_MB=1964

        # Calculate total cores and memory in the cluster
        TOTAL_CORES=$(( slaves * TOTAL_CORES_PER_NODE ))
        TOTAL_MEMORY_MB=$(( slaves * TOTAL_MEMORY_PER_NODE_MB ))

        # Convert to percentage
        CPU_PERCENTAGE=$(awk "BEGIN {print ($CPU_USAGE / ($ELAPSED_TIME * $TOTAL_CORES)) * 100}")
        TOTAL_MEMORY_USED_MB=$(awk "BEGIN {print ($MEMORY_USAGE / $ELAPSED_TIME)}")

        # Log results to CSV
        echo "$dataset,$slaves,$ELAPSED_TIME,$CPU_TIME,$MEMORY_USAGE,$CPU_USAGE,$CPU_PERCENTAGE,$TOTAL_MEMORY_USED_MB" >> $CSV_FILE
    done
done

echo "Benchmarking complete! Results saved in $CSV_FILE and logs/"

