import matplotlib.pyplot as plt

# Example: Task Progress Values
tasks = ["Task 1", "Task 2", "Task 3", "Task 4"]
progress = [30, 50, 75, 90]  # Percentage values

# Creating a bar chart for progress
plt.figure(figsize=(8, 5))
bars = plt.bar(tasks, progress, color='skyblue', edgecolor='black')

# Adding percentage labels on top of each bar
for bar, pct in zip(bars, progress):
    plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 2,
             f"{pct}%", ha='center', va='bottom', fontsize=10, color='black')

# Chart labels and title
plt.title("Task Progress", fontsize=14)
plt.xlabel("Tasks", fontsize=12)
plt.ylabel("Progress (%)", fontsize=12)
plt.ylim(0, 100)  # Progress ranges from 0% to 100%
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Show the chart
plt.tight_layout()
plt.show()