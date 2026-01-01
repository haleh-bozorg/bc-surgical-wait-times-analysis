# main.py
import os
import pandas as pd
import matplotlib.pyplot as plt

RAW_PATH = "data/raw/bc_surgical_wait_times_quarterly_2009_2025.xlsx"

def load_data(path: str) -> pd.DataFrame:
    return pd.read_excel(path)

def build_procedure_series(df: pd.DataFrame, procedure_name: str) -> pd.DataFrame:
    df_proc = df[df["PROCEDURE_GROUP"] == procedure_name].copy()

    # ensure numeric
    df_proc["WAITING"] = pd.to_numeric(df_proc["WAITING"], errors="coerce")
    df_proc["COMPLETED"] = pd.to_numeric(df_proc["COMPLETED"], errors="coerce")

    # aggregate
    agg = (
        df_proc.groupby(["FISCAL_YEAR", "QUARTER"])[["WAITING", "COMPLETED"]]
        .sum()
        .reset_index()
    )

    # time label for plotting
    agg["time"] = agg["FISCAL_YEAR"].astype(str) + "-" + agg["QUARTER"]

    # backlog pressure
    agg["pressure"] = agg["WAITING"] / agg["COMPLETED"]

    # tag procedure
    agg["procedure"] = procedure_name

    # period label (Pre/COVID/Post)
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
    print("Shape:", df.shape)

    skin = build_procedure_series(df, "Skin Tumour Removal")
    print("✅ built skin")

    hernia = build_procedure_series(df, "Hernia Repair - Abdominal")
    print("✅ built hernia")

    # ---- Summary by period (mean pressure) ----
    skin_period = skin.groupby("period")["pressure"].mean()
    hernia_period = hernia.groupby("period")["pressure"].mean()

    print("\nSkin pressure by period (mean):")
    print(skin_period.round(3))

    print("\nHernia pressure by period (mean):")
    print(hernia_period.round(3))

    # quick sanity check
    print("\nSkin head:\n", skin[["procedure","time","WAITING","COMPLETED","pressure","period"]].head())
    print("\nHernia head:\n", hernia[["procedure","time","WAITING","COMPLETED","pressure","period"]].head())

    # ensure figures folder exists
    os.makedirs("reports/figures", exist_ok=True)

    # =========================================================
    # CHART 1: Pressure trend comparison (line chart)
    # =========================================================
    plt.figure(figsize=(10, 4))
    plt.title(
        "Backlog Pressure Trend (WAITING / COMPLETED)\nSkin Tumour vs Hernia – BC",
        fontsize=12
    )
    plt.ylabel("Pressure (ratio)")
    plt.xlabel("Fiscal Quarter")

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

    out_path_trend = "reports/figures/pressure_trend_comparison.png"
    plt.savefig(out_path_trend, dpi=200)
    plt.show()

    print(f"\n✅ Saved trend chart to: {out_path_trend}")

    # =========================================================
    # CHART 2: Mean pressure by period (bar chart)  ✅ DIFFERENT
    # =========================================================
    periods_order = ["Pre-COVID", "COVID", "Post-COVID"]

    summary = pd.DataFrame({
        "Skin Tumour Removal": skin_period,
        "Hernia Repair - Abdominal": hernia_period
    }).reindex(periods_order)

    ax = summary.plot(kind="bar", figsize=(8, 4))
    ax.set_title("Mean Backlog Pressure by Period\nPre-COVID vs COVID vs Post-COVID", fontsize=12)
    ax.set_xlabel("Period")
    ax.set_ylabel("Mean Pressure (WAITING / COMPLETED)")
    ax.legend(title="Procedure")
    plt.xticks(rotation=0)
    plt.tight_layout()

    out_path_bar = "reports/figures/pressure_mean_by_period.png"
    plt.savefig(out_path_bar, dpi=200)
    plt.show()

    print(f"✅ Saved period summary chart to: {out_path_bar}")

if __name__ == "__main__":
    main()