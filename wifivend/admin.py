#!/usr/bin/env python3
"""
Administrator module for WiFiVend.
"""

import os
import shutil

# These imports provide the shared interface, validation, and file-storage tools
# used by the administrator features.
from common import (
    clear_screen, press_enter, print_header, print_centered, print_separator,
    get_valid_input, PACKAGES_FILE, PURCHASES_FILE, CUSTOMERS_FILE,
    load_packages, save_packages, get_next_package_id, is_duplicate_package,
    load_customers, save_customers, load_purchases, WifiPackage,
    load_admin_credentials, save_admin_credentials,
)

# This code defines reusable widths and labels for transaction displays.
TRANSACTION_HEADER = (
    f"{'Customer':<15} {'Package':<15} {'Price':<10} {'Voucher':<10} "
    f"{'Purchased':<20} {'Expires':<20}"
)
TRANSACTION_TABLE_WIDTH = len(TRANSACTION_HEADER)
COMPACT_TRANSACTION_WIDTH = 53


# This code checks the terminal width and selects either a wide table heading
# or a compact transaction layout that will not wrap on smaller screens.
def print_transaction_heading(title):
    """Print a transaction heading suited to the current terminal width."""
    is_wide = shutil.get_terminal_size(fallback=(80, 24)).columns >= TRANSACTION_TABLE_WIDTH
    width = TRANSACTION_TABLE_WIDTH if is_wide else COMPACT_TRANSACTION_WIDTH

    print_header(title, width=width)
    if is_wide:
        print(TRANSACTION_HEADER)
    print_separator(length=width)
    return is_wide, width


# This code prints one purchase record using the layout selected for the current
# terminal width.
def print_transaction(parts, is_wide, width):
    """Print one transaction without wrapping in narrow terminals."""
    if is_wide:
        print(
            f"{parts[0]:<15} {parts[1]:<15} ${parts[2]:<9} "
            f"{parts[3]:<10} {parts[4]:<20} {parts[5]:<20}"
        )
    else:
        print(f"Customer:  {parts[0]:<15} Voucher: {parts[3]}")
        print(f"Package:   {parts[1]:<15} Price: ${parts[2]}")
        print(f"Purchased: {parts[4]}")
        print(f"Expires:   {parts[5]}")
    print_separator(length=width)


# This code compares the entered administrator credentials with admin.txt and
# grants access only when both values match.
def admin_login():
    """Handle administrator login."""
    clear_screen()
    print_header("Administrator Login")
    username = input("Username: ").strip()
    password = input("Password: ").strip()

    # This block checks whether the entered login information is valid.
    creds = load_admin_credentials()
    if username == creds["username"] and password == creds["password"]:
        print("Login successful!")
        press_enter()
        return True
    else:
        print("Invalid username or password.")
        press_enter()
        return False


# This code loads all registered accounts and displays their usernames and
# current balances in a numbered table.
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


# This code lets the administrator select a customer, validate a replacement
# password, confirm the action, and save the updated account.
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

    # This block ensures the selected customer number exists in the list.
    try:
        choice = get_valid_input("\nEnter customer number to reset password: ", int,
                                 lambda x: 1 <= x <= len(customers))
    except ValueError:
        print("Invalid selection.")
        press_enter()
        return

    selected_customer = customers[choice - 1]
    print(f"\nSelected customer: {selected_customer['username']}")

    # This block prevents an empty password from being saved.
    new_password = input("Enter new password: ").strip()
    if not new_password:
        print("Password cannot be empty.")
        press_enter()
        return

    # This block requires confirmation before changing stored account data.
    confirm = input("Confirm password reset? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Password reset cancelled.")
        press_enter()
        return

    customers[choice - 1]["password"] = new_password
    if not save_customers(customers):
        print("Password reset could not be saved. Please try again.")
        press_enter()
        return
    print(f"Password for '{selected_customer['username']}' has been reset successfully.")
    press_enter()


