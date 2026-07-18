import pandas as pd

gt = pd.read_csv("data/pilot_ground_truth.csv")
llm = pd.read_csv("results/pilot_llm_output.csv")

print("=== Developer gán nhãn gì ===")
for comp in ["ob", "eb", "s2r"]:
    print(f"{comp.upper()}:", gt[f"consensus_{comp}"].value_counts().to_dict())

print("\n=== LLM gán nhãn gì ===")
for comp in ["ob", "eb", "s2r"]:
    print(f"{comp.upper()}:", llm[f"llm_{comp}_label"].value_counts().to_dict())