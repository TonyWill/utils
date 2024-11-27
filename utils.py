import os
import sys
import time

import keyboard
import pyautogui
import typer
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QColor, QPainter, QPen, QIcon
from PyQt5.QtWidgets import (QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
                             QApplication)

app = typer.Typer()
QtCore.QCoreApplication.setAttribute(Qt.AA_DisableHighDpiScaling)
app_gui = None # QtWidgets.QApplication(sys.argv)

def capture_region():
    """
    Captures a rectangular region on the screen with dimming and visual feedback.
    """

    window = Regioner()
    window.show()

    # Loop until Esc is pressed
    while window.isVisible():
        app_gui.processEvents()  # Allow the GUI to update

def snipper():
    """

     Starts the screenshot snipping tool.
    Press F9 to capture, Esc to exit.
    """

    window = Snipper()
    window.show()

    # Loop until Esc is pressed
    while window.isVisible():
        app_gui.processEvents()  # Allow the GUI to update

class PixelTracker(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pixel Tracker")
        self.setWindowFlags(Qt.FramelessWindowHint
                            | Qt.WindowStaysOnTopHint)  # Add Qt.WindowStaysOnTopHint
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(-50, -50, 300,
                         200)  # Small initial size

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_position_and_color)
        self.timer.start(10)  # Update every 10ms
        
        self.current_color = QColor(0, 0, 0)
        self.current_location = (0, 0)

    def showEvent(self, event):
        """Sets the mask after the widget is shown."""
        self.setMask(QtGui.QRegion(self.rect(), QtGui.QRegion.Ellipse))
        super().showEvent(event)

    def update_position_and_color(self):
        x, y = pyautogui.position()
        try:
            pixel_color = pyautogui.pixel(x, y)
            hex_color = "#%02x%02x%02x" % pixel_color
            self.current_color = QColor(hex_color)
            self.current_location = (x, y)
        except KeyboardInterrupt:
            print("Exiting pixel tracker...")
            self.close()
            return
        # Check if the circle would be drawn off-screen
        if x + 5 + 50 > pyautogui.size()[0]:
            x = x - 5 - 50  # Move to the left of the cursor
        else:
            x = x + 5  # Move to the right of the cursor

        if y - 50 < 0:
            y = y + 30  # Move below the cursor
        else:
            y = y - 50  # Move above the cursor

        self.move(x - 100, y - 50)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QPen(QColor(0, 0, 0), 3))
        painter.setBrush(
            self.current_color)  # Use the QColor object directly
        painter.drawEllipse(100, 50, 50, 50)

        # Draw the color value below the circle
        # Determine contrasting text color
        text_color = QColor(255 - self.current_color.red(),
                            255 - self.current_color.green(),
                            255 - self.current_color.blue())

        # Ensure antialiasing is enabled for smooth outlines
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        # Draw the color value with a white outline
        font = painter.font()
        font.setPointSize(12)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QPen(QColor(255, 255, 255), 2))  # White outline
        painter.drawText(110, 100, 150, 20, Qt.AlignLeft,
                         self.current_color.name())
        painter.setPen(QPen(text_color))  # Contrasting color
        font.setBold(False)
        painter.drawText(110, 100, 150, 20, Qt.AlignLeft,
                         self.current_color.name())
        painter.drawText(110, 118, 150, 20, Qt.AlignLeft, 
                         f"({self.current_location[0]}, {self.current_location[1]})")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            x, y = pyautogui.position()
            pixel_color = pyautogui.pixel(x, y)
            hex_color = "#%02x%02x%02x" % pixel_color
            print(f"Position: ({x}, {y}), Color: {hex_color}")
            
            # Save pixel data to file
            output_dir = resource_path("output")
            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, "pixel_data.txt")

            with open(output_file, "a") as f:
                f.write(f"Position: ({x}, {y}), Color: {hex_color}\n") 

            print(f"Pixel data appended to {output_file}")

