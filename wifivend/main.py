#!/usr/bin/env python3
"""
WiFiVend - WiFi Hotspot Vending System
Main entry point with menu-driven interface.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from customer import customer_menu
from admin import admin_menu


def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def press_enter():
    """Wait for user to press Enter to continue."""
    input("\nPress Enter to continue...")


def print_main_menu():
    print("\n" + "=" * 50)
    print(" " * 12 + "WiFiVend System")
    print("=" * 50)
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
