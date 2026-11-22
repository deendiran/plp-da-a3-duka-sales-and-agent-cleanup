"""cleaning_pipeline.py.

Module providing automated data cleaning for mobile money agent network transactions.
Resolves data quality issues across six dimensions without manual edits or hardcoded indices.
"""

from typing import Any, Dict, List, Tuple
import numpy as np
import pandas as pd


def clean_agent_data(
    txns: pd.DataFrame, agents: pd.DataFrame
) -> Tuple[pd.DataFrame, List[Dict[str, Any]]]:
  """Cleans transaction and agent datasets and returns a merged, validated DataFrame.

  Rules Applied:
  1. Uniqueness: Deduplicates rows based on 'txn_id', retaining the first
  record.
  2. Consistency: Normalizes 'txn_type' strings (stripping whitespace,
  capitalizing)
     to strictly 'Deposit' or 'Withdrawal'.
  3. Consistency & Validity: Normalizes 'txn_date' separators ('/' to '-')
     and parses dates to standard ISO-8601 (YYYY-MM-DD).
  4. Validity & Completeness: Converts 'amount' to numeric float, treating
  'N/A' as NaN,
     imputes missing values using the median amount of each transaction type,
     and records imputation in an 'amount_imputed' boolean flag.
  5. Accuracy: Flags statistical outliers using the IQR rule (1.5 * IQR)
     in an 'is_outlier' boolean flag.
  6. Referential Integrity: Left-joins transactions to the agent register on
  'agent_id',
     preserving all transactions and labeling unmapped agents as 'Unknown'.

  Parameters
  ----------
  txns : pd.DataFrame
      Raw transactions DataFrame.
  agents : pd.DataFrame
      Master agent registry DataFrame.

  Returns
  -------
  Tuple[pd.DataFrame, List[Dict[str, Any]]]
      A tuple of (clean_df, log).
  """
  log: List[Dict[str, Any]] = []
  df = txns.copy()

  # 1. Uniqueness: Remove duplicate txn_id
  dup_count = int(df.duplicated(subset=['txn_id']).sum())
  df = df.drop_duplicates(subset=['txn_id'], keep='first').copy()
  log.append({
      'step': 'Deduplication',
      'dimension': 'Uniqueness',
      'column': 'txn_id',
      'rows_affected': dup_count,
      'description': (
          f'Identified and removed {dup_count} duplicate records based on'
          ' txn_id.'
      ),
  })

  # 2. Consistency: Standardize txn_type
  original_types = df['txn_type'].unique().tolist()
  df['txn_type'] = df['txn_type'].astype(str).str.strip().str.capitalize()
  type_changes = int((df['txn_type'] != txns.loc[df.index, 'txn_type']).sum())
  log.append({
      'step': 'Standardize txn_type',
      'dimension': 'Consistency',
      'column': 'txn_type',
      'rows_affected': type_changes,
      'description': (
          f'Normalized {type_changes} non-standard values from {original_types}'
          " to ['Deposit', 'Withdrawal']."
      ),
  })

  # 3. Validity & Consistency: Standardize txn_date
  slash_count = int(df['txn_date'].astype(str).str.contains('/').sum())
  df['txn_date'] = pd.to_datetime(
      df['txn_date'].astype(str).str.replace('/', '-'),
      format='mixed',
      errors='coerce',
  ).dt.strftime('%Y-%m-%d')
  log.append({
      'step': 'Format txn_date',
      'dimension': 'Validity & Consistency',
      'column': 'txn_date',
      'rows_affected': slash_count,
      'description': (
          f'Standardized {slash_count} slash dates into ISO-8601 YYYY-MM-DD.'
      ),
  })

  # 4. Validity & Completeness: Convert amount to numeric and impute missing
  cleaned_amount = df['amount'].astype(str).replace(
      ['N/A', 'nan', 'None', ''], np.nan
  )
  numeric_amount = pd.to_numeric(cleaned_amount, errors='coerce')

  missing_mask = numeric_amount.isna()
  missing_count = int(missing_mask.sum())
  df['amount_imputed'] = missing_mask

  # Group-specific median imputation by transaction type
  type_medians = numeric_amount.groupby(df['txn_type']).transform('median')
  df['amount'] = numeric_amount.fillna(type_medians)

  log.append({
      'step': 'Amount Conversion & Imputation',
      'dimension': 'Completeness & Validity',
      'column': 'amount',
      'rows_affected': missing_count,
      'description': (
          f'Converted amounts to numeric and imputed {missing_count} missing'
          ' values using txn_type medians.'
      ),
  })

  # 5. Accuracy: Flag outliers via IQR
  q1 = df['amount'].quantile(0.25)
  q3 = df['amount'].quantile(0.75)
  iqr = q3 - q1
  lower_bound = q1 - 1.5 * iqr
  upper_bound = q3 + 1.5 * iqr

  outlier_mask = (df['amount'] < lower_bound) | (df['amount'] > upper_bound)
  outlier_count = int(outlier_mask.sum())
  df['is_outlier'] = outlier_mask
  log.append({
      'step': 'Outlier Detection',
      'dimension': 'Accuracy',
      'column': 'amount',
      'rows_affected': outlier_count,
      'description': (
          f'Flagged {outlier_count} records outside IQR bounds [{lower_bound:.2f},'
          f' {upper_bound:.2f}].'
      ),
  })

  # 6. Referential Integrity: Left join with agent registry
  merged = df.merge(agents, on='agent_id', how='left')
  unmapped_count = int(merged['county'].isna().sum())
  merged['county'] = merged['county'].fillna('Unknown')
  log.append({
      'step': 'Agent Registry Merge',
      'dimension': 'Validity & Integrity',
      'column': 'agent_id',
      'rows_affected': unmapped_count,
      'description': (
          f'Left-joined agents. Labeled {unmapped_count} transactions with'
          ' unknown agents as Unknown.'
      ),
  })

  return merged, log