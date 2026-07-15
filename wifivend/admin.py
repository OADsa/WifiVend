#!/usr/bin/env python3
"""
Administrator module for WiFiVend.
"""

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PACKAGES_FILE = os.path.join(BASE_DIR, "packages.txt")
PURCHASES_FILE = os.path.join(BASE_DIR, "purchases.txt")
CUSTOMERS_FILE = os.path.join(BASE_DIR, "customers.txt")


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


def admin_login():
    """Handle administrator login."""
    clear_screen()
    print_header("Administrator Login")
    username = input("Username: ").strip()
    password = input("Password: ").strip()

    if username == "admin" and password == "admin123":
        print("Login successful!")
        press_enter()
        return True
    else:
        print("Invalid username or password.")
        press_enter()
        return False


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


def save_packages(packages):
    """Save packages list back to text file."""
    with open(PACKAGES_FILE, "w") as f:
        for p in packages:
            f.write(f"{p['name']}|{p['price']:.2f}|{p['duration']}\n")


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


def view_all_customers():
    """Display all registered customers."""
    customers = load_customers()
    if not customers:
        print("\nNo registered customers found.")
        press_enter()
        return

    print_header("All Registered Customers")
    print(f"{'No.':<5} {'Username':<15} {'Balance':<10}")
    print_separator()
    for i, c in enumerate(customers, 1):
        print(f"{i:<5} {c['username']:<15} ${c['balance']:.2f}")
    press_enter()


def reset_customer_password():
    """Reset a customer's password."""
    customers = load_customers()
    if not customers:
        print("\nNo registered customers found.")
        press_enter()
        return

    print_header("Reset Customer Password")
    print("Registered Customers:")
    for i, c in enumerate(customers, 1):
        print(f"{i}. {c['username']}")

    try:
        choice = get_valid_input("\nEnter customer number to reset password: ", int,
                                 lambda x: 1 <= x <= len(customers))
    except ValueError:
        print("Invalid selection.")
        press_enter()
        return

    selected_customer = customers[choice - 1]
    print(f"\nSelected customer: {selected_customer['username']}")

    new_password = input("Enter new password: ").strip()
    if not new_password:
        print("Password cannot be empty.")
        press_enter()
        return

    confirm = input("Confirm password reset? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Password reset cancelled.")
        press_enter()
        return

    customers[choice - 1]["password"] = new_password
    save_customers(customers)
    print(f"Password for '{selected_customer['username']}' has been reset successfully.")
    press_enter()


