# main.py
import os
import pandas as pd
import matplotlib.pyplot as plt

RAW_PATH = "data/raw/bc_surgical_wait_times_quarterly_2009_2025.xlsx"

def load_data(path: str) -> pd.DataFrame:
    return pd.read_excel(path)

def build_procedure_series(df: pd.DataFrame, procedure_name: str) -> pd.DataFrame:
    df_proc = df[df["PROCEDURE_GROUP"] == procedure_name].copy()

    df_proc["WAITING"] = pd.to_numeric(df_proc["WAITING"], errors="coerce")
    df_proc["COMPLETED"] = pd.to_numeric(df_proc["COMPLETED"], errors="coerce")

    agg = (
        df_proc.groupby(["FISCAL_YEAR", "QUARTER"])[["WAITING", "COMPLETED"]]
        .sum()
        .reset_index()
    )

    # time label for plotting
    agg["time"] = agg["FISCAL_YEAR"].astype(str) + "-" + agg["QUARTER"]

    # backlog pressure
    agg["pressure"] = agg["WAITING"] / agg["COMPLETED"]

    # tag procedure (prevents mixing)
    agg["procedure"] = procedure_name

    # --- COVID period labeling ---
    # Pre-COVID : FY <= 2018/19
    # COVID     : FY 2019/20 - 2021/22
    # Post-COVID: FY >= 2022/23
    def assign_period(fy: str) -> str:
        start_year = int(str(fy).split("/")[0])
        if start_year <= 2018:
            return "Pre-COVID"
        elif start_year <= 2021:
            return "COVID"
        else:
            return "Post-COVID"

    agg["period"] = agg["FISCAL_YEAR"].apply(assign_period)

    return agg

def main():
    print("main.py is running ✅")
    print("BC Surgical Wait Times — Project Start")

    df = load_data(RAW_PATH)
    print("✅ loaded excel")
    print("\nShape:", df.shape)

    skin = build_procedure_series(df, "Skin Tumour Removal")
    print("✅ built skin")

    hernia = build_procedure_series(df, "Hernia Repair - Abdominal")
    print("✅ built hernia")

    # quick sanity check
    print("\nSkin head:\n", skin[["procedure","time","WAITING","COMPLETED","pressure","period"]].head())
    print("\nHernia head:\n", hernia[["procedure","time","WAITING","COMPLETED","pressure","period"]].head())

    # --- COVID summary table (mean pressure by period) ---
    print("\nSkin pressure by period (mean):")
    print(skin.groupby("period")["pressure"].mean().round(3))

    print("\nHernia pressure by period (mean):")
    print(hernia.groupby("period")["pressure"].mean().round(3))

    # ---- Plot: Pressure comparison ----
    plt.figure(figsize=(10, 4))
    plt.title(
        "Backlog Pressure Comparison (WAITING / COMPLETED)\nSkin Tumour vs Hernia – BC",
        fontsize=12
    )
    plt.ylabel("Pressure (ratio)")
    plt.xlabel("Fiscal Quarter")
        # --- Highlight COVID period (FY 2019/20 to FY 2021/22) ---
    covid_years = {"2019/20", "2020/21", "2021/22"}
    covid_idx = skin.index[skin["FISCAL_YEAR"].isin(covid_years)].tolist()

    if covid_idx:
        start_i, end_i = min(covid_idx), max(covid_idx)
        plt.axvspan(start_i, end_i, alpha=0.15, label="COVID period")

    plt.plot(skin["pressure"], label="Skin Tumour Removal", linewidth=2)
    plt.plot(hernia["pressure"], label="Hernia Repair - Abdominal", linewidth=2, linestyle="--")

    plt.xticks(
        ticks=range(0, len(skin)),
        labels=skin["time"],
        rotation=90,
        fontsize=6
    )

    plt.legend()
    plt.tight_layout()

    # save for README
    os.makedirs("reports/figures", exist_ok=True)
    out_path = "reports/figures/pressure_comparison.png"

    out_path_covid = "reports/figures/pressure_comparison_covid.png"
    plt.savefig(out_path_covid, dpi=200)
    plt.savefig(out_path, dpi=200)
    plt.show()

    print(f"\n✅ Saved chart to: {out_path}")
    print(f"✅ Saved COVID chart to: {out_path_covid}")

if __name__ == "__main__":
    main()
