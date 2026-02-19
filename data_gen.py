# Data Generator

import pandas as pd
import random
from faker import Faker
from datetime import datetime, timedelta
import uuid

# Initialize Faker with Indian locale for realistic names/addresses
fake = Faker('en_IN')

# Constants for PMLA Thresholds
PAN_REPORTING_THRESHOLD = 50000
STR_CASH_LIMIT = 1000000

def generate_structuring_scenario(account_id, start_date, total_amount=1500000):
    """
    Generates a smurfing scenario: multiple cash deposits below 50k INR
    to avoid PAN reporting thresholds.
    """
    transactions = []
    amount_remaining = total_amount
    current_date = start_date

    print(f"[GEN] Injecting Structuring Pattern for Acct: {account_id}")

    while amount_remaining > 0:
        # Generate amount between 40k and 49k (Just below PAN threshold)
        txn_amount = random.randint(40000, 49000)
        
        # Handle last chunk
        if txn_amount > amount_remaining:
            txn_amount = amount_remaining

        txn = {
            'txn_id': uuid.uuid4().hex[:12].upper(),
            'account_no': account_id,
            'txn_date': current_date.strftime('%d-%m-%Y'),
            'txn_type': 'CREDIT',
            'mode': 'CASH', # Critical Red Flag: Cash Mode
            'amount': txn_amount,
            'balance': 0, # To be calculated later
            'counterparty': 'SELF',
            'remarks': 'CASH DEPOSIT',
            'branch_id': f'BR{random.randint(100, 999)}',
            'typology_tag': 'Structuring_Smurf'
        }
        transactions.append(txn)
        amount_remaining -= txn_amount

        # Increment time slightly (multiple deposits per day or spread out)
        if random.random() > 0.5:
            current_date += timedelta(hours=random.randint(1, 4))
        else:
            current_date += timedelta(days=1)
            
    return transactions

def generate_layering_scenario(root_account, mule_accounts, start_date):
    """
    Generates a layering scenario: Funds move Root -> Mule -> Shell -> Integration.
    Characterized by high velocity (rapid in/out).
    """
    transactions = []
    current_date = start_date
    transfer_sum = 2000000 # 20 Lakhs

    print(f"[GEN] Injecting Layering Pattern. Root: {root_account} -> Mules: len({mule_accounts})")

    # Step 1: Root sends to Mules (Placement/Layering 1)
    split_amount = transfer_sum / len(mule_accounts)
    
    for mule in mule_accounts:
        # Outflow from Root
        txn_out = {
            'txn_id': uuid.uuid4().hex[:12].upper(),
            'account_no': root_account,
            'txn_date': current_date.strftime('%d-%m-%Y'),
            'txn_type': 'DEBIT',
            'mode': 'NEFT',
            'amount': split_amount,
            'balance': 0,
            'counterparty': mule,
            'remarks': f'TRF TO {mule}',
            'branch_id': 'BR001',
            'typology_tag': 'Layering_Source'
        }
        transactions.append(txn_out)

        # Inflow to Mule
        txn_in = {
            'txn_id': uuid.uuid4().hex[:12].upper(),
            'account_no': mule,
            'txn_date': current_date.strftime('%d-%m-%Y'),
            'txn_type': 'CREDIT',
            'mode': 'NEFT',
            'amount': split_amount,
            'balance': 0,
            'counterparty': root_account,
            'remarks': f'TRF FROM {root_account}',
            'branch_id': 'BR999',
            'typology_tag': 'Layering_Mule_In'
        }
        transactions.append(txn_in)

        # Mule moves funds immediately (Velocity of funds < 24 hrs)
        next_day = current_date + timedelta(days=1)
        shell_company = fake.company()
        
        # Mule keeps a small cut (commission)
        layer_amt = int(split_amount * 0.98)
        
        txn_layer_out = {
            'txn_id': uuid.uuid4().hex[:12].upper(),
            'account_no': mule,
            'txn_date': next_day.strftime('%d-%m-%Y'),
            'txn_type': 'DEBIT',
            'mode': 'RTGS', # High value transfer
            'amount': layer_amt,
            'balance': 0,
            'counterparty': shell_company,
            'remarks': 'CONSULTANCY FEES',
            'branch_id': 'BR999',
            'typology_tag': 'Layering_Mule_Out'
        }
        transactions.append(txn_layer_out)
        
    return transactions

def main():
    # 1. Setup Base Data
    all_txns = []
    
    # 2. Inject Structuring
    structuring_acct = fake.bban()
    all_txns.extend(generate_structuring_scenario(structuring_acct, datetime(2023, 10, 1)))
    
    # 3. Inject Layering
    layering_root = fake.bban()
    mules = [fake.bban() for _ in range(3)] # 3 Mule accounts
    all_txns.extend(generate_layering_scenario(layering_root, mules, datetime(2023, 10, 5)))
    
    # 4. Generate Noise (Normal Transactions)
    # This ensures the AI has to 'search' for the signal amidst noise.
    print("[GEN] Generating 1,500 rows of background noise...")
    for _ in range(1500):
        txn = {
            'txn_id': uuid.uuid4().hex[:12].upper(),
            'account_no': fake.bban(),
            'txn_date': datetime(2023, 10, random.randint(1, 30)).strftime('%d-%m-%Y'),
            'txn_type': random.choice(['CREDIT', 'DEBIT']),
            'mode': random.choice(['UPI', 'NEFT', 'IMPS', 'CASH', 'POS']),
            'amount': random.randint(100, 15000), # Normal daily spending
            'balance': 0,
            'counterparty': fake.company() if random.random() > 0.5 else fake.name(),
            'remarks': random.choice(['GROCERIES', 'UTILITY BILL', 'SALARY', 'POS PURCHASE', 'FUNDS TRF']),
            'branch_id': f'BR{random.randint(100, 999)}',
            'typology_tag': 'Normal'
        }
        all_txns.append(txn)
        
    # 5. Create DataFrame and Export
    df = pd.DataFrame(all_txns)
    
    # Sort by Date for chronological consistency
    df['txn_date_obj'] = pd.to_datetime(df['txn_date'], format='%d-%m-%Y')
    df = df.sort_values(by='txn_date_obj')
    df = df.drop(columns=['txn_date_obj'])
    
    # Save
    filename = 'synthetic_banking_data.csv'
    df.to_csv(filename, index=False)
    print(f"Success: Generated {len(df)} transactions in {filename}")

if __name__ == "__main__":
    main()