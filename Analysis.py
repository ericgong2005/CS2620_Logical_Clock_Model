import pandas as pd
import matplotlib.pyplot as plt
import sys

def main():
   # Confirm validity of commandline arguments
    if len(sys.argv) != 5:
        print("Usage: python Analysis.py DIRECTORY PORT1 PORT2 PORT3")
        sys.exit(1)
    
    dataframes = []
    for port in sys.argv[2:]:
        df = pd.read_csv(f"{sys.argv[1]}/Log_{port}.txt", sep="\t")
        dataframes.append(df)
    
    # Queue Size as a function of True Time
    plt.figure(figsize=(10, 6))
    for df in dataframes:
        plt.plot(df["TRUE_TIME"], df["QUEUE_SIZE"], label=f"{df['SELF_PORT'].iloc[0]} with {float(df['SELF_INTERVAL'].iloc[0]):.3f}s Ticks")
    plt.xlabel("True Time")
    plt.ylabel("Queue Size")
    plt.title("Queue Size as a Function of True Time")
    plt.legend()
    plt.grid(True)
    plt.savefig(f"{sys.argv[1]}/Queue_size.png")
    plt.close()
    
    # Logical Time as a function of True Time.
    plt.figure(figsize=(10, 6))
    for df in dataframes:
        plt.plot(df["TRUE_TIME"], df["LOGICAL_TIME"], label=f"{df['SELF_PORT'].iloc[0]} with {float(df['SELF_INTERVAL'].iloc[0]):.3f}s Ticks")
    plt.xlabel("True Time")
    plt.ylabel("Logical Time")
    plt.title("Logical Time as a Function of True Time")
    plt.legend()
    plt.grid(True)
    plt.savefig(f"{sys.argv[1]}/Logical_time.png")
    plt.close()

if __name__ == "__main__":
    main()