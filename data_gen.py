import pandas as pd
import numpy as np
import random
import uuid
from datetime import datetime, timedelta

# --- 1. CONFIGURATION ---
NUM_NORMAL_ACCOUNTS = 120  # Generates ~1200+ rows
START_DATE = datetime(2023, 10, 1)

# Fake KYC Data Generators
first_names = ["Rahul", "Priya", "Amit", "Neha", "Rohan", "Sneha", "Vikram", "Pooja", "Karan", "Anjali", "John", "Emma", "Michael", "Sarah", "David", "James", "William", "Olivia"]
last_names = ["Sharma", "Singh", "Patel", "Gupta", "Kumar", "Verma", "Jain", "Mehta", "Doe", "Smith", "Johnson", "Brown", "Taylor", "Anderson", "Thomas", "Jackson"]
cities = ["Mumbai, MH, 400001", "Delhi, DL, 110001", "Bangalore, KA, 560001", "New York, NY, 10001", "London, UK, EC1A 1BB", "San Francisco, CA, 94105", "Dubai, UAE, 00000"]

def generate_kyc():
    name = f"{random.choice(first_names)} {random.choice(last_names)}"
    dob = f"{random.randint(1950, 2000)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"
    address = f"{random.randint(10, 999)} {random.choice(['Main St', 'Park Ave', 'MG Road', 'High St', 'Oak Lane', 'Maple Drive'])}, {random.choice(cities)}"
    tax_id = f"PAN{random.randint(1000, 9999)}{random.choice('ABCDE')}"
    return name, dob, address, tax_id

def generate_account_number():
    # Real bank accounts use realistic 10-12 digit numbers, not obvious text.
    return str(random.randint(10000000000, 99999999999))

data = []

# --- 2. GENERATE NORMAL ACCOUNTS ---
for _ in range(NUM_NORMAL_ACCOUNTS):
    account_no = generate_account_number()
    name, dob, address, tax_id = generate_kyc()
    
    # Generate 8-15 normal transactions per account to easily cross 1000 rows
    for _ in range(random.randint(8, 15)):
        txn_date = START_DATE + timedelta(days=random.randint(0, 60), hours=random.randint(8, 18))
        txn_id = uuid.uuid4().hex[:12].upper()
        
        is_credit = random.choice([True, False])
        if is_credit:
            txn_type = "CREDIT"
            mode = random.choice(["NEFT", "RTGS", "IMPS", "ACH", "WIRE"])
            amount = round(random.uniform(1000, 85000), 2)
            counterparty = random.choice(["Employer / Salary", "Transfer In", "Dividend Payout", "Refund"])
            memo = random.choice(["Salary credited", "Monthly rent received", "Refund", "Transfer from savings", "Invoice Payment"])
        else:
            txn_type = "DEBIT"
            mode = random.choice(["UPI", "POS", "CASH", "DIRECT DEBIT"])
            amount = round(random.uniform(10, 15000), 2)
            counterparty = random.choice(["Amazon", "Starbucks", "Grocery Store", "Utility Bill", "ATM Withdrawal", "Insurance Premium"])
            memo = random.choice(["Online shopping", "Coffee", "Groceries", "Electricity bill", "Cash for weekend", "Monthly premium"])

        data.append([account_no, name, dob, address, tax_id, txn_date.strftime("%d-%m-%Y"), txn_id, txn_type, mode, amount, counterparty, memo])


# --- 3. INJECT SUSPECT 1: THE "SMURFER" (Structuring for FIU-IND / FinCEN) ---
smurfer_acct = generate_account_number()
s_name, s_dob, s_address, s_tax_id = generate_kyc()

for i in range(7):
    txn_date = START_DATE + timedelta(days=i, hours=10)
    txn_id = uuid.uuid4().hex[:12].upper()
    amount = random.choice([49000.00, 49500.00, 48000.00, 49900.00])
    data.append([smurfer_acct, s_name, s_dob, s_address, s_tax_id, txn_date.strftime("%d-%m-%Y"), txn_id, "CREDIT", "CASH", amount, "SELF", "Cash Deposit via Branch"])