class Regioner(QtWidgets.QWidget):
    def __init__(self, parent=None, flags=Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)
        
        self.setWindowTitle("Region Snipper")
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Dialog)
        self.setWindowState(self.windowState() | Qt.WindowFullScreen)

        self._screen = QtWidgets.QApplication.primaryScreen()

        palette = QtGui.QPalette()
        palette.setBrush(self.backgroundRole(), QtGui.QBrush(self.getWindow()))
        self.setPalette(palette)

        QtWidgets.QApplication.setOverrideCursor(
            QtGui.QCursor(QtCore.Qt.CrossCursor))

        self.start, self.end = QtCore.QPoint(), QtCore.QPoint()

    def getWindow(self):
        return self._screen.grabWindow(0)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
        return super().keyPressEvent(event)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QtGui.QColor(0, 0,0, 100))
        painter.drawRect(0, 0, self.width(), self.height())

        if self.start == self.end:
            return super().paintEvent(event)

        painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255), 3))
        painter.setBrush(painter.background())
        painter.drawRect(QtCore.QRect(self.start, self.end))
        return super().paintEvent(event)

    def mousePressEvent(self, event):
        self.start = self.end = event.pos()
        self.update()
        return super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()
        return super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if self.start == self.end:
            return super().mouseReleaseEvent(event)

        self.hide()
        QtWidgets.QApplication.processEvents()
        shot = self.getWindow().copy(
            QtCore.QRect(self.start, self.end))
        QtWidgets.QApplication.restoreOverrideCursor()

        x1, y1, x2, y2 = self.start.x(), self.start.y(), self.end.x(), self.end.y()
        x1, x2 = min(x1, x2), max(x1, x2)
        y1, y2 = min(y1, y2), max(y1, y2)

        if x1 + 3 < x2 and y1 + 3 < y2:
            x1 += 3
            y1 += 3

        width = x2 - x1
        height = y2 - y1
        
        print(f"Region captured:")
        print(f"  * Top-left corner: ({x1}, {y1})")
        print(f"  * Bottom-right corner: ({x2}, {y2})")
        print(f"  * Width: {width}")
        print(f"  * Height: {height}")
        
        # Print the x_region information
        print(f"  * self.x_region = ({x1}, {y1}, {width}, {height})")  # New line
        output_dir = resource_path("output")  # Directory to save the file
        os.makedirs(output_dir, exist_ok=True)  # Create the directory if it doesn't exist
        output_file = os.path.join(output_dir, "region_data.txt")

        with open(output_file, "a") as f:
            f.write(f"Top-left corner: ({x1}, {y1})\n")
            f.write(f"Bottom-right corner: ({x2}, {y2})\n")
            f.write(f"Width: {width}\n")
            f.write(f"Height: {height}\n")
            f.write(f"self.x_region = ({x1}, {y1}, {width}, {height})\n\n")  # New line

        print(f"Region data saved to {output_file}")
        self.close() 

        return super().mouseReleaseEvent(event)

class Snipper(QtWidgets.QWidget):
    def __init__(self, parent=None, flags=Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)

        self.setWindowTitle("Screenshot Snipper")
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Dialog)
        self.setWindowState(self.windowState() | Qt.WindowFullScreen)

        self._screen = QtWidgets.QApplication.primaryScreen()
        palette = QtGui.QPalette()
        palette.setBrush(self.backgroundRole(), QtGui.QBrush(self.getWindow()))
        self.setPalette(palette)

        QtWidgets.QApplication.setOverrideCursor(
            QtGui.QCursor(QtCore.Qt.CrossCursor))

        self.start, self.end = QtCore.QPoint(), QtCore.QPoint()

    def getWindow(self):
        return self._screen.grabWindow(0)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            QtWidgets.QApplication.quit()
        return super().keyPressEvent(event)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QtGui.QColor(0, 0, 0, 100))
        painter.drawRect(0, 0, self.width(), self.height())

        if self.start == self.end:
            return super().paintEvent(event)

        painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255), 3))
        painter.setBrush(painter.background())
        painter.drawRect(QtCore.QRect(self.start, self.end))
        return super().paintEvent(event)

    def mousePressEvent(self, event):
        self.start = self.end = event.pos()
        self.update()
        return super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()
        return super().mouseMoveEvent(event)  # Use mouseMoveEvent here

    def mouseReleaseEvent(self, event):
        self.end = event.pos()
        self.capture_screenshot()
        self.close()
        QtWidgets.QApplication.restoreOverrideCursor()  # Restore default cursor
        return super().mouseReleaseEvent(event)

    def capture_screenshot(self):
        x1, y1, x2, y2 = self.start.x(), self.start.y(), self.end.x(
        ), self.end.y()
        x1, x2 = min(x1, x2), max(x1, x2)
        y1, y2 = min(y1, y2), max(y1, y2)

        if x1 + 3 < x2 and y1 + 3 < y2:
            x1 += 3  # Adjust for the rectangle border width
            y1 += 3

        screenshot = pyautogui.screenshot(region=(x1, y1, x2 - x1, y2 - y1))

        options = QtWidgets.QFileDialog.Options()
        filepath, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Save Screenshot",
            "",
            "PNG Image (*.png);;JPEG Image (*.jpg)",
            options=options)
        if filepath:
            screenshot.save(filepath)
            print(f"Screenshot saved to {filepath}")
        self.close()  # Close the Snipper window after saving

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = os.path.dirname(sys.executable) # For building with PyInstaller
        # base_path = os.path.dirname(os.path.abspath(__file__)) # For running the script directly
    except Exception:
        base_path = os.path.dirname(os.path.abspath(sys.executable))
        
    return os.path.join(base_path, relative_path)


