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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PACKAGES_FILE = os.path.join(BASE_DIR, "packages.txt")
PURCHASES_FILE = os.path.join(BASE_DIR, "purchases.txt")
CUSTOMERS_FILE = os.path.join(BASE_DIR, "customers.txt")

# Global variable to track current logged-in customer
current_customer = None


def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def press_enter():
    """Wait for user to press Enter to continue."""
    input("\nPress Enter to continue...")


def print_header(title):
    """Print a formatted section header."""
    print("\n" + "=" * 50)
    print(f" {title}")
    print("=" * 50)


def print_separator(char="-", length=50):
    """Print a separator line."""
    print(char * length)


def get_valid_input(prompt, input_type=str, validation=None):
    """Get and validate user input."""
    while True:
        try:
            value = input(prompt).strip()
            if input_type == int:
                value = int(value)
            elif input_type == float:
                value = float(value)
            
            if validation and not validation(value):
                print("Invalid input. Please try again.")
                continue
            return value
        except ValueError:
            print(f"Please enter a valid {input_type.__name__}.")


# ==================== CUSTOMER AUTHENTICATION ====================

def load_customers():
    """Load customers from text file."""
    customers = []
    if not os.path.exists(CUSTOMERS_FILE):
        return customers
    with open(CUSTOMERS_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                parts = line.split("|")
                customers.append({
                    "username": parts[0],
                    "password": parts[1],
                    "balance": float(parts[2])
                })
    return customers


def save_customers(customers):
    """Save customers list back to text file."""
    with open(CUSTOMERS_FILE, "w") as f:
        for c in customers:
            f.write(f"{c['username']}|{c['password']}|{c['balance']:.2f}\n")


def find_customer(username):
    """Find a customer by username."""
    customers = load_customers()
    for c in customers:
        if c["username"] == username:
            return c
    return None


def update_customer_balance(username, new_balance):
    """Update a customer's balance."""
    customers = load_customers()
    for c in customers:
        if c["username"] == username:
            c["balance"] = new_balance
            save_customers(customers)
            return True
    return False


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
            
        elif choice == '3':
            return False
        else:
            print("Invalid option. Please try again.")
            press_enter()


def deposit_money():
    """Allow customer to deposit more money."""
    global current_customer
    
    if not current_customer:
        print("Please login first.")
        press_enter()
        return
    
    print_header("Deposit Money")
    print(f"Current balance: ${current_customer['balance']:.2f}")
    
    try:
        amount = get_valid_input("Enter deposit amount ($): ", float, 
                                 lambda x: x > 0)
    except ValueError:
        print("Invalid amount.")
        press_enter()
        return
    
    new_balance = current_customer["balance"] + amount
    update_customer_balance(current_customer["username"], new_balance)
    current_customer["balance"] = new_balance
    
    print(f"\nDeposit successful!")
    print(f"New balance: ${new_balance:.2f}")
    press_enter()


def view_account():
    """View customer account details."""
    global current_customer
    
    if not current_customer:
        print("Please login first.")
        press_enter()
        return
    
    print_header("My Account")
    print(f"Username   : {current_customer['username']}")
    print(f"Balance    : ${current_customer['balance']:.2f}")
    
    # Show purchase history for this customer
    if os.path.exists(PURCHASES_FILE):
        print("\n--- My Purchase History ---")
        print(f"{'Package':<15} {'Price':<10} {'Voucher':<10} {'Purchased':<20} {'Expires':<20}")
        print_separator()
        found = False
        with open(PURCHASES_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    parts = line.split("|")
                    if parts[0] == current_customer["username"]:
                        print(f"{parts[1]:<15} ${parts[2]:<9} {parts[3]:<10} {parts[4]:<20} {parts[5]:<20}")
                        print_separator()
                        found = True
        if not found:
            print("No purchases yet.")
    else:
        print("\nNo purchases yet.")
    
    press_enter()


# ==================== PACKAGE MANAGEMENT ====================

def load_packages():
    """Load packages from text file."""
    packages = []
    if not os.path.exists(PACKAGES_FILE):
        return packages
    with open(PACKAGES_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                parts = line.split("|")
                packages.append({
                    "name": parts[0],
                    "price": float(parts[1]),
                    "duration": int(parts[2])
                })
    return packages


def display_packages(affordable_only=False):
    """Show all available WiFi packages or only affordable ones."""
    packages = load_packages()
    
    if affordable_only and current_customer:
        packages = [p for p in packages if p["price"] <= current_customer["balance"]]
        print_header("Affordable WiFi Packages")
        print(f"Your balance: ${current_customer['balance']:.2f}")
    else:
        print_header("Available WiFi Packages")
    
    print(f"{'No.':<5} {'Package':<15} {'Duration':<12} {'Price':<10}")
    print_separator()
    
    if not packages:
        print("No packages available.")
        return []
    
    for i, p in enumerate(packages, 1):
        print(f"{i:<5} {p['name']:<15} {f"{p['duration']} mins":<12} ${p['price']:.2f}")
    return packages


# ==================== VOUCHER MANAGEMENT ====================

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
    
    while True:
        chars = string.ascii_uppercase + string.digits
        code = ''.join(random.choice(chars) for _ in range(8))
        if code not in existing_codes:
            return code


def save_purchase(customer_name, package_name, price, voucher_code,
                  purchase_time, expiration_time):
    """Save purchase record to text file."""
    with open(PURCHASES_FILE, "a") as f:
        f.write(f"{customer_name}|{package_name}|{price:.2f}|"
                f"{voucher_code}|{purchase_time}|{expiration_time}\n")


def print_receipt(customer_name, package_name, price, voucher_code,
                  purchase_time, expiration_time):
    """Print a formatted purchase receipt."""
    print_separator("=")
    print("           PURCHASE RECEIPT")
    print_separator("=")
    print(f"Customer  : {customer_name}")
    print(f"Package   : {package_name}")
    print(f"Price     : ${price:.2f}")
    print(f"Voucher   : {voucher_code}")
    print(f"Purchased : {purchase_time}")
    print(f"Expires   : {expiration_time}")
    print_separator("=")
    print("  Thank you for your purchase!")
    print("  Please keep your voucher code safe.")
    print_separator("=")


def purchase_package():
    """Handle the complete purchase flow for a customer."""
    global current_customer
    
    if not current_customer:
        print("Please login first.")
        press_enter()
        return
    
    packages = display_packages(affordable_only=True)

    if not packages:
        print("\nYou don't have enough balance for any package.")
        print("Please deposit more money first.")
        press_enter()
        return

    try:
        choice = get_valid_input("\nSelect package number(1/2/3/4): ", int,
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

    confirm = input("Confirm purchase? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Purchase cancelled.")
        press_enter()
        return

    # Check balance again
    if current_customer["balance"] < package["price"]:
        print("Insufficient balance. Please deposit more money.")
        press_enter()
        return

    try:
        # Deduct balance
        new_balance = current_customer["balance"] - package["price"]
        update_customer_balance(current_customer["username"], new_balance)
        current_customer["balance"] = new_balance
        
        # Generate voucher
        voucher_code = generate_unique_voucher_code()
        purchase_time = datetime.now()
        expiration_time = purchase_time + timedelta(minutes=package['duration'])

        purchase_time_str = purchase_time.strftime("%Y-%m-%d %H:%M:%S")
        expiration_time_str = expiration_time.strftime("%Y-%m-%d %H:%M:%S")

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


def check_voucher():
    """Check voucher status by code."""
    if not os.path.exists(PURCHASES_FILE):
        print("\nNo purchases have been made yet.")
        press_enter()
        return

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


def customer_menu():
    """Customer menu loop."""
    global current_customer
    
    # Force login/register first
    if not customer_login():
        return
    
    while True:
        clear_screen()
        print("\n" + "=" * 50)
        print(" " * 12 + "CUSTOMER MENU")
        print("=" * 50)
        print(f"  User: {current_customer['username']}")
        print(f"  Balance: ${current_customer['balance']:.2f}")
        print("=" * 50)
        print("  1. View Packages")
        print("  2. Buy Voucher")
        print("  3. Check Voucher Status")
        print("  4. Deposit Money")
        print("  5. View My Account")
        print("  6. Logout")
        print("=" * 50)

        choice = input("Select option: ").strip()

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
        elif choice == '6':
            current_customer = None
            print("Logged out successfully.")
            press_enter()
            break
        else:
            print("Invalid option. Please try again.")
            press_enter()
