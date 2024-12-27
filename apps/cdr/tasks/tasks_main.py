import subprocess

"""
1. The producer process (`tasks_producer.py`) is responsible for generating tasks or data.
2. The consumer processes (`tasks_consumer.py`) process the tasks, each assigned a unique shard ID.
"""
if __name__ == "__main__":
    producer_process = subprocess.Popen(['python', 'tasks_producer.py'])
    consumer_processes = []
    shard_count = 2
    for shard_id in range(shard_count):
        process = subprocess.Popen(['python', 'tasks_consumer.py', str(shard_id)])
        consumer_processes.append(process)
    try:
        producer_process.wait()
        for process in consumer_processes:
            process.wait()
    except KeyboardInterrupt:
        producer_process.terminate()
        for process in consumer_processes:
            process.terminate()
        print("Shutting down gracefully.")