# This code lets the administrator remove a customer account from customers.txt
# after selecting the account and confirming the permanent action. Existing
# purchases are intentionally kept for transaction history and sales reports.
def delete_customer_account():
    """Delete one customer account while preserving purchase records."""
    customers = load_customers()
    if not customers:
        print("\nNo registered customers found.")
        press_enter()
        return

    print_header("Delete Customer Account")
    print("Registered Customers:")
    for i, customer in enumerate(customers, 1):
        print(f"{i}. {customer['username']} - Balance: ${customer['balance']:.2f}")

    # This block ensures the administrator selects an existing customer.
    try:
        choice = get_valid_input(
            "\nEnter customer number to delete: ", int,
            lambda x: 1 <= x <= len(customers)
        )
    except ValueError:
        print("Invalid selection.")
        press_enter()
        return

    selected_customer = customers[choice - 1]
    print(f"\nSelected customer: {selected_customer['username']}")
    print("Purchase history will be preserved for transaction records.")

    # This block protects customer data by requiring explicit confirmation.
    confirm = input("Permanently delete this customer account? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Customer account deletion cancelled.")
        press_enter()
        return

    deleted_customer = customers.pop(choice - 1)
    if not save_customers(customers):
        print("Customer account could not be deleted. Please try again.")
        press_enter()
        return

    print(f"Customer account '{deleted_customer['username']}' deleted successfully.")
    print("The customer's purchase history was preserved.")
    press_enter()


# This code reads purchases.txt and displays every saved transaction.
def view_all_transactions():
    """Display all transactions."""
    if not os.path.exists(PURCHASES_FILE):
        print("\nNo transactions yet.")
        press_enter()
        return

    is_wide, table_width = print_transaction_heading("All Transactions")
    for parts in load_purchases():
        print_transaction(parts, is_wide, table_width)
    press_enter()


# This code performs a case-insensitive partial-name search and displays only
# transactions belonging to matching customers.
def search_transactions():
    """Search transactions by customer name."""
    if not os.path.exists(PURCHASES_FILE):
        print("\nNo transactions yet.")
        press_enter()
        return

    # This block normalizes the search text and scans each transaction record.
    search_name = input("Enter customer name to search: ").strip().lower()
    found = False

    is_wide, table_width = print_transaction_heading("Search Results")
    for parts in load_purchases():
        if search_name in parts[0].lower():
            print_transaction(parts, is_wide, table_width)
            found = True
    if not found:
        print("No transactions found for that customer.")
    press_enter()


# This code adds all purchase prices and counts the records to produce the
# administrator's sales summary.
def view_total_sales():
    """Calculate and display total sales."""
    total = 0.0
    count = 0
    for parts in load_purchases():
        total += float(parts[2])
        count += 1
    print_header("Total Sales Summary")
    print(f"Total Sales   : ${total:.2f}")
    print(f"Transactions  : {count}")
    press_enter()


# This code validates a new package's name, duration, and price, rejects a
# conflicting package, assigns a unique ID, and saves the new record.
def add_new_package():
    """Add a new WiFi package, rejecting duplicates by duration or price."""
    packages = load_packages()

    print_header("Add New WiFi Package")
    name = input("Package name (e.g., 3 Hours, Student Promo): ").strip()
    if not name:
        print("Package name cannot be empty.")
        press_enter()
        return

    # This block accepts only a positive duration and a nonnegative price.
    try:
        duration = get_valid_input("Duration in minutes: ", int, lambda x: x > 0)
        price = get_valid_input("Price ($): ", float, lambda x: x >= 0)
    except ValueError:
        print("Invalid input. Please try again.")
        press_enter()
        return

    # This block prevents duplicate package durations or prices.
    conflict = is_duplicate_package(packages, duration, price)
    if conflict:
        print(f"\nCannot add package: '{conflict['name']}' already uses the "
              f"same duration or price ({conflict['duration']} mins, "
              f"${conflict['price']:.2f}).")
        print("Please use a different duration and price.")
        press_enter()
        return

    # This block builds and permanently saves the valid package record.
    new_package = WifiPackage(
        get_next_package_id(packages), name, duration, price, "Active"
    )
    packages.append(new_package)
    if not save_packages(packages):
        print("Package could not be saved. Please try again.")
        press_enter()
        return
    print("Package added successfully.")
    press_enter()


