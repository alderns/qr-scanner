#!/usr/bin/env python3

import subprocess
import sys
import os

def install_package(package):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    print("QR Scanner - Optional Dependencies Installer")
    print("=" * 50)
    
    optional_packages = [
        ("psutil", "Enhanced performance monitoring and system metrics"),
        ("pytest", "Testing framework (for development)"),
        ("pytest-cov", "Test coverage reporting (for development)")
    ]
    
    print("\nOptional packages available:")
    for i, (package, description) in enumerate(optional_packages, 1):
        print(f"{i}. {package} - {description}")
    
    print("\nEnter the numbers of packages to install (comma-separated), or 'all' for all packages:")
    choice = input("Choice: ").strip().lower()
    
    if choice == 'all':
        packages_to_install = [pkg for pkg, _ in optional_packages]
    else:
        try:
            indices = [int(x.strip()) - 1 for x in choice.split(',')]
            packages_to_install = [optional_packages[i][0] for i in indices if 0 <= i < len(optional_packages)]
        except (ValueError, IndexError):
            print("Invalid choice. Please enter valid numbers or 'all'.")
            return
    
    if not packages_to_install:
        print("No packages selected.")
        return
    
    print(f"\nInstalling packages: {', '.join(packages_to_install)}")
    print("-" * 50)
    
    success_count = 0
    for package in packages_to_install:
        print(f"Installing {package}...", end=" ")
        if install_package(package):
            print("✓ Success")
            success_count += 1
        else:
            print("✗ Failed")
    
    print("-" * 50)
    print(f"Installation complete: {success_count}/{len(packages_to_install)} packages installed successfully.")
    
    if success_count < len(packages_to_install):
        print("\nNote: Some packages failed to install. The application will still work with basic features.")
        print("You can try installing them manually using: pip install <package_name>")

if __name__ == "__main__":
    main() 