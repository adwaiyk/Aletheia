import pandas as pd
import numpy as np
import random
import uuid
from datetime import datetime, timedelta

# --- 1. CONFIGURATION ---
NUM_NORMAL_ACCOUNTS = 130  
START_DATE = datetime(2023, 10, 1)

first_names = ["Rahul", "Priya", "Amit", "Neha", "Rohan", "Sneha", "Vikram", "Pooja", "Karan", "Anjali", "John", "Emma", "Michael", "Sarah", "David"]
last_names = ["Sharma", "Singh", "Patel", "Gupta", "Kumar", "Verma", "Jain", "Mehta", "Doe", "Smith", "Johnson", "Brown", "Taylor"]
cities = ["Mumbai, MH, 400001", "Delhi, DL, 110001", "Bangalore, KA, 560001", "New York, NY, 10001", "London, UK, EC1A 1BB"]

def generate_kyc():
    name = f"{random.choice(first_names)} {random.choice(last_names)}"
    dob = f"{random.randint(1950, 2000)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"
    address = f"{random.randint(10, 999)} {random.choice(['Main St', 'Park Ave', 'MG Road', 'High St'])}, {random.choice(cities)}"
    tax_id = f"PAN{random.randint(1000, 9999)}{random.choice('ABCDE')}"
    return name, dob, address, tax_id

def generate_account_number():
    return str(random.randint(10000000000, 99999999999))

data = []

# --- 2. GENERATE NORMAL ACCOUNTS (THE HAYSTACK) ---
# Normal accounts max out at 35,000 so they NEVER trigger the AML rules
for _ in range(NUM_NORMAL_ACCOUNTS):
    account_no = generate_account_number()
    name, dob, address, tax_id = generate_kyc()
    for _ in range(random.randint(8, 15)):
        txn_date = START_DATE + timedelta(days=random.randint(0, 60))
        is_credit = random.choice([True, False])
        if is_credit:
            data.append([account_no, name, dob, address, tax_id, txn_date.strftime("%Y-%m-%d"), uuid.uuid4().hex[:12].upper(), "CREDIT", "NEFT", round(random.uniform(1000, 35000), 2), "Employer / Salary", "Salary"])
        else:
            data.append([account_no, name, dob, address, tax_id, txn_date.strftime("%Y-%m-%d"), uuid.uuid4().hex[:12].upper(), "DEBIT", "POS", round(random.uniform(10, 15000), 2), "Amazon", "Shopping"])

# --- 3. INJECT EXACTLY 5 ANOMALIES ---

# 1. The False Positive (House Downpayment) -> Triggers > 1M Rule
fp_acct = generate_account_number()
fp_name, fp_dob, fp_address, fp_tax_id = generate_kyc()
data.append([fp_acct, fp_name, fp_dob, fp_address, fp_tax_id, "2023-10-25", uuid.uuid4().hex[:12].upper(), "DEBIT", "RTGS", 5500000.00, "DLF REAL ESTATE DEVELOPERS", "Downpayment for new house property Unit 4B"])

#  2. Fraudster 1 (Traditional Structuring / Smurfing) -> Triggers 45k-50k Rule
f1_acct = generate_account_number()
f1_name, f1_dob, f1_address, f1_tax_id = generate_kyc()
for i in range(4):
    data.append([f1_acct, f1_name, f1_dob, f1_address, f1_tax_id, (START_DATE + timedelta(days=i)).strftime("%Y-%m-%d"), uuid.uuid4().hex[:12].upper(), "CREDIT", "CASH", 49500.00, "SELF", "Branch Cash Deposit"])
data.append([f1_acct, f1_name, f1_dob, f1_address, f1_tax_id, "2023-10-10", uuid.uuid4().hex[:12].upper(), "DEBIT", "SWIFT", 195000.00, "GLOBAL TRADING LLC (Dubai)", "Invoice Payment"])

#  3. Fraudster 2 (UK Market Abuse / Insider Trading) -> Triggers > 1M Rule
f2_acct = generate_account_number()
f2_name, f2_dob, f2_address, f2_tax_id = generate_kyc()
data.append([f2_acct, f2_name, f2_dob, f2_address, f2_tax_id, "2023-11-02", uuid.uuid4().hex[:12].upper(), "DEBIT", "BROKERAGE", 1250000.00, "INTERACTIVE BROKERS UK", "Purchase of 500,000 shares ISIN GB0031348658"])
data.append([f2_acct, f2_name, f2_dob, f2_address, f2_tax_id, "2023-11-05", uuid.uuid4().hex[:12].upper(), "CREDIT", "BROKERAGE", 1850000.00, "INTERACTIVE BROKERS UK", "Liquidation of 500,000 shares ISIN GB0031348658"])

#  4. Fraudster 3 (Heavy Layering Pass-Through) -> Triggers > 1M Rule
f3_acct = generate_account_number()
f3_name, f3_dob, f3_address, f3_tax_id = generate_kyc()
data.append([f3_acct, f3_name, f3_dob, f3_address, f3_tax_id, "2023-10-15", uuid.uuid4().hex[:12].upper(), "CREDIT", "WIRE", 3000000.00, "APEX HOLDINGS LTD", "Consulting Retainer"])
for i in range(5):
    data.append([f3_acct, f3_name, f3_dob, f3_address, f3_tax_id, (datetime(2023, 10, 16) + timedelta(hours=i)).strftime("%Y-%m-%d"), uuid.uuid4().hex[:12].upper(), "DEBIT", "SWIFT", 590000.00, f"SHELL CORP {i} (Cayman Islands)", "Logistics Services"])

#  5. Fraudster 4 (Crypto Smurfing) -> Triggers 45k-50k Rule
f4_acct = generate_account_number()
f4_name, f4_dob, f4_address, f4_tax_id = generate_kyc()
for i in range(5):
    data.append([f4_acct, f4_name, f4_dob, f4_address, f4_tax_id, (START_DATE + timedelta(days=i*2)).strftime("%Y-%m-%d"), uuid.uuid4().hex[:12].upper(), "CREDIT", "IMPS", 48000.00, "UNKNOWN P2P", "P2P Transfer"])
data.append([f4_acct, f4_name, f4_dob, f4_address, f4_tax_id, "2023-10-20", uuid.uuid4().hex[:12].upper(), "DEBIT", "WIRE", 235000.00, "BINANCE HOLDINGS", "Crypto Funding"])

# --- 4. EXPORT ---
columns = ["account_no", "customer_name", "dob", "address", "tax_id", "txn_date", "txn_id", "txn_type", "mode", "amount", "counterparty", "transaction_memo"]
df = pd.DataFrame(data, columns=columns)
df = df.sample(frac=1).reset_index(drop=True).sort_values('txn_date').reset_index(drop=True)
df.to_csv("synthetic_banking_data.csv", index=False)

print("\nDATA GENERATED SUCCESSFULLY!")
print(f"FALSE POSITIVE: {fp_acct} (House Purchase)")
print(f"FRAUDSTER 1:    {f1_acct} (Structuring)")
print(f"FRAUDSTER 2:    {f2_acct} (Market Abuse UK)")
print(f"FRAUDSTER 3:    {f3_acct} (Heavy Layering)")
print(f"FRAUDSTER 4:    {f4_acct} (Crypto Smurfing)")