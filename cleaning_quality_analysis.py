import pandas as pd

cash_df = pd.read_csv('project_dataset/extract - cash request - data analyst.csv')
fees_df = pd.read_csv('project_dataset/extract - fees - data analyst - .csv')

cash_df.head()

fees_df.head()

cash_df['created_at'] = pd.to_datetime(cash_df['created_at'])

clean_cash = cash_df[cash_df['status'].isin(['money_back', 'active'])].copy()

clean_cash = clean_cash[['user_id', 'id', 'created_at', 'recovery_status']]

clean_fees = fees_df[['cash_request_id', 'category', 'total_amount']].copy()

print(f"Clean Cash Rows: {len(clean_cash)}")
print(f"Clean Fees Rows: {len(clean_fees)}")
clean_cash.head()


# We use a 'left' join. This takes every row from 'clean_cash' and tries to find a match in 'clean_fees'.
# If a loan has no fees, it keeps the loan and puts NaN for the fee columns.
master_df = pd.merge(
    clean_cash,
    clean_fees,
    left_on='id',
    right_on='cash_request_id',
    how='left'
)

master_df['total_amount'] = master_df['total_amount'].fillna(0)

print(f"Total Rows in Master File: {len(master_df)}")
master_df.head()

master_df = master_df.dropna(subset=['user_id'])

master_df['total_amount'] = master_df['total_amount'].fillna(0)

master_df['recovery_status'] = master_df['recovery_status'].fillna('Normal Payment')

master_df['category'] = master_df['category'].fillna('No Fee')

print(f"Final Row Count: {len(master_df)}")
print(master_df.head())

master_df.to_csv('project_clean_master.csv', index=False)

clean_master = pd.read_csv('project_clean_master.csv')
clean_master.head()

cash_quality = {
    "rows": len(cash_df),
    "columns": cash_df.shape[1],
    "duplicate_ids": cash_df["id"].duplicated().sum(),
    "missing_user_id": cash_df["user_id"].isna().sum(),
    "missing_amount": cash_df["amount"].isna().sum(),
    "missing_status": cash_df["status"].isna().sum(),
    "missing_created_at": cash_df["created_at"].isna().sum(),
    "non_positive_amounts": (cash_df["amount"] <= 0).sum(),
    "created_at_min": cash_df["created_at"].min(),
    "created_at_max": cash_df["created_at"].max(),
}

fees_quality = {
    "rows": len(fees_df),
    "columns": fees_df.shape[1],
    "duplicate_ids": fees_df["id"].duplicated().sum(),
    "missing_cash_request_id": fees_df["cash_request_id"].isna().sum(),
    "missing_total_amount": fees_df["total_amount"].isna().sum(),
    "missing_status": fees_df["status"].isna().sum(),
    "missing_created_at": fees_df["created_at"].isna().sum(),
    "non_positive_total_amounts": (fees_df["total_amount"] <= 0).sum(),
    "created_at_min": fees_df["created_at"].min(),
    "created_at_max": fees_df["created_at"].max(),
}

quality_summary = pd.DataFrame(
    {
        "cash_requests": cash_quality,
        "fees": fees_quality,
    }
).T
quality_summary