def view_all_transactions():
    """Display all transactions."""
    if not os.path.exists(PURCHASES_FILE):
        print("\nNo transactions yet.")
        press_enter()
        return

    print_header("All Transactions")
    print(f"{'Customer':<15} {'Package':<15} {'Price':<10} {'Voucher':<10}")
    print(f"{'Purchased':<20} {'Expires':<20}")
    print_separator()
    with open(PURCHASES_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                parts = line.split("|")
                print(f"{parts[0]:<15} {parts[1]:<15} ${parts[2]:<9} {parts[3]:<10}")
                print(f"{parts[4]:<20} {parts[5]:<20}")
                print_separator()
    press_enter()


def search_transactions():
    """Search transactions by customer name."""
    if not os.path.exists(PURCHASES_FILE):
        print("\nNo transactions yet.")
        press_enter()
        return

    search_name = input("Enter customer name to search: ").strip().lower()
    found = False

    print_header("Search Results")
    print(f"{'Customer':<15} {'Package':<15} {'Price':<10} {'Voucher':<10}")
    print(f"{'Purchased':<20} {'Expires':<20}")
    print_separator()
    with open(PURCHASES_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                parts = line.split("|")
                if search_name in parts[0].lower():
                    print(f"{parts[0]:<15} {parts[1]:<15} ${parts[2]:<9} {parts[3]:<10}")
                    print(f"{parts[4]:<20} {parts[5]:<20}")
                    print_separator()
                    found = True
    if not found:
        print("No transactions found for that customer.")
    press_enter()


def view_total_sales():
    """Calculate and display total sales."""
    total = 0.0
    count = 0
    if os.path.exists(PURCHASES_FILE):
        with open(PURCHASES_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    parts = line.split("|")
                    total += float(parts[2])
                    count += 1
    print_header("Total Sales Summary")
    print(f"Total Sales   : ${total:.2f}")
    print(f"Transactions  : {count}")
    press_enter()


def add_new_package():
    """Add a new WiFi package."""
    print_header("Add New WiFi Package")
    name = input("Package name (e.g., 3 Hours): ").strip()
    if not name:
        print("Package name cannot be empty.")
        press_enter()
        return

    try:
        duration = get_valid_input("Duration in minutes: ", int, lambda x: x > 0)
        price = get_valid_input("Price ($): ", float, lambda x: x >= 0)
    except ValueError:
        print("Invalid input. Please try again.")
        press_enter()
        return

    with open(PACKAGES_FILE, "a") as f:
        f.write(f"{name}|{price:.2f}|{duration}\n")
    print("Package added successfully.")
    press_enter()


def edit_package_price():
    """Edit the price of an existing package."""
    packages = load_packages()
    if not packages:
        print("\nNo packages available.")
        press_enter()
        return

    print_header("Edit Package Price")
    for i, p in enumerate(packages, 1):
        print(f"{i}. {p['name']} - ${p['price']:.2f} ({p['duration']} mins)")

    try:
        choice = get_valid_input("\nEnter package number to edit: ", int,
                                 lambda x: 1 <= x <= len(packages))
    except ValueError:
        print("Invalid selection.")
        press_enter()
        return

    try:
        new_price = get_valid_input(f"Enter new price for {packages[choice-1]['name']}: $",
                                    float, lambda x: x >= 0)
    except ValueError:
        print("Invalid price. Please enter a number.")
        press_enter()
        return

    packages[choice - 1]["price"] = new_price
    save_packages(packages)
    print("Package price updated successfully.")
    press_enter()


def delete_package():
    """Delete an existing package."""
    packages = load_packages()
    if not packages:
        print("\nNo packages available.")
        press_enter()
        return

    print_header("Delete Package")
    for i, p in enumerate(packages, 1):
        print(f"{i}. {p['name']} - ${p['price']:.2f} ({p['duration']} mins)")

    try:
        choice = get_valid_input("\nEnter package number to delete: ", int,
                                 lambda x: 1 <= x <= len(packages))
    except ValueError:
        print("Invalid selection.")
        press_enter()
        return

    confirm = input(f"Are you sure you want to delete '{packages[choice-1]['name']}'? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Delete cancelled.")
        press_enter()
        return

    deleted = packages.pop(choice - 1)
    save_packages(packages)
    print(f"Package '{deleted['name']}' deleted successfully.")
    press_enter()


def admin_menu():
    """Administrator menu loop with login."""
    if not admin_login():
        return

    while True:
        clear_screen()
        print("\n" + "=" * 50)
        print(" " * 12 + "ADMINISTRATOR MENU")
        print("=" * 50)
        print("  1. View All Transactions")
        print("  2. Search Transactions by Customer Name")
        print("  3. View Total Sales")
        print("  4. Add New WiFi Package")
        print("  5. Edit Package Price")
        print("  6. Delete Package")
        print("  7. View All Customers")
        print("  8. Reset Customer Password")
        print("  9. Back to Main Menu")
        print("=" * 50)

        choice = input("Select option: ").strip()

        if choice == '1':
            view_all_transactions()
        elif choice == '2':
            search_transactions()
        elif choice == '3':
            view_total_sales()
        elif choice == '4':
            add_new_package()
        elif choice == '5':
            edit_package_price()
        elif choice == '6':
            delete_package()
        elif choice == '7':
            view_all_customers()
        elif choice == '8':
            reset_customer_password()
        elif choice == '9':
            break
        else:
            print("Invalid option. Please try again.")
            press_enter()
