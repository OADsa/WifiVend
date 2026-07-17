#!/usr/bin/env python3
"""
WiFiVend - WiFi Hotspot Vending System
Main entry point with menu-driven interface.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import clear_screen, press_enter, print_header
from customer import customer_menu
from admin import admin_menu


def print_main_menu():
    print_header("Main Menu: WifiVend!")
    print("  1. Customer")
    print("  2. Administrator")
    print("  3. Exit")
    print("=" * 50)


def main():
    while True:
        clear_screen()
        print_main_menu()
        choice = input("Select option: ").strip()

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


if __name__ == "__main__":
    main()