import os, sys
import subprocess

# Informacje o aplikacji
APP_NAME = "FinanList"
APP_VERSION = "1.0.0.0"
ICON = os.path.join("data", "images", "app_logo.jpg")
DATA = os.path.join("data")

BUILD_DIR = r"build"

command = []

# Nuitka commands
match sys.platform:
    case "win32":
        # Windows
        command = [
            "python",
            "-m",
            "nuitka",
            "--standalone",
            "--deployment",
            "--enable-plugin=pyside6",
            "--windows-console-mode=disable",
            "--output-dir={0}".format(BUILD_DIR),
            "--output-filename={0}".format(APP_NAME),
            "--product-name={0}".format(APP_NAME),
            "--product-version={0}".format(APP_VERSION),
            "--windows-icon-from-ico={0}".format(ICON),
            "--include-data-dir={0}=data".format(DATA),
            "--follow-imports",
            "main.py",
        ]
    case "darwin":
        # MacOs
        command = [
            "python",
            "-m",
            "nuitka",
            "--standalone",
            "--deployment",
            "--macos-create-app-bundle",
            "--enable-plugin=pyside6",
            "--output-dir={0}".format(BUILD_DIR),
            "--output-filename={0}".format(APP_NAME),
            "--product-name={0}".format(APP_NAME),
            "--product-version={0}".format(APP_VERSION),
            "--macos-app-icon={0}".format(ICON),
            "--include-data-dir={0}=data".format(DATA),
            "--follow-imports",
            "main.py",
        ]
    case "linux":
        # Linux
        command = [
            "python",
            "-m",
            "nuitka",
            "--standalone",
            "--deployment",
            "--enable-plugin=pyside6",
            "--static-libpython=no",
            "--output-dir={0}".format(BUILD_DIR),
            "--output-filename={0}".format(APP_NAME),
            "--product-name={0}".format(APP_NAME),
            "--product-version={0}".format(APP_VERSION),
            "--linux-icon={0}".format(ICON),
            "--include-data-dir={0}=data".format(DATA),
            "--follow-imports",
            "main.py",
        ]

print(command)

# Uruchomienie komendy
subprocess.run(command, check=True)
print("{0} app was generated to: {1}".format(sys.platform, BUILD_DIR))
