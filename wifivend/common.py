#!/usr/bin/env python3
import os

# This code builds absolute paths to all text files used as the system's
# storage, allowing every module to access the same files reliably.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PACKAGES_FILE = os.path.join(BASE_DIR, "packages.txt")
PURCHASES_FILE = os.path.join(BASE_DIR, "purchases.txt")
CUSTOMERS_FILE = os.path.join(BASE_DIR, "customers.txt")
ADMIN_FILE = os.path.join(BASE_DIR, "admin.txt")

DEFAULT_WIDTH = 50


# ==================== TERMINAL / UI HELPERS ====================

# This code clears the terminal using the correct command for the operating
# system currently running the application.
def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


# This code pauses the screen until the user is ready to continue.
def press_enter():
    """Wait for user to press Enter to continue."""
    input("\nPress Enter to continue...")


# This code prints a centered title surrounded by lines for consistent menus.
def print_header(title, width=DEFAULT_WIDTH):
    """Print a centered, formatted section header (used for every menu/title)."""
    print("\n" + "=" * width)
    print(title.center(width))
    print("=" * width)


# This code centers important information such as a username or balance.
def print_centered(text, width=DEFAULT_WIDTH):
    """Print a single line of text centered within the given width.
    Used for important standalone info (e.g. current balance, logged-in user).
    """
    print(text.center(width))


# This code prints a divider that makes tables and receipts easier to read.
def print_separator(char="-", length=DEFAULT_WIDTH):
    """Print a separator line."""
    print(char * length)


# This code keeps asking for input until the value has the requested data type
# and passes the optional validation rule.
def get_valid_input(prompt, input_type=str, validation=None):
    """Get and validate user input."""
    while True:
        try:
            value = input(prompt).strip()
            # This block converts the entered text into the requested type.
            if input_type == int:
                value = int(value)
            elif input_type == float:
                value = float(value)

            # This block rejects values that fail a supplied rule, such as a
            # price being negative or a menu number being out of range.
            if validation and not validation(value):
                print("Invalid input. Please try again.")
                continue
            return value
        except ValueError:
            print(f"Please enter a valid {input_type.__name__}.")


# ==================== CUSTOMER STORAGE ====================

# This code reads every customer record and converts each pipe-delimited line
# into a dictionary that is convenient for the rest of the program to use.
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


# This code writes the complete customer list back to customers.txt.
def save_customers(customers):
    """Save customers list back to text file."""
    with open(CUSTOMERS_FILE, "w") as f:
        for c in customers:
            f.write(f"{c['username']}|{c['password']}|{c['balance']:.2f}\n")


# This code searches the stored customers for an exact username match.
def find_customer(username):
    """Find a customer by username."""
    customers = load_customers()
    for c in customers:
        if c["username"] == username:
            return c
    return None


# This code changes one customer's balance and saves the updated records.
def update_customer_balance(username, new_balance):
    """Update a customer's balance."""
    customers = load_customers()
    for c in customers:
        if c["username"] == username:
            c["balance"] = new_balance
            save_customers(customers)
            return True
    return False

# This code reads the WiFi packages and supports both the old three-field file
# format and the current five-field format.
def load_packages():
    """Load packages from text file.

    Supports both the legacy 3-field format (name|price|duration) and the
    current 5-field format (id|name|duration|price|status). Legacy files
    are transparently upgraded and re-saved so IDs stay stable afterwards.
    """
    packages = []
    if not os.path.exists(PACKAGES_FILE):
        return packages

    # This block removes blank lines before processing package records.
    with open(PACKAGES_FILE, "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    legacy_format_detected = False
    for i, line in enumerate(lines, 1):
        parts = line.split("|")
        # This block converts a current-format line into a package dictionary.
        if len(parts) == 5:
            packages.append({
                "id": int(parts[0]),
                "name": parts[1],
                "duration": int(parts[2]),
                "price": float(parts[3]),
                "status": parts[4],
            })
        # This block converts older package records and supplies their missing
        # ID and status fields.
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

    # This block upgrades an old package file after it has been loaded.
    if legacy_format_detected:
        save_packages(packages)

    return packages


# This code saves packages using the current five-field storage format.
def save_packages(packages):
    """Save packages list back to text file (id|name|duration|price|status)."""
    with open(PACKAGES_FILE, "w") as f:
        for p in packages:
            f.write(f"{p['id']}|{p['name']}|{p['duration']}|{p['price']:.2f}|{p['status']}\n")


# This code creates an ID greater than every existing package ID.
def get_next_package_id(packages):
    """Return the next available package ID."""
    if not packages:
        return 1
    return max(p["id"] for p in packages) + 1


# This code prevents packages from sharing the same duration or price while
# allowing an edited package to be excluded from comparison with itself.
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

# This code reads the administrator login and creates default credentials when
# the credentials file is missing or empty.
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


# This code saves the administrator username and password to admin.txt.
def save_admin_credentials(username, password):
    """Save admin username/password back to text file."""
    with open(ADMIN_FILE, "w") as f:
        f.write(f"{username}|{password}\n")
