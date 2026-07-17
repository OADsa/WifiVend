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


# ==================== CLASSES AND OBJECTS ====================

# This class represents one customer account. Its methods convert between an
# object and the pipe-delimited format used in customers.txt.
class Customer:
    """Store and manage one customer's account data."""

    def __init__(self, username, password, balance):
        self.username = username
        self.password = password
        self.balance = float(balance)

    @classmethod
    def from_record(cls, record):
        """Create a Customer object from one text-file record."""
        parts = record.split("|")
        if len(parts) != 3:
            raise ValueError("customer record must contain 3 fields")
        return cls(parts[0], parts[1], float(parts[2]))

    def to_record(self):
        """Convert this object into the format stored in customers.txt."""
        return f"{self.username}|{self.password}|{self.balance:.2f}"

    # These methods preserve the existing dictionary-style access used by the
    # menus while the stored account is now a real Customer object.
    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)


# This class represents one WiFi package and contains the behavior needed to
# create the object from either the current or legacy packages.txt format.
class WifiPackage:
    """Store and manage one WiFi package's data."""

    def __init__(self, package_id, name, duration, price, status="Active"):
        self.id = int(package_id)
        self.name = name
        self.duration = int(duration)
        self.price = float(price)
        self.status = status

    @classmethod
    def from_record(cls, record, legacy_id=None):
        """Create a WifiPackage object from a current or legacy record."""
        parts = record.split("|")
        if len(parts) == 5:
            return cls(parts[0], parts[1], parts[2], parts[3], parts[4])
        if len(parts) == 3 and legacy_id is not None:
            return cls(legacy_id, parts[0], parts[2], parts[1], "Active")
        raise ValueError("package record must contain 3 or 5 fields")

    def to_record(self):
        """Convert this object into the current packages.txt format."""
        return f"{self.id}|{self.name}|{self.duration}|{self.price:.2f}|{self.status}"

    # These methods let the unchanged menus access package objects using the
    # same keys they previously used with dictionaries.
    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def get(self, key, default=None):
        return getattr(self, key, default)


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

# This code reads every valid customer record and creates a Customer object.
# Invalid records are reported and skipped instead of crashing the program.
def load_customers():
    """Load customers from text file."""
    customers = []
    if not os.path.exists(CUSTOMERS_FILE):
        return customers
    try:
        with open(CUSTOMERS_FILE, "r", encoding="utf-8") as f:
            for line_number, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    customers.append(Customer.from_record(line))
                except (ValueError, TypeError) as error:
                    print(f"Warning: skipped invalid customer record on line "
                          f"{line_number}: {error}")
    except OSError as error:
        print(f"Unable to read customer data: {error}")
    return customers


# This code writes the complete customer list back to customers.txt.
def save_customers(customers):
    """Save customers list back to text file."""
    try:
        with open(CUSTOMERS_FILE, "w", encoding="utf-8") as f:
            for customer in customers:
                if not isinstance(customer, Customer):
                    customer = Customer(customer["username"], customer["password"],
                                        customer["balance"])
                f.write(customer.to_record() + "\n")
        return True
    except (OSError, ValueError, TypeError, KeyError) as error:
        print(f"Unable to save customer data: {error}")
        return False


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
            return save_customers(customers)
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

    # This block removes blank lines before processing package records and
    # handles file access errors without closing the program.
    try:
        with open(PACKAGES_FILE, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
    except OSError as error:
        print(f"Unable to read package data: {error}")
        return packages

    legacy_format_detected = False
    for i, line in enumerate(lines, 1):
        try:
            parts = line.split("|")
            if len(parts) == 3:
                legacy_format_detected = True
            packages.append(WifiPackage.from_record(line, legacy_id=i))
        except (ValueError, TypeError) as error:
            print(f"Warning: skipped invalid package record on line {i}: {error}")

    # This block upgrades an old package file after it has been loaded.
    if legacy_format_detected:
        save_packages(packages)

    return packages


# This code saves packages using the current five-field storage format.
def save_packages(packages):
    """Save packages list back to text file (id|name|duration|price|status)."""
    try:
        with open(PACKAGES_FILE, "w", encoding="utf-8") as f:
            for package in packages:
                if not isinstance(package, WifiPackage):
                    package = WifiPackage(
                        package["id"], package["name"], package["duration"],
                        package["price"], package["status"]
                    )
                f.write(package.to_record() + "\n")
        return True
    except (OSError, ValueError, TypeError, KeyError) as error:
        print(f"Unable to save package data: {error}")
        return False


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


# ==================== PURCHASE STORAGE ====================

# This code safely reads purchase records used by both customer and admin
# features. A damaged line is skipped with a warning instead of causing an
# IndexError or ValueError elsewhere in the program.
def load_purchases():
    """Load valid purchase records as lists of six text fields."""
    purchases = []
    if not os.path.exists(PURCHASES_FILE):
        return purchases

    try:
        with open(PURCHASES_FILE, "r", encoding="utf-8") as f:
            for line_number, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    parts = line.split("|")
                    if len(parts) != 6:
                        raise ValueError("purchase record must contain 6 fields")
                    float(parts[2])
                    purchases.append(parts)
                except (ValueError, TypeError) as error:
                    print(f"Warning: skipped invalid purchase record on line "
                          f"{line_number}: {error}")
    except OSError as error:
        print(f"Unable to read purchase data: {error}")

    return purchases


# ==================== ADMIN CREDENTIAL STORAGE ====================

# This code reads the administrator login and creates default credentials when
# the credentials file is missing or empty.
def load_admin_credentials():
    """Load admin username/password, creating the default file if missing."""
    if not os.path.exists(ADMIN_FILE):
        save_admin_credentials("admin", "admin123")
        return {"username": "admin", "password": "admin123"}

    try:
        with open(ADMIN_FILE, "r", encoding="utf-8") as f:
            line = f.readline().strip()
    except OSError as error:
        print(f"Unable to read administrator credentials: {error}")
        return {"username": "admin", "password": "admin123"}

    if not line:
        save_admin_credentials("admin", "admin123")
        return {"username": "admin", "password": "admin123"}

    parts = line.split("|")
    if len(parts) != 2 or not parts[0] or not parts[1]:
        print("Warning: administrator credentials are invalid. Using defaults.")
        return {"username": "admin", "password": "admin123"}
    return {"username": parts[0], "password": parts[1]}


# This code saves the administrator username and password to admin.txt.
def save_admin_credentials(username, password):
    """Save admin username/password back to text file."""
    try:
        with open(ADMIN_FILE, "w", encoding="utf-8") as f:
            f.write(f"{username}|{password}\n")
        return True
    except OSError as error:
        print(f"Unable to save administrator credentials: {error}")
        return False
