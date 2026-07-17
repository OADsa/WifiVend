#!/usr/bin/env python3
"""
Customer module for WiFiVend.
Handles customer login/registration, balance management,
package viewing, purchasing, and voucher generation.
"""

import os
import random
import string
from datetime import datetime, timedelta

# These imports provide shared display, validation, storage, and package tools.
from common import (
    clear_screen, press_enter, print_header, print_centered, print_separator,
    get_valid_input, PURCHASES_FILE,
    load_customers, save_customers, find_customer, update_customer_balance,
    load_packages,
)

# Global variable to track current logged-in customer
current_customer = None


# ==================== CUSTOMER AUTHENTICATION ====================

# This code displays the customer access screen and handles both existing-user
# login and new-account registration.
def customer_login():
    """Handle customer login or registration."""
    global current_customer

    while True:
        clear_screen()
        print_header("Customer Login / Register")
        print("  1. Login")
        print("  2. Register")
        print("  3. Back to Main Menu")
        print("=" * 50)

        choice = input("Select option: ").strip()

        # This block validates an existing customer's username and password.
        if choice == '1':
            username = input("Enter username: ").strip()
            password = input("Enter password: ").strip()

            customer = find_customer(username)
            if customer and customer["password"] == password:
                current_customer = customer
                print(f"\nWelcome back, {username}!")
                print(f"Your current balance: ${customer['balance']:.2f}")
                press_enter()
                return True
            else:
                print("Invalid username or password.")
                press_enter()

        # This block validates registration details, saves the new account,
        # and immediately signs in the newly registered customer.
        elif choice == '2':
            username = input("Choose a username: ").strip()
            if not username:
                print("Username cannot be empty.")
                press_enter()
                continue

            if find_customer(username):
                print("Username already exists. Please choose another.")
                press_enter()
                continue

            password = input("Choose a password: ").strip()
            if not password:
                print("Password cannot be empty.")
                press_enter()
                continue

            # This block ensures the starting deposit is numeric and is not
            # less than zero.
            try:
                initial_deposit = get_valid_input("Enter initial deposit amount ($): ",
                                                   float, lambda x: x >= 0)
            except ValueError:
                print("Invalid amount.")
                press_enter()
                continue

            customers = load_customers()
            customers.append({
                "username": username,
                "password": password,
                "balance": initial_deposit
            })
            save_customers(customers)

            current_customer = find_customer(username)
            print(f"\nAccount created successfully! Welcome, {username}!")
            print(f"Your balance: ${initial_deposit:.2f}")
            press_enter()
            return True

        # This block returns to the main menu without logging anyone in.
        elif choice == '3':
            return False
        else:
            print("Invalid option. Please try again.")
            press_enter()


# This code accepts a positive deposit or lets the customer cancel, then saves
# the new account balance in customers.txt.
def deposit_money():
    """Allow customer to deposit more money. Supports cancelling the deposit."""
    global current_customer

    # This check prevents balance changes when nobody is logged in.
    if not current_customer:
        print("Please login first.")
        press_enter()
        return

    print_header("Deposit Money")
    print_centered(f"Current balance: ${current_customer['balance']:.2f}")

    # This block validates the deposit and continues asking after bad input.
    while True:
        raw = input("\nEnter deposit amount ($) or type 'C' to cancel: ").strip()
        if raw.lower() in ('c', 'cancel'):
            print("\nDeposit cancelled. Your balance is unchanged.")
            press_enter()
            return

        try:
            amount = float(raw)
        except ValueError:
            print("Please enter a valid amount, or 'C' to cancel.")
            continue

        if amount <= 0:
            print("Amount must be greater than zero.")
            continue

        break

    # This block updates both the saved record and the current session copy.
    new_balance = current_customer["balance"] + amount
    update_customer_balance(current_customer["username"], new_balance)
    current_customer["balance"] = new_balance

    print(f"\nDeposit successful!")
    print(f"New balance: ${new_balance:.2f}")
    press_enter()


