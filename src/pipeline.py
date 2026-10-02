import pandas as pd
from pathlib import Path


# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def load_data():
    sales = pd.read_csv(RAW_DIR / "sales_daily.csv")
    sku = pd.read_csv(RAW_DIR / "sku_master.csv")
    calendar = pd.read_csv(RAW_DIR / "calendar.csv")
    inventory = pd.read_csv(RAW_DIR / "inventory_snapshots.csv")

    return sales, sku, calendar, inventory


def clean_data(sales, sku, calendar, inventory):

    # Convert dates
    sales["Date"] = pd.to_datetime(sales["Date"])
    sku["Launch_Date"] = pd.to_datetime(sku["Launch_Date"])
    calendar["date"] = pd.to_datetime(calendar["date"])
    inventory["Snapshot_Date"] = pd.to_datetime(inventory["Snapshot_Date"])

    # Remove inventory records for SKUs that do not exist
    # in the Sales/SKU Master datasets
    valid_skus = set(sku["SKU"])

    inventory = inventory[
        inventory["SKU"].isin(valid_skus)
    ].copy()

    # Treat missing calendar event fields as "No Event"
    calendar["holiday"] = calendar["holiday"].fillna("No Holiday")
    calendar["promotion_event"] = calendar["promotion_event"].fillna(
        "No Promotion"
    )

    return sales, sku, calendar, inventory


def save_data(sales, sku, calendar, inventory):

    sales.to_csv(
        PROCESSED_DIR / "sales_daily_clean.csv",
        index=False
    )

    sku.to_csv(
        PROCESSED_DIR / "sku_master_clean.csv",
        index=False
    )

    calendar.to_csv(
        PROCESSED_DIR / "calendar_clean.csv",
        index=False
    )

    inventory.to_csv(
        PROCESSED_DIR / "inventory_snapshots_clean.csv",
        index=False
    )


def main():

    sales, sku, calendar, inventory = load_data()

    sales, sku, calendar, inventory = clean_data(
        sales, sku, calendar, inventory
    )

    save_data(
        sales, sku, calendar, inventory
    )

    print("Data pipeline completed successfully.")
    print("Sales records:", len(sales))
    print("SKU Master records:", len(sku))
    print("Calendar records:", len(calendar))
    print("Inventory records:", len(inventory))


if __name__ == "__main__":
    main()

