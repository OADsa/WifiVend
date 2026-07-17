#!/usr/bin/env python3
"""
WiFiVend - WiFi Hotspot Vending System
Main entry point with menu-driven interface.
"""

import sys
import os

# This code adds the project folder to Python's module search path so the
# program can import the other source files regardless of where it is run.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# These imports provide the shared screen helpers and the two user modules.
from common import clear_screen, press_enter, print_header
from customer import customer_menu
from admin import admin_menu


# This code displays the choices available on the program's main screen.
def print_main_menu():
    print_header("Main Menu: WifiVend!")
    print("  1. Customer")
    print("  2. Administrator")
    print("  3. Exit")
    print("=" * 50)


# This code repeatedly accepts a main-menu choice and sends the user to the
# customer module, administrator module, or program exit.
def main():
    while True:
        clear_screen()
        print_main_menu()
        choice = input("Select option: ").strip()

        # This block checks the selected option and opens the matching menu.
        if choice == '1':
            customer_menu()
        elif choice == '2':
            admin_menu()
        elif choice == '3':
            clear_screen()
            print("\nThank you for using WiFiVend. Goodbye!")
            press_enter()
            break
        else:
            print("Invalid option. Please try again.")
            press_enter()


# This condition starts the program only when this file is run directly.
if __name__ == "__main__":
    main()
