"""
Receipt Processing Script
Jaric Thorning, 2023
"""

import csv
import re
from os import walk, path
from argparse import ArgumentParser
from datetime import datetime


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def color_print(color, string):
    print(color + str(string) + bcolors.ENDC)


class Receipt:
    def __init__(self, date, name, description, amount, status, path, filename):
        self.name = name

        try:
            self.date = datetime.strptime(date.strip(), "%Y.%m.%d")
        except:
            print(
                f"Incorrect date format (YYYY.MM.DD) in receipt {description}: ", date
            )
            exit()

        self.description = description

        amountString = amount.strip().strip("$")
        self.amount = float(amountString)

        self.status = status
        self.path = path
        self.filename = filename

        pattern = r"\(\d{4}\.\d{2}\.\d{2}\)"
        match = re.search(pattern, status)

        if match:
            date_str = match.group().replace("(", "").replace(")", "")
            self.paidDate = datetime.strptime(date_str, "%Y.%m.%d")
        else:
            self.paidDate = None

    def __str__(self):
        return f"{self.filename}"


class Transaction:
    def __init__(
        self, account, date, narrative, debit, credit, balance, categories, serial
    ):
        try:
            self.date = datetime.strptime(date.strip(), "%d/%m/%Y")
        except:
            print(
                f"Incorrect date format ([D]D/MM/YY) in transaction {narrative}: ", date
            )
            exit()

        if debit:
            self.amount = float(debit)
            self.type = "debit"

        if credit:
            self.amount = float(credit)
            self.type = "credit"

        self.description = narrative
        self.balance = balance

    def __str__(self):
        return f"{self.date}, {self.amount}, {self.description}"


def readTransactions(fileName):
    with open(fileName, "r") as readFile:
        reader = csv.reader(readFile)
        lines = list(reader)

    transactions = []
    for line in lines[1:]:
        newTransaction = Transaction(*line)
        transactions.append(newTransaction)

    return transactions


def readReceipts(directory):
    receipts = []
    errors = []
    for dirpath, dirnames, filenames in walk(directory, followlinks=True):
        for filename in filenames:
            if filename == "Icon\r" or filename == ".DS_Store":
                continue
            items = filename.split("-")
            if len(items) == 5 or len(items) == 6:
                receipts.append(
                    Receipt(
                        items[0],
                        items[1],
                        items[2],
                        items[3],
                        items[4],
                        dirpath,
                        filename,
                    )
                )
            else:
                color_print(bcolors.FAIL, f"FILENAME ERROR: {filename}")
                errors.append(filename)
    return receipts, errors


def main():
    parser = ArgumentParser()
    parser.add_argument(
        "--transactions",
        required=True,
        help="CSV file containing transactions to match",
    )
    parser.add_argument(
        "--receipts", required=True, help="Top level folder containing receipts"
    )
    parser.add_argument("--list_matching", action="store_true")
    parser.add_argument("--list_not_matching", action="store_true")
    parser.add_argument("--list_not_used_receipts", action="store_true")
    parser.add_argument("--include_stripe", action="store_true")
    parser.add_argument("--include_credit", action="store_true")
    parser.add_argument("--list_errors", action="store_true")

    args = parser.parse_args()

    if not path.isfile(args.transactions):
        print(f"{args.transactions} doesn't exist.")

    if not path.isdir(args.receipts):
        print(f"{args.receipts} doesn't exist or isn't a directory.")

    transactions = readTransactions(args.transactions)
    receipts, errors = readReceipts(args.receipts)

    processed_transactions = {}

    for t in transactions:
        if t.type == "credit" and not args.include_credit:
            # print(f"Excluding - {t}")
            continue

        if not args.include_stripe and "STRIPE" in t.description:
            continue

        processed_transactions[t] = {"matches": [], "partial_matches": []}
        for r in receipts:
            if r.amount == t.amount:
                if r.paidDate == t.date:
                    processed_transactions[t]["matches"].append(r)
                else:
                    processed_transactions[t]["partial_matches"].append(r)

    print()

    if args.list_matching:
        for t in processed_transactions.keys():
            matches = processed_transactions[t]["matches"]
            partials = processed_transactions[t]["partial_matches"]

            if len(matches) + len(partials) == 0:
                continue

            color_print(bcolors.BOLD, f"Transaction - {t}")

            if len(matches) + len(partials) > 1:
                color_print(
                    bcolors.WARNING,
                    f"WARNING - Multiple matching receipts with amount {t.amount} found - ",
                )

            if len(matches) > 0:
                print(f"Matches: ")
                for receipt in matches:
                    color_print(bcolors.OKGREEN, receipt)
            if len(partials) > 0:
                print(f"Partial Matches (only amount, not paidDate): ")
                for receipt in partials:
                    color_print(bcolors.OKBLUE, receipt)
            print()
        exit()

    if args.list_not_matching:
        print("No matching or partial matching receipt:")
        for t in processed_transactions.keys():
            matches = processed_transactions[t]["matches"]
            partials = processed_transactions[t]["partial_matches"]
            if len(matches) + len(partials) == 0:
                color_print(bcolors.FAIL, f"Transaction - {t}")
        exit()

    if args.list_not_used_receipts:
        print("Receipts not used:")
        for r in receipts:
            used = False
            for t in processed_transactions.keys():
                matches = processed_transactions[t]["matches"]
                partials = processed_transactions[t]["partial_matches"]
                if r in matches or r in partials:
                    used = True
                    break
            if not used:
                print(f"Receipt - {r}")
            exit()

    if args.list_errors:
        for error in errors:
            color_print(bcolors.FAIL, error)
        exit()

    # Default - List all color coded

    total_matches = 0
    total_partials = 0
    total_not_matching = 0
    total_multiple_match = 0
    for t in processed_transactions.keys():
        matches = processed_transactions[t]["matches"]
        partials = processed_transactions[t]["partial_matches"]

        if len(matches) + len(partials) == 0:
            color_print(bcolors.FAIL, f"No Match - {t}")
            total_not_matching += 1

        elif len(matches) + len(partials) > 1:
            if len(matches) == 1:
                # If only one match, then assume is correct
                color_print(bcolors.OKGREEN, f"Match - {t}")
                total_matches += 1
            else:
                color_print(bcolors.WARNING, f"Multiple Match - {t}")
                total_multiple_match += 1

        elif len(matches) == 1:
            color_print(bcolors.OKGREEN, f"Match - {t}")
            total_matches += 1

        elif len(partials) == 1:
            color_print(bcolors.OKBLUE, f"Partial Match - {t}")
            total_partials += 1

    # Print Summary
    print()
    color_print(
        bcolors.BOLD,
        f"Total Debit Transactions - {len(processed_transactions)}  Total Receipts - {len(receipts)}",
    )
    color_print(bcolors.OKGREEN, f"Matching - {total_matches}")
    color_print(bcolors.OKBLUE, f"Partial Matching - {total_partials}")
    color_print(bcolors.WARNING, f"Multiple Match - {total_not_matching}")
    color_print(bcolors.FAIL, f"Not Matching - {total_multiple_match}")
    color_print(bcolors.FAIL, f"Receipt Read Errors - {len(errors)}")


if __name__ == "__main__":
    main()
