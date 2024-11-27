# Utility Script for Computer Information and Automation

This Python script provides a versatile toolbox for gathering computer information and building automation scripts. It offers both a command-line interface (CLI) and a graphical user interface (GUI) for convenient access to its functionalities.

## Features

### Screenshot Snipping Tool

* Captures screenshots of selected screen regions.
* Saves screenshots in PNG or JPEG format.
* Uses a crosshair cursor for precise region selection.
* Provides visual feedback during region selection.
* Press `F9` to start the taking of the screenshot and `esc` to cancel.

### Pixel Tracker

* Displays a circle around the mouse cursor, showing the pixel color dynamically.
* Provides the HEX color values of the pixel under the cursor.
* Shows the (x, y) coordinates of the pixel.
* Press `spacebar` to print the pixel information in the console.

### Region Capture

* Captures a rectangular region on the screen.
* Prints the coordinates of the captured region.
* Can be used to determine the position of elements for automation scripts.

## Usage

### CLI

1. Install the required packages:
   ```bash
   pip install PyQt5 pyautogui keyboard typer
   ```
2. You can also use:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the script with the desired command:
   * `python utils.py region`: Captures a screen region and prints its coordinates.
   * `python utils.py pixel`: Activates the pixel tracker.
   * `python utils.py snip`: Starts the screenshot snipping tool.
   * `python utils.py gui`: Launches the GUI.
   * `python utils.py --help`: Get help information.

### GUI

1. Run the script without any command-line arguments: `python utils.py`
2. The GUI will appear, providing buttons for:
   * Toggling "Always on Top"
   * Activating the pixel tracker
   * Capturing a region
   * Taking a screenshot
   * Closing the application

## Building an Executable

You can create an executable file for this script using PyInstaller. Here's a basic command:

```bash
pyinstaller --onefile --windowed --add-data "images/gui;images/gui" utils.py -i "images/icon.png"
```

This will generate a single executable file in the dist directory.

**Note**: The output directory for captured region and pixel data will be created in the same directory as the executable.

## Hotkeys

* `F9`: Capture region or screenshot (depending on the active tool)
* `Esc`: Exit the current tool or close the application

## Requirements

* Python 3
* PyQt5
* PyAutoGUI
* Keyboard
* Typer

## Icons

* The icons used in this project are taken from Google's Material Icons pack: https://fonts.google.com/icons

## Contributing

Contributions are welcome! Feel free to submit bug reports, feature requests, or pull requests.