# This code displays the signed-in customer's details and filters the purchase
# file so only that customer's transaction history is shown.
def view_account():
    """View customer account details."""
    global current_customer

    # This check stops unauthenticated users from opening an account page.
    if not current_customer:
        print("Please login first.")
        press_enter()
        return

    print_header("My Account")
    print(f"Username   : {current_customer['username']}")
    print(f"Balance    : ${current_customer['balance']:.2f}")

    # Show purchase history for this customer
    # This block reads and displays matching purchase records when the file is
    # available; otherwise it reports that there is no history yet.
    if os.path.exists(PURCHASES_FILE):
        print("\n           --- My Purchase History ---")
        history_header = (
            f"{'Package':<15} {'Price':<10} {'Voucher':<10} "
            f"{'Purchased':<20} {'Expires':<20}"
        )
        print(history_header)
        print_separator(length=len(history_header))
        found = False
        with open(PURCHASES_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    parts = line.split("|")
                    if parts[0] == current_customer["username"]:
                        print(f"{parts[1]:<15} ${parts[2]:<9} {parts[3]:<10} {parts[4]:<20} {parts[5]:<20}")
                        print_separator(length=len(history_header))
                        found = True
        if not found:
            print("No purchases yet.")
    else:
        print("\nNo purchases yet.")

    press_enter()


# ==================== PACKAGE MANAGEMENT ====================

# This code loads active packages, optionally filters out packages the current
# customer cannot afford, and displays the result as a numbered table.
def display_packages(affordable_only=False):
    """Show all available (Active) WiFi packages, or only affordable ones."""
    packages = load_packages()
    # Customers should only ever see packages the admin has marked Active.
    packages = [p for p in packages if p.get("status", "Active") == "Active"]

    # This block applies the balance filter during the purchase process.
    if affordable_only and current_customer:
        packages = [p for p in packages if p["price"] <= current_customer["balance"]]
        print_header("Affordable WiFi Packages")
        print_centered(f"Your balance: ${current_customer['balance']:.2f}")
    else:
        print_header("Available WiFi Packages")

    print(f"{'No.':<5} {'Package':<15} {'Duration':<12} {'Price':<10}")
    print_separator()

    # This block handles the case where there is nothing available to display.
    if not packages:
        print("No packages available.")
        return []

    for i, p in enumerate(packages, 1):
        duration_str = f"{p['duration']} mins"
        print(f"{i:<5} {p['name']:<15} {duration_str:<12} ${p['price']:.2f}")
    return packages


# ==================== VOUCHER MANAGEMENT ====================

# This code gathers all existing voucher codes, then creates random codes until
# it finds an unused eight-character combination.
def generate_unique_voucher_code():
    """Generate a unique 8-character alphanumeric voucher code."""
    existing_codes = set()
    if os.path.exists(PURCHASES_FILE):
        with open(PURCHASES_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    parts = line.split("|")
                    existing_codes.add(parts[3])

    # This loop guarantees that the returned voucher is unique in purchases.txt.
    while True:
        chars = string.ascii_uppercase + string.digits
        code = ''.join(random.choice(chars) for _ in range(8))
        if code not in existing_codes:
            return code


# This code appends one completed purchase to the permanent transaction file.
def save_purchase(customer_name, package_name, price, voucher_code,
                  purchase_time, expiration_time):
    """Save purchase record to text file."""
    with open(PURCHASES_FILE, "a") as f:
        f.write(f"{customer_name}|{package_name}|{price:.2f}|"
                f"{voucher_code}|{purchase_time}|{expiration_time}\n")


# This code formats the important purchase and voucher details as a receipt.
def print_receipt(customer_name, package_name, price, voucher_code,
                  purchase_time, expiration_time):
    """Print a formatted purchase receipt."""
    print_separator("=")
    print_centered("PURCHASE RECEIPT")
    print_separator("=")
    print(f"Customer  : {customer_name}")
    print(f"Package   : {package_name}")
    print(f"Price     : ${price:.2f}")
    print(f"Voucher   : {voucher_code}")
    print(f"Purchased : {purchase_time}")
    print(f"Expires   : {expiration_time}")
    print_separator("=")
    print_centered("Thank you for your purchase!")
    print_centered("Please keep your voucher code safe.")
    print_separator("=")


# This code manages the full buying process: authentication, affordable-package
# selection, confirmation, payment, voucher generation, storage, and receipt.
def purchase_package():
    """Handle the complete purchase flow for a customer."""
    global current_customer

    # This check prevents a purchase when no customer is signed in.
    if not current_customer:
        print("Please login first.")
        press_enter()
        return

    packages = display_packages(affordable_only=True)

    # This block stops the purchase if the balance cannot cover any package.
    if not packages:
        print("\nYou don't have enough balance for any package.")
        print("Please deposit more money first.")
        press_enter()
        return

    # This block ensures the customer selects a package number in the list.
    try:
        choice = get_valid_input("\nSelect package number (e.g. 1/2/3...): ", int,
                                 lambda x: 1 <= x <= len(packages))
    except ValueError:
        print("Invalid selection.")
        press_enter()
        return

    package = packages[choice - 1]

    print(f"\n--- Purchase Summary ---")
    print(f"Package   : {package['name']}")
    print(f"Price     : ${package['price']:.2f}")
    print(f"Duration  : {package['duration']} minutes")
    print(f"Balance   : ${current_customer['balance']:.2f}")

    # This block gives the customer a final opportunity to cancel the order.
    confirm = input("Confirm purchase? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Purchase cancelled.")
        press_enter()
        return

    # This code checks the balance again immediately before charging the account.
    if current_customer["balance"] < package["price"]:
        print("Insufficient balance. Please deposit more money.")
        press_enter()
        return

    # This block completes the payment and voucher transaction while reporting
    # unexpected errors instead of closing the entire application.
    try:
        # This code deducts the price from the saved and current balances.
        new_balance = current_customer["balance"] - package["price"]
        update_customer_balance(current_customer["username"], new_balance)
        current_customer["balance"] = new_balance

        # This code generates the voucher and calculates its expiration date.
        voucher_code = generate_unique_voucher_code()
        purchase_time = datetime.now()
        expiration_time = purchase_time + timedelta(minutes=package['duration'])

        # This code converts both times into a consistent storage/display format.
        purchase_time_str = purchase_time.strftime("%Y-%m-%d %H:%M:%S")
        expiration_time_str = expiration_time.strftime("%Y-%m-%d %H:%M:%S")

        # This code permanently stores the purchase before printing its receipt.
        save_purchase(current_customer["username"], package['name'], package['price'],
                      voucher_code, purchase_time_str, expiration_time_str)

        clear_screen()
        print_receipt(current_customer["username"], package['name'], package['price'],
                      voucher_code, purchase_time_str, expiration_time_str)
        print(f"\nRemaining balance: ${new_balance:.2f}")
        press_enter()
    except Exception as e:
        print(f"An error occurred during purchase: {e}")
        press_enter()


# This code looks up an entered voucher code and displays its owner, package,
# price, purchase time, and expiration time when found.
def check_voucher():
    """Check voucher status by code."""
    if not os.path.exists(PURCHASES_FILE):
        print("\nNo purchases have been made yet.")
        press_enter()
        return

    # This block normalizes the code to uppercase and searches every purchase.
    code = input("Enter voucher code: ").strip().upper()
    found = False
    with open(PURCHASES_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                parts = line.split("|")
                if parts[3] == code:
                    print_header("Voucher Details")
                    print(f"Customer  : {parts[0]}")
                    print(f"Package   : {parts[1]}")
                    print(f"Price     : ${parts[2]}")
                    print(f"Purchased : {parts[4]}")
                    print(f"Expires   : {parts[5]}")
                    found = True
                    break
    if not found:
        print("Voucher not found.")
    press_enter()


# This code controls the signed-in customer menu and calls the function that
# corresponds to each selected option until the customer logs out.
def customer_menu():
    """Customer menu loop."""
    global current_customer

    # This code requires a successful login or registration before continuing.
    if not customer_login():
        return

    while True:
        clear_screen()
        print_header("Customer Menu")
        print_centered(f"User: {current_customer['username']}")
        print_centered(f"Balance: ${current_customer['balance']:.2f}")
        print("=" * 50)
        print("  1. View Packages")
        print("  2. Buy Voucher")
        print("  3. Check Voucher Status")
        print("  4. Deposit Money")
        print("  5. View My Account")
        print("  6. Logout")
        print("=" * 50)

        choice = input("Select option: ").strip()

        # This block routes each valid menu choice to its customer feature.
        if choice == '1':
            clear_screen()
            display_packages()
            press_enter()
        elif choice == '2':
            purchase_package()
        elif choice == '3':
            check_voucher()
        elif choice == '4':
            deposit_money()
        elif choice == '5':
            view_account()
        # This block clears the active session before returning to the main menu.
        elif choice == '6':
            current_customer = None
            print("Logged out successfully.")
            press_enter()
            break
        else:
            print("Invalid option. Please try again.")
            press_enter()
