# Receipt Processing Script

## Overview

This script is designed to process and match transactions from a CSV file with corresponding receipt files in a specified directory. It provides options to list matching transactions, partial matches, transactions without matches, and receipts that have not been used in matching.

The original purpose of this script was to aid in end-of-year financial audits for a not-for-profit organisation. A receipt is required for every bank (debit) transaction, and this script helps track down missing ones. This script allows an organisation to simply store all their receipts in a folder/ google drive, rather than using expensive financial management tools.  

## Requirements

- Python 3.x
- Required Python packages (listed in the script)
- CSV file containing transactions to match
- Top-level folder containing receipt files

## Usage

```bash
python receipt_processing_script.py --transactions [TRANSACTIONS_CSV] --receipts [RECEIPTS_DIRECTORY] [OPTIONS]
```

### Options

- `--list_matching`: Display transactions with matching receipts.
- `--list_not_matching`: Display transactions without matching receipts.
- `--list_not_used_receipts`: Display receipts that have not been used in matching.
- `--include_stripe`: Include transactions with "STRIPE" in the description.
- `--include_credit`: Include credit transactions.
- `--list_errors`: Display any filename errors encountered during processing.

## Data Formats

### Transaction CSV Format

The CSV file should have the following columns:

1. Account
2. Date (DD/MM/YYYY)
3. Narrative
4. Debit amount
5. Credit amount
6. Balance
7. Categories
8. Serial

### Receipt File Naming

Receipt files should be named with the following format:

`[DATE] - [NAME] - [DESCRIPTION] - [AMOUNT] - [STATUS] - [(Optional) Note].[fileformat]`

## Classes

### `Receipt`

- Represents a receipt with attributes like date, name, description, amount, status, path, and filename.
- Provides a method to format the object as a string.

### `Transaction`

- Represents a transaction with attributes like account, date, narrative, debit, credit, balance, categories, and serial.
- Provides a method to format the object as a string.

## Functions

### `readTransactions(fileName)`

- Reads transactions from a CSV file and returns a list of transaction objects.

### `readReceipts(directory)`

- Reads receipts from a specified directory and returns a list of receipt objects and a list of errors encountered during processing.

### `color_print(color, string)`

- Prints a colored string to the console using ANSI escape codes.

## How to Run

1. Ensure Python is installed on your system.
2. Open a terminal and navigate to the directory containing the script.
3. Run the script with the appropriate command-line arguments.

## Examples

- Display matching transactions:

```bash
python receipt_processing_script.py --transactions transactions.csv --receipts receipts_directory --list_matching
```

- Display transactions without matching receipts:

```bash
python receipt_processing_script.py --transactions transactions.csv --receipts receipts_directory --list_not_matching
```

- Display receipts that have not been used:

```bash
python receipt_processing_script.py --transactions transactions.csv --receipts receipts_directory --list_not_used_receipts
```

- Display errors encountered during processing:

```bash
python receipt_processing_script.py --transactions transactions.csv --receipts receipts_directory --list_errors
```