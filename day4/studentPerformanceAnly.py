import pandas as pd

data = {
    "Name": ["A", "B", "C", "D", "E"],
    "Score": [85, 39, 76, 55, 30]
}
df = pd.DataFrame(data)
df["Passed"] = df["Score"] >= 40
highest_score = df["Score"].max()
total_passed = df["Passed"].sum()
print("Student Results:")
print(df)
print("\nHighest Score:", highest_score)
print("Total Students Passed:", total_passed)