def image_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = os.path.dirname(os.path.abspath(__file__)) 
    except Exception:
        base_path = os.path.dirname(sys.executable)
        
    return os.path.join(base_path, relative_path)
class UtilityGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.tracker = None  # Initialize tracker as a class member

        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # Always on top button
        self.always_on_top_button = QPushButton()
        self.always_on_top_button.setCheckable(True)
        self.always_on_top_button.setChecked(True)
        self.always_on_top_button.toggled.connect(self.toggle_always_on_top)
        self.layout.addWidget(self.always_on_top_button)

        # Move the window to the bottom left, above the taskbar
        screen_geometry = QApplication.desktop().availableGeometry()
        taskbar_height = QApplication.desktop().screenGeometry().height() - screen_geometry.height()
        self.move(screen_geometry.right() - 50, screen_geometry.bottom() - taskbar_height - 143) # Adjust the height as needed

        # Utility buttons
        self.utility_buttons = []
        for i in range(3):
            button = QPushButton()
            button.setCheckable(True)
            self.utility_buttons.append(button)
            self.layout.addWidget(button)

        # Close button
        close_button = QPushButton()
        close_button.clicked.connect(self.close_application)  # Changed to close_application
        self.layout.addWidget(close_button)

        # Set button icons
        self.always_on_top_button.setIcon(QIcon(image_resource_path(r"images\gui\on_top_icon.svg")))
        self.utility_buttons[0].setIcon(
            QIcon(image_resource_path(r"images\gui\pixel_color_icon.svg")))
        self.utility_buttons[1].setIcon(QIcon(image_resource_path(r"images\gui\region_icon.svg")))
        self.utility_buttons[2].setIcon(
            QIcon(image_resource_path(r"images\gui\screenshot_icon.svg")))
        close_button.setIcon(QIcon(image_resource_path(r"images\gui\close_icon.svg")))
        self.setWindowIcon(QIcon(image_resource_path(r"images\icon.png")))

        # Connect button signals to functions
        # Connect the toggled signal to control the timer and button state
        self.utility_buttons[0].toggled.connect(self.toggle_pixel_tracker)
        self.utility_buttons[1].toggled.connect(self.toggle_region_capture)  # Connect toggled signal        
        # Connect the toggled signal to control the timer and button state
        self.utility_buttons[2].toggled.connect(self.toggle_snip_capture)

        bg_color = "#6200ee"
        hover_color = "#6750A4"
        checked_color = "#3700b3"
        # Set button styles
        for i, button in enumerate(
            [self.always_on_top_button] + self.utility_buttons +
            [close_button]):
            if i == 0:  # First button (top)
                button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {bg_color};
                    border: none;
                    padding: 10px;
                    border-top-left-radius: 20px;
                    border-top-right-radius: 20px;
                }}
                QPushButton:hover {{
                    background-color: {hover_color};
                }}
                QPushButton:checked {{
                    background-color: {checked_color};
                }}
            """)
            elif i == len(self.utility_buttons) + 1:  # Last button (bottom)
                button.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {bg_color};
                        border: none;
                        padding: 10px;
                        border-bottom-left-radius: 20px; 
                        border-bottom-right-radius: 20px;
                    }}
                    QPushButton:hover {{
                        background-color: {hover_color};
                    }}
                    QPushButton:checked {{
                        background-color: {checked_color};
                    }}
                """)
            else:  # Middle buttons
                button.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {bg_color};
                        border: none;
                        padding: 10px;
                    }}
                    QPushButton:hover {{
                        background-color: {hover_color};
                    }}
                    QPushButton:checked {{
                        background-color: {checked_color};
                    }}
                """)

        # Add a spacer and a grab line
        spacer = QWidget()
        spacer.setFixedHeight(5)  # Adjust spacer height as needed
        self.layout.addWidget(spacer)

        grab_line = QWidget()
        grab_line.setFixedHeight(5)  # Adjust line height as needed
        grab_line.setStyleSheet(
            f"background-color: {checked_color};")  # Customize line color
        self.layout.addWidget(grab_line)

        self.setFixedWidth(self.always_on_top_button.sizeHint().width())

    def toggle_always_on_top(self, checked):
        if checked:
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)


        self.show()

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

    def toggle_region_capture(self, checked):
        if checked:
            print("Region data button clicked")
            print("Press F9 to capture a region, Esc to exit.")
            self.region_capture_active = True

            def check_keys():
                if keyboard.is_pressed('f9'):
                    capture_region()
                if keyboard.is_pressed('esc') or not self.utility_buttons[1].isChecked():  # Check button state
                    print("Exiting region snipper.")
                    self.region_timer.stop()
                    self.region_capture_active = False
                    self.utility_buttons[1].setChecked(False)

            self.region_timer = QTimer()
            self.region_timer.timeout.connect(check_keys)
            self.region_timer.start(100)
        else:
            if self.region_capture_active:  # Only stop the timer if it's running
                print("Exiting region snipper.")
                self.region_timer.stop()
                self.region_capture_active = False
    
    def pixel_data(self):
        """Displays a circle around the mouse cursor showing the pixel color."""
        print("Pixel data button clicked")
        self.tracker = PixelTracker()
        self.tracker.show()

        # Define a function to handle key presses
        def check_keys():
            if keyboard.is_pressed('esc') or not self.utility_buttons[0].isChecked():
                self.utility_buttons[0].setChecked(False)

        # Use a QTimer to periodically check for key presses
        self.pixel_timer = QTimer()
        self.pixel_timer.timeout.connect(check_keys)
        self.pixel_timer.start(100)  # Check every 100ms

    def toggle_pixel_tracker(self, checked):
        if checked:
            self.pixel_data()  # Start the pixel tracker when the button is pressed
        else:
            # This will be triggered if the button is unchecked manually or by the Esc key
            print("Exiting pixel tracker...")
            self.tracker.close()
            self.pixel_timer.stop()

    def snip(self):
        """Starts the screenshot snipping tool."""
        print("Screenshot button clicked")
        print("Press F9 to capture a screenshot, Esc to exit.")

        self.snip_capture_active = True  # Flag to indicate screenshot capture mode

        def check_keys():
            if keyboard.is_pressed('f9'):
                snipper()
            if keyboard.is_pressed('esc') or not self.utility_buttons[2].isChecked():  # Check button state
                print("Exiting screenshot snipper.")
                self.snip_timer.stop()
                self.snip_capture_active = False
                self.utility_buttons[2].setChecked(False)  # Uncheck the button

        self.snip_timer = QTimer()
        self.snip_timer.timeout.connect(check_keys)
        self.snip_timer.start(100)
        
    def toggle_snip_capture(self, checked):
        if checked:
            self.snip()  # Start the snipping process when the button is pressed
        else:
            if self.snip_capture_active:
                print("Exiting screenshot snipper.")
                self.snip_timer.stop()
                self.snip_capture_active = False


    def close_application(self):  # New method to close the application
        """Closes the entire application."""
        app_gui.quit()
        sys.exit()  # Exit the Python script

def initialize_cli():
    # This function will encapsulate your CLI setup
    app = typer.Typer()  # Initialize Typer application

    @app.command()
    def region():
        """Captures a region on the screen and displays its coordinates."""
        print("Press F9 to capture a region, Esc to exit.")
        while True:  # Loop until Esc is pressed
            if keyboard.is_pressed('f9'):  # Check for F9
                capture_region()
            if keyboard.is_pressed('esc'):  # Check for Esc
                print("Exiting region snipper.")
                break
            time.sleep(0.1)  # Small delay to avoid excessive CPU usage
            # N

    @app.command()
    def pixel():
        """
        Displays a circle around the mouse cursor that dynamically
        changes color to match the pixel under the cursor.
        """
        tracker = PixelTracker()
        tracker.show()
        # sys.exit(app_gui.exec_())

    @app.command()
    def snip():
        """Starts the screenshot snipping tool."""
        print("Press F9 to capture a screenshot, Esc to exit.")
        while True:  # Loop until Esc is pressed
            if keyboard.is_pressed('f9'):  # Check for F9
                snipper()
            if keyboard.is_pressed('esc'):  # Check for Esc
                print("Exiting screenshot snipper.")
                break
            time.sleep(0.1)  # Small delay to avoid excessive CPU usage

    @app.command()
    def gui():
        """Shows the utility GUI."""
        global app_gui  # Declare app_gui as global
        app_gui = QApplication(sys.argv)  # Create QApplication instance
        initialize_gui()

    return app  # Return the initialized Typer application

def initialize_gui():
    # This function will encapsulate your GUI setup
    utility_gui = UtilityGUI()
    utility_gui.show()
    app_gui.exec_()

def main():
    global app_gui  # Declare app_gui as global
    app = initialize_cli()
    if len(sys.argv) > 1:  # Check if there are command-line arguments
        app()  # Run the Typer application if arguments are present
    else:
        app_gui = QApplication(sys.argv)  # Create QApplication instance if GUI is launched
        initialize_gui()  # Launch the GUI if no arguments are provided
    if app_gui:  # Start the event loop only if app_gui is created
        app_gui.exec_()
        
if __name__ == "__main__":
    main()