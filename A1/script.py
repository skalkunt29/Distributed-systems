import multiprocessing
import subprocess

NUM_PROCESSES = 50

def run_program(i):
    program_map = {0: ["python3", "buyer_client.py"], 1: ["python3", "seller_client.py"]}
    result = subprocess.run(program_map[i % len(program_map)], stdout=subprocess.PIPE)
    return float(result.stdout.strip())

if __name__ == '__main__':

    # multiprocessing.freeze_support()

    # Start 100 processes concurrently
    with multiprocessing.Pool(processes=NUM_PROCESSES) as pool:
        results = pool.map(run_program, range(NUM_PROCESSES))

    # Calculate the average of the results
    average = sum(results) / len(results)

    print("Average:", average)



