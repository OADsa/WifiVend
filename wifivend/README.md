# WiFiVend - WiFi Hotspot Vending System

A terminal-based Python application for managing WiFi voucher sales. Designed as a college final project, it demonstrates file handling, menu-driven interfaces, input validation, customer authentication, balance management, and basic CRUD operations using only Python's standard libraries.

## Features

### Customer Module
- **Login / Register**: New customers can register with a username, password, and initial deposit. Returning customers can log in.
- **Balance Management**: Customers can deposit money into their account at any time.
- **View Packages**: See all available WiFi packages or filter by affordable options only.
- **Purchase Vouchers**: Buy vouchers using account balance. System deducts the correct amount and prevents overspending.
- **Unique Voucher Codes**: Every purchase generates a unique 8-character alphanumeric code.
- **Receipt**: Formatted purchase receipt showing customer name, package, price, voucher code, purchase time, and expiration time.
- **Check Voucher Status**: Verify voucher details by entering the voucher code.
- **View Account**: See current balance and personal purchase history.
- **Logout**: Securely end the current customer session.

### Administrator Module
- **Secure Login**: Protected by username `admin` and password `admin123`.
- **View All Transactions**: See every purchase made on the system.
- **Search Transactions**: Find transactions by customer name.
- **View Total Sales**: See total revenue and transaction count.
- **Manage Packages**: Add, edit prices, and delete WiFi packages.
- **View All Customers**: See every registered customer and their current balance.
- **Reset Customer Password**: Admin can reset any customer's password for support purposes.

## Requirements

- Python 3.x (No external libraries required)
- Only standard Python libraries are used: `os`, `random`, `string`, `datetime`, `sys`

## How to Run

1. Ensure Python 3 is installed on your system:
   ```bash
   python --version
   ```

2. Navigate to the project folder:
   ```bash
   cd wifivend
   ```

3. Run the main program:
   ```bash
   python main.py
   ```

## Project Structure

```
wifivend/
├── main.py          # Entry point with main menu
├── customer.py      # Customer module (auth, balance, purchase, vouchers)
├── admin.py         # Administrator module (login, transactions, package/customer management)
├── packages.txt     # Stores available WiFi packages
├── customers.txt    # Stores registered customer accounts (auto-generated)
├── purchases.txt    # Stores all purchase records (auto-generated)
└── README.md        # Project documentation
```

## Usage

### Main Menu
```
1. Customer
2. Administrator
3. Exit
```

### Customer Flow
1. Select **Customer** from the main menu
2. **Login** with existing credentials or **Register** a new account
3. During registration, enter an initial deposit amount
4. View available packages or buy a voucher
5. When purchasing, only packages within your balance are shown
6. Confirm purchase to receive a unique voucher code and receipt
7. Use **Deposit Money** to add more funds
8. Use **View My Account** to check balance and purchase history
9. Use **Logout** to return to the main menu

### Administrator Flow
1. Select **Administrator** from the main menu
2. Login with credentials:
   - Username: `admin`
   - Password: `admin123`
3. Manage packages, view sales, search transactions, view customers, or reset customer passwords

## Data Storage

All data is stored in plain text files using pipe-delimited format (`|`):
- `packages.txt` - WiFi package definitions: `name|price|duration`
- `customers.txt` - Customer accounts: `username|password|balance`
- `purchases.txt` - Purchase records: `customer|package|price|voucher|purchased|expires`

## Sample Packages

| Package | Duration | Price |
|---------|----------|-------|
| 30 Minutes | 30 mins | $2.00 |
| 1 Hour | 60 mins | $3.50 |
| 2 Hours | 120 mins | $6.00 |
| 5 Hours | 300 mins | $12.00 |

## Error Handling

- Input validation for all numeric entries
- Prevents empty usernames, passwords, or names
- Prevents duplicate voucher codes
- Prevents overspending (balance check before purchase)
- Graceful handling of missing data files
- Confirmation prompts for destructive actions (delete, purchase, password reset)

## License

This project is created for educational purposes as a college final project.
