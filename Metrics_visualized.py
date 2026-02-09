import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns 
from datetime import datetime
from datetime import timedelta

cleaned = pd.read_csv('project_dataset/project_clean_master.csv')
display(cleaned)

# convert to datetime to be recognizable by pandas as time
cleaned['created_at'] = pd.to_datetime(cleaned['created_at'])
# initiate the cohort series
cohort = cleaned.groupby('user_id')['created_at'].min().dt.to_period('M')
display(cohort)
type(cohort)

# initiate the cohort month column by linking the cohort series based on the user id
cleaned['cohort_month'] = cleaned['user_id'].map(cohort)
display(cleaned)

# initiate the activity month column based on the created at column ordered by months
cleaned['activity_month'] = cleaned['created_at'].dt.to_period('M')
display(cleaned)

# initiate cohort index column to establish a monthly timeline for each raw starting from the month 0
from operator import attrgetter
cleaned['cohort_index'] = (cleaned['activity_month'] - cleaned['cohort_month']).apply(attrgetter('n'))
display(cleaned)

# counting the usage per cohort across the timeline of measurement
grouped = cleaned.groupby(['cohort_month', 'cohort_index'])['id'].count()
display(grouped)

# the second metrics#
# # initiate the incident boolen colmun 
cleaned['incident_request'] = (cleaned['category'] == 'month_delay_on_payment').astype(int)

# new data frame summing the incidents per cohort
incident_counts = (cleaned.groupby(['cohort_month', 'cohort_index'])['incident_request'].sum().reset_index())
display(incident_counts)

# new data frame counting the incidents per cohort
total_requests = (cleaned.groupby(['cohort_month', 'cohort_index'])['id'].count().reset_index().rename(columns={'id': 'total_requests'}))
display(total_requests)

# merging on left to include the nan valuse and change them to 0 
cohort_metrics = total_requests.merge(incident_counts, on=['cohort_month', 'cohort_index'], how='left')
cohort_metrics['incident_request'] = (cohort_metrics['incident_request'] .fillna(0) .astype(int))

#computing
cohort_metrics['incident_rate'] = (cohort_metrics['incident_request'] / cohort_metrics['total_requests'])
display(cohort_metrics)
# cohort_metrics.sample(20)

# normal display
cleaned

revenue = (
    cleaned.groupby(["id", "user_id", "cohort_month", "activity_month", "cohort_index"], as_index=False)
           .agg(request_revenue=("total_amount", "sum"))
)
revenue

revenue_by_cohort = (
    revenue.groupby(["cohort_month", "cohort_index"], as_index=False)
             .agg(cohort_revenue=("request_revenue", "sum"))
)
revenue_by_cohort.sample(20)

#new_metric
user_request_counts = cleaned.groupby("user_id")["id"].nunique()
second_time_users = user_request_counts[user_request_counts >= 2].index
cleaned["second_time_user"] = cleaned["user_id"].isin(second_time_users).astype(int)

cohort_users = cleaned[["cohort_month", "user_id", "second_time_user"]].drop_duplicates()
retention_by_cohort = (
    cohort_users.groupby("cohort_month", as_index=False)
               .agg(total_users=("user_id", "nunique"), retained_users=("second_time_user", "sum"))
)
retention_by_cohort["retention_rate"] = round(retention_by_cohort["retained_users"] / retention_by_cohort["total_users"], 2)
retention_by_cohort.head()

#visuals
import matplotlib.pyplot as plt
import seaborn as sns


usage_pivot = cleaned.pivot_table(index='cohort_month', columns='cohort_index', values='id', aggfunc='count')

incident_pivot = cleaned.pivot_table(index='cohort_month', columns='cohort_index', values='incident_request', aggfunc='mean')

revenue_pivot = cleaned.pivot_table(index='cohort_month', columns='cohort_index', values='total_amount', aggfunc='sum')

user_request_counts = cleaned.groupby("user_id")["id"].nunique()
second_timers = user_request_counts[user_request_counts >= 2].index
cleaned["second_time_user"] = cleaned["user_id"].isin(second_timers).astype(int)
retention_rate_df = cleaned.groupby("cohort_month")["second_time_user"].mean().reset_index()


sns.set_style("whitegrid")

# Chart 1: Usage Heatmap
plt.figure(figsize=(12, 6))
plt.title('Cohort Analysis: Frequency of Usage (Number of Loans)')
sns.heatmap(usage_pivot, annot=True, fmt='.0f', cmap='YlGnBu')
plt.ylabel('Cohort Month')
plt.xlabel('Months Since First Loan')
plt.show()

# Chart 2: Incident Rate Heatmap
plt.figure(figsize=(12, 6))
plt.title('Cohort Analysis: Incident Rate (%)')
sns.heatmap(incident_pivot, annot=True, fmt='.1%', cmap='RdYlGn_r') # Red = Bad
plt.ylabel('Cohort Month')
plt.xlabel('Months Since First Loan')
plt.show()

# Chart 3: Revenue Heatmap
plt.figure(figsize=(12, 6))
plt.title('Cohort Analysis: Total Revenue ($)')
sns.heatmap(revenue_pivot, annot=True, fmt='.0f', cmap='Greens')
plt.ylabel('Cohort Month')
plt.xlabel('Months Since First Loan')
plt.show()

# Chart 4: Overall Retention Rate per Cohort
plt.figure(figsize=(12, 5))
sns.barplot(data=retention_rate_df, x='cohort_month', y='second_time_user', palette='Blues_d')
plt.title('Overall Retention: % of Users Who Took a 2nd Loan', fontsize=14)
plt.ylabel('Retention Rate')
plt.xlabel('Cohort Month')
plt.ylim(0, 1) 
plt.show()