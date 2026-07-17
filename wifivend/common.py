#!/usr/bin/env python3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PACKAGES_FILE = os.path.join(BASE_DIR, "packages.txt")
PURCHASES_FILE = os.path.join(BASE_DIR, "purchases.txt")
CUSTOMERS_FILE = os.path.join(BASE_DIR, "customers.txt")
ADMIN_FILE = os.path.join(BASE_DIR, "admin.txt")

DEFAULT_WIDTH = 50


# ==================== TERMINAL / UI HELPERS ====================

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def press_enter():
    """Wait for user to press Enter to continue."""
    input("\nPress Enter to continue...")


def print_header(title, width=DEFAULT_WIDTH):
    """Print a centered, formatted section header (used for every menu/title)."""
    print("\n" + "=" * width)
    print(title.center(width))
    print("=" * width)


def print_centered(text, width=DEFAULT_WIDTH):
    """Print a single line of text centered within the given width.
    Used for important standalone info (e.g. current balance, logged-in user).
    """
    print(text.center(width))


def print_separator(char="-", length=DEFAULT_WIDTH):
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


# ==================== CUSTOMER STORAGE ====================

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

def load_packages():
    """Load packages from text file.

    Supports both the legacy 3-field format (name|price|duration) and the
    current 5-field format (id|name|duration|price|status). Legacy files
    are transparently upgraded and re-saved so IDs stay stable afterwards.
    """
    packages = []
    if not os.path.exists(PACKAGES_FILE):
        return packages

    with open(PACKAGES_FILE, "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    legacy_format_detected = False
    for i, line in enumerate(lines, 1):
        parts = line.split("|")
        if len(parts) == 5:
            packages.append({
                "id": int(parts[0]),
                "name": parts[1],
                "duration": int(parts[2]),
                "price": float(parts[3]),
                "status": parts[4],
            })
        elif len(parts) == 3:
            # Legacy format: name|price|duration
            legacy_format_detected = True
            packages.append({
                "id": i,
                "name": parts[0],
                "duration": int(parts[2]),
                "price": float(parts[1]),
                "status": "Active",
            })

    if legacy_format_detected:
        save_packages(packages)

    return packages


def save_packages(packages):
    """Save packages list back to text file (id|name|duration|price|status)."""
    with open(PACKAGES_FILE, "w") as f:
        for p in packages:
            f.write(f"{p['id']}|{p['name']}|{p['duration']}|{p['price']:.2f}|{p['status']}\n")


def get_next_package_id(packages):
    """Return the next available package ID."""
    if not packages:
        return 1
    return max(p["id"] for p in packages) + 1


def is_duplicate_package(packages, duration, price, exclude_id=None):
    """Return the conflicting package dict if a package with the same
    duration OR the same price already exists, else None.

    `exclude_id` lets an edit operation skip comparing a package against
    itself. This same check works for any future package (including named
    promos), since it only looks at duration/price, never the name.
    """
    for p in packages:
        if p["id"] == exclude_id:
            continue
        if p["duration"] == duration or p["price"] == price:
            return p
    return None


# ==================== ADMIN CREDENTIAL STORAGE ====================

def load_admin_credentials():
    """Load admin username/password, creating the default file if missing."""
    if not os.path.exists(ADMIN_FILE):
        save_admin_credentials("admin", "admin123")
        return {"username": "admin", "password": "admin123"}

    with open(ADMIN_FILE, "r") as f:
        line = f.readline().strip()

    if not line:
        save_admin_credentials("admin", "admin123")
        return {"username": "admin", "password": "admin123"}

    parts = line.split("|")
    return {"username": parts[0], "password": parts[1]}


def save_admin_credentials(username, password):
    """Save admin username/password back to text file."""
    with open(ADMIN_FILE, "w") as f:
        f.write(f"{username}|{password}\n")