# This code displays every package, including its stable ID, duration, price,
# and availability status.
def view_all_packages():
    """Display all packages in a clean, readable table."""
    packages = load_packages()

    print_header("View Packages")
    if not packages:
        print("No packages available.")
        press_enter()
        return

    print(f"{'ID':<4} {'Name':<20} {'Duration':<12} {'Price':<10} {'Status':<10}")
    print_separator()
    for p in packages:
        duration_str = f"{p['duration']} mins"
        print(f"{p['id']:<4} {p['name']:<20} {duration_str:<12} ${p['price']:<9.2f} {p['status']:<10}")
    press_enter()


# This code lets the administrator change a package's duration, price, or both
# while supporting cancellation and duplicate checking.
def edit_package():
    """Edit an existing package's duration and/or price. Supports cancelling."""
    packages = load_packages()
    if not packages:
        print("\nNo packages available.")
        press_enter()
        return

    print_header("Edit Package")
    for i, p in enumerate(packages, 1):
        print(f"{i}. [{p['status']}] {p['name']} - {p['duration']} mins - ${p['price']:.2f}")
    cancel_option = len(packages) + 1
    print(f"{cancel_option}. Cancel")

    # This block validates the chosen package and includes a cancel option.
    try:
        choice = get_valid_input("\nEnter package number to edit: ", int,
                                 lambda x: 1 <= x <= cancel_option)
    except ValueError:
        print("Invalid selection.")
        press_enter()
        return

    if choice == cancel_option:
        print("Edit cancelled.")
        press_enter()
        return

    # This block displays which fields of the selected package can be edited.
    package = packages[choice - 1]
    print(f"\nEditing: {package['name']} (ID {package['id']})")
    print("  1. Edit Duration")
    print("  2. Edit Price")
    print("  3. Edit Both")
    print("  4. Cancel")
    sub_choice = input("Select option: ").strip()

    new_duration = package["duration"]
    new_price = package["price"]

    # This block validates new values according to the selected edit mode.
    try:
        if sub_choice == '1':
            new_duration = get_valid_input("Enter new duration (minutes): ", int, lambda x: x > 0)
        elif sub_choice == '2':
            new_price = get_valid_input("Enter new price ($): ", float, lambda x: x >= 0)
        elif sub_choice == '3':
            new_duration = get_valid_input("Enter new duration (minutes): ", int, lambda x: x > 0)
            new_price = get_valid_input("Enter new price ($): ", float, lambda x: x >= 0)
        elif sub_choice == '4':
            print("Edit cancelled.")
            press_enter()
            return
        else:
            print("Invalid option. Edit cancelled.")
            press_enter()
            return
    except ValueError:
        print("Invalid input. Edit cancelled.")
        press_enter()
        return

    # This block makes sure the edited values do not conflict with another
    # package while excluding the current package from comparison.
    conflict = is_duplicate_package(packages, new_duration, new_price, exclude_id=package["id"])
    if conflict:
        print(f"\nCannot save: '{conflict['name']}' already uses the same "
              f"duration or price. Please choose different values.")
        press_enter()
        return

    # This block applies and saves the validated changes.
    package["duration"] = new_duration
    package["price"] = new_price
    if not save_packages(packages):
        print("Package changes could not be saved. Please try again.")
        press_enter()
        return
    print("Package updated successfully.")
    press_enter()


