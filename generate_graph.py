import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv("benchmark_results.csv")

# Adjust slave count (subtract 1, it counted master as 1 during the run)
df["Adjusted Slaves"] = df["Slaves"] - 1


df_50k = df[df["Dataset"] == "reddit_50k"]
df_100k = df[df["Dataset"] == "reddit_100k"]

plt.figure(figsize=(8, 5))

plt.plot(df_50k["Adjusted Slaves"], df_50k["Execution Time (s)"], marker='o', linestyle='-', label="reddit_50k", color='blue')
plt.plot(df_100k["Adjusted Slaves"], df_100k["Execution Time (s)"], marker='s', linestyle='-', label="reddit_100k", color='red')

plt.title("Execution Time Comparison")
plt.xlabel("Number of Slaves")
plt.ylabel("Execution Time (s)")
plt.grid(True)
plt.legend()

plt.tight_layout()
plt.savefig("execution_time_comparison.png")
plt.show()