wire_date = START_DATE + timedelta(days=7, hours=14)
data.append([smurfer_acct, s_name, s_dob, s_address, s_tax_id, wire_date.strftime("%d-%m-%Y"), uuid.uuid4().hex[:12].upper(), "DEBIT", "SWIFT", 335000.00, "GLOBAL TRADING LLC (Dubai)", "Invoice #8849 Payment"])


# --- 4. INJECT SUSPECT 2: THE "FALSE POSITIVE" (For the Life Event Clearance Engine) ---
fp_acct = generate_account_number()
fp_name, fp_dob, fp_address, fp_tax_id = generate_kyc()

for i in range(3): # A few normal transactions to blend in
    txn_date = START_DATE + timedelta(days=i*5)
    data.append([fp_acct, fp_name, fp_dob, fp_address, fp_tax_id, txn_date.strftime("%d-%m-%Y"), uuid.uuid4().hex[:12].upper(), "CREDIT", "NEFT", 85000.00, "Salary", "Monthly Salary"])

fp_date = START_DATE + timedelta(days=15, hours=11)
data.append([fp_acct, fp_name, fp_dob, fp_address, fp_tax_id, fp_date.strftime("%d-%m-%Y"), uuid.uuid4().hex[:12].upper(), "DEBIT", "RTGS", 5500000.00, "DLF REAL ESTATE DEVELOPERS", "Downpayment for new house property Unit 4B"])


# --- 5. INJECT SUSPECT 3: THE "MARKET ABUSER" (For UK FCA Insider Trading) ---
uk_acct = generate_account_number()
uk_name, uk_dob, uk_address, uk_tax_id = generate_kyc()

# Massive highly anomalous stock purchase
uk_date = START_DATE + timedelta(days=22, hours=9, minutes=15)
data.append([uk_acct, uk_name, uk_dob, uk_address, uk_tax_id, uk_date.strftime("%d-%m-%Y"), uuid.uuid4().hex[:12].upper(), "DEBIT", "BROKERAGE", 1250000.00, "INTERACTIVE BROKERS UK", "Purchase of 500,000 shares ISIN GB0031348658 (Barclays PLC)"])

# Immediate liquidation post-announcement 3 days later for a massive profit
uk_sell_date = START_DATE + timedelta(days=25, hours=10, minutes=30)
data.append([uk_acct, uk_name, uk_dob, uk_address, uk_tax_id, uk_sell_date.strftime("%d-%m-%Y"), uuid.uuid4().hex[:12].upper(), "CREDIT", "BROKERAGE", 1850000.00, "INTERACTIVE BROKERS UK", "Liquidation of 500,000 shares ISIN GB0031348658 (Barclays PLC)"])


# --- 6. FINALIZE DATAFRAME ---
columns = ["account_no", "customer_name", "dob", "address", "tax_id", "txn_date", "txn_id", "txn_type", "mode", "amount", "counterparty", "transaction_memo"]
df = pd.DataFrame(data, columns=columns)

# Shuffle the data slightly so suspect transactions aren't perfectly sequential blocks in the raw CSV
df = df.sample(frac=1).reset_index(drop=True)

# Sort strictly by Date to mimic a real ledger chronologically
df['txn_date_obj'] = pd.to_datetime(df['txn_date'], format="%d-%m-%Y")
df = df.sort_values('txn_date_obj').drop('txn_date_obj', axis=1)

csv_filename = "synthetic_banking_data.csv"
df.to_csv(csv_filename, index=False)

print(f"Generated {len(df)} realistic transactions with standard 11-digit account numbers.")
print("--- SUSPECT ACCOUNTS TO INVESTIGATE IN DEMO ---")
print(f"1. Structuring/Smurfing (India/USA): {smurfer_acct}")
print(f"2. False Positive / Life Event (House Purchase): {fp_acct}")
print(f"3. Market Abuse / Insider Trading (UK FCA): {uk_acct}")
print("-----------------------------------------------------")
print(f"Saved to {csv_filename}")