# This code lets the administrator select a package and permanently removes it
# only after receiving explicit confirmation.
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

    # This block ensures the selected package number is valid.
    try:
        choice = get_valid_input("\nEnter package number to delete: ", int,
                                 lambda x: 1 <= x <= len(packages))
    except ValueError:
        print("Invalid selection.")
        press_enter()
        return

    # This block protects against accidental deletion by asking for confirmation.
    confirm = input(f"Are you sure you want to delete '{packages[choice-1]['name']}'? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Delete cancelled.")
        press_enter()
        return

    deleted = packages.pop(choice - 1)
    if not save_packages(packages):
        print("Package could not be deleted. Please try again.")
        press_enter()
        return
    print(f"Package '{deleted['name']}' deleted successfully.")
    press_enter()


# This code verifies the current administrator password, accepts a new username,
# password, or both, and saves the change only after confirmation.
def change_admin_credentials():
    """Allow the admin to change username, password, or both."""
    creds = load_admin_credentials()

    print_header("Change Admin Credentials")
    print_centered(f"Current Username: {creds['username']}")

    # This block prevents unauthorized credential changes.
    current_password = input("\nEnter current password to continue: ").strip()
    if current_password != creds["password"]:
        print("Incorrect password. No changes were made.")
        press_enter()
        return

    print("\n  1. Change Username Only")
    print("  2. Change Password Only")
    print("  3. Change Both Username and Password")
    print("  4. Cancel")
    choice = input("Select option: ").strip()

    new_username = creds["username"]
    new_password = creds["password"]

    # This block validates the new credential fields for the chosen change type.
    if choice == '1':
        new_username = input("Enter new username: ").strip()
        if not new_username:
            print("Username cannot be empty. No changes were made.")
            press_enter()
            return
    elif choice == '2':
        new_password = input("Enter new password: ").strip()
        if not new_password:
            print("Password cannot be empty. No changes were made.")
            press_enter()
            return
    elif choice == '3':
        new_username = input("Enter new username: ").strip()
        new_password = input("Enter new password: ").strip()
        if not new_username or not new_password:
            print("Username/password cannot be empty. No changes were made.")
            press_enter()
            return
    elif choice == '4':
        print("Change cancelled.")
        press_enter()
        return
    else:
        print("Invalid option. No changes were made.")
        press_enter()
        return

    # This block requires final confirmation before overwriting admin.txt.
    confirm = input("Save new credentials? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Change cancelled.")
        press_enter()
        return

    if not save_admin_credentials(new_username, new_password):
        print("New credentials could not be saved. Please try again.")
        press_enter()
        return
    print("Admin credentials updated successfully.")
    press_enter()


# This code requires administrator login, displays all management choices, and
# routes each selection until the administrator returns to the main menu.
def admin_menu():
    """Administrator menu loop with login."""
    if not admin_login():
        return

    while True:
        clear_screen()
        print_header("Administrator Menu")
        print("  1. View All Transactions")
        print("  2. Search Transactions by Customer Name")
        print("  3. View Total Sales")
        print("  4. Add New WiFi Package")
        print("  5. Edit Package")
        print("  6. Delete Package")
        print("  7. View Packages")
        print("  8. View All Customers")
        print("  9. Reset Customer Password")
        print(" 10. Delete Customer Account")
        print(" 11. Change Admin Credentials")
        print(" 12. Back to Main Menu")
        print("=" * 50)

        choice = input("Select option: ").strip()

        # This block calls the administrator feature selected from the menu.
        if choice == '1':
            view_all_transactions()
        elif choice == '2':
            search_transactions()
        elif choice == '3':
            view_total_sales()
        elif choice == '4':
            add_new_package()
        elif choice == '5':
            edit_package()
        elif choice == '6':
            delete_package()
        elif choice == '7':
            view_all_packages()
        elif choice == '8':
            view_all_customers()
        elif choice == '9':
            reset_customer_password()
        elif choice == '10':
            delete_customer_account()
        elif choice == '11':
            change_admin_credentials()
        elif choice == '12':
            break
        else:
            print("Invalid option. Please try again.")
            press_enter()
