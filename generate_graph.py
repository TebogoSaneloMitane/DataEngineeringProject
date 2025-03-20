import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv("benchmark_results.csv")

# Adjust slave count (subtract 1, it counted master as 1 during the run)
df["Adjusted Slaves"] = df["Slaves"] - 1

# Convert Total Memory Used to GB
df["Total Memory Used (GB)"] = df["Total Memory Used (MB)"] / 1024

df_50k = df[df["Dataset"] == "reddit_50k"]
df_100k = df[df["Dataset"] == "reddit_100k"]

fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# Execution Time Plot
axes[0].plot(df_50k["Adjusted Slaves"], df_50k["Execution Time (s)"], marker='o', linestyle='-', label="reddit_50k", color='blue')
axes[0].plot(df_100k["Adjusted Slaves"], df_100k["Execution Time (s)"], marker='s', linestyle='-', label="reddit_100k", color='red')
axes[0].set_title("Execution Time Comparison")
axes[0].set_xlabel("Number of Slaves")
axes[0].set_ylabel("Execution Time (s)")
axes[0].grid(True)
axes[0].legend()

# CPU Usage Plot
axes[1].plot(df_50k["Adjusted Slaves"], df_50k["CPU (%)"], marker='o', linestyle='-', label="reddit_50k", color='blue')
axes[1].plot(df_100k["Adjusted Slaves"], df_100k["CPU (%)"], marker='s', linestyle='-', label="reddit_100k", color='red')
axes[1].set_title("CPU Usage (%) Comparison")
axes[1].set_xlabel("Number of Slaves")
axes[1].set_ylabel("CPU Usage (%)")
axes[1].grid(True)
axes[1].legend()

# Memory Usage Plot
axes[2].plot(df_50k["Adjusted Slaves"], df_50k["Total Memory Used (GB)"], marker='o', linestyle='-', label="reddit_50k", color='blue')
axes[2].plot(df_100k["Adjusted Slaves"], df_100k["Total Memory Used (GB)"], marker='s', linestyle='-', label="reddit_100k", color='red')
axes[2].set_title("Total Memory Used Comparison")
axes[2].set_xlabel("Number of Slaves")
axes[2].set_ylabel("Total Memory Used (GB)")
axes[2].grid(True)
axes[2].legend()

plt.tight_layout()
plt.savefig("execution_cpu_memory_comparison.png")
plt.show()
