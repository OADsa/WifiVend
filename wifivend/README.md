# WiFiVend - WiFi Hotspot Vending System

A terminal-based Python application for managing WiFi voucher sales. Designed as a college final project, it demonstrates file handling, menu-driven interfaces, input validation, and basic CRUD operations using only Python's standard libraries.

## Features

### Customer Module
- View available WiFi packages
- Purchase WiFi vouchers with name entry and confirmation
- Receive randomly generated unique voucher codes
- Check voucher status and expiration details
- Formatted purchase receipt after every transaction

### Administrator Module
- Secure login system (Username: `admin`, Password: `admin123`)
- View all transactions
- Search transactions by customer name
- View total sales and transaction count
- Add new WiFi packages
- Edit package prices
- Delete packages

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
├── customer.py      # Customer module (purchase, view packages, check voucher)
├── admin.py         # Administrator module (login, transactions, package management)
├── packages.txt     # Stores available WiFi packages
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
2. View available packages or purchase a voucher
3. Enter your name and confirm the purchase
4. Receive a unique voucher code with expiration time
5. Use "Check Voucher Status" to verify voucher details

### Administrator Flow
1. Select **Administrator** from the main menu
2. Login with credentials:
   - Username: `admin`
   - Password: `admin123`
3. Manage packages and view sales data

## Data Storage

All data is stored in plain text files:
- `packages.txt` - WiFi package definitions (pipe-delimited)
- `purchases.txt` - Purchase records (pipe-delimited)

## Sample Packages

| Package | Duration | Price |
|---------|----------|-------|
| 30 Minutes | 30 mins | $2.00 |
| 1 Hour | 60 mins | $3.50 |
| 2 Hours | 120 mins | $6.00 |
| 5 Hours | 300 mins | $12.00 |

## Error Handling

- Input validation for all numeric entries
- Prevents empty customer names
- Prevents duplicate voucher codes
- Graceful handling of missing data files
- Confirmation prompts for destructive actions (delete, purchase)

## License

This project is created for educational purposes as a college final project.
