import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout,
                             QWidget, QLabel, QColorDialog, QLineEdit, QGroupBox, QGridLayout, QComboBox)
from PyQt5.QtGui import QIntValidator
from PyQt5.QtCore import Qt

import socket


class LEDRemoteGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LED Remote Control")
        self.setGeometry(100, 100, 400, 600)

        self.sock = None
        self.server_address = ('192.168.1.109', 50000)

        self.init_ui()
        self.connect_to_server()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Status label
        self.status_label = QLabel("Status: Disconnected")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
        main_layout.addWidget(self.status_label)

        # ON/OFF buttons - centered
        on_off_layout = QHBoxLayout()
        on_off_layout.addStretch()  # Add stretch to center the buttons
        on_button = self.create_button("ON", lambda: self.send_command("DYNAMIC"))
        off_button = self.create_button("OFF", lambda: self.send_command("CLEAR"))
        on_off_layout.addWidget(on_button)
        on_off_layout.addWidget(off_button)
        on_off_layout.addStretch()  # Add stretch to center the buttons
        main_layout.addLayout(on_off_layout)

        # Brightness group
        brightness_group = QGroupBox("Brightness")
        brightness_layout = QGridLayout()
        brightness_group.setLayout(brightness_layout)

        brightness_up = self.create_button("Brightness +", lambda: self.send_command("BRIGHTNESS:UP"))
        brightness_down = self.create_button("Brightness -", lambda: self.send_command("BRIGHTNESS:DOWN"))
        brightness_layout.addWidget(brightness_up, 0, 0)
        brightness_layout.addWidget(brightness_down, 1, 0)

        self.brightness_input = QLineEdit()
        self.brightness_input.setPlaceholderText("0-100")
        self.brightness_input.setFixedWidth(100)
        self.brightness_input.setValidator(QIntValidator(0, 100))
        self.brightness_input.setStyleSheet("border: 1px solid gray; padding: 2px;")

        set_brightness = self.create_button("Set Brightness", self.set_manual_brightness)
        set_brightness.setFixedWidth(100)
        set_brightness.setFixedHeight(30)

        brightness_layout.addWidget(self.brightness_input, 0, 1)
        brightness_layout.addWidget(set_brightness, 1, 1)

        main_layout.addWidget(brightness_group)

        # Static color group
        color_group = QGroupBox("Static Color")
        color_layout = QVBoxLayout()
        color_group.setLayout(color_layout)

        choose_color_layout = QHBoxLayout()
        choose_color_layout.addStretch()  # Add stretch to center the button
        choose_color = self.create_button("Choose Color", self.choose_color)
        choose_color_layout.addWidget(choose_color)
        choose_color_layout.addStretch()  # Add stretch to center the button
        color_layout.addLayout(choose_color_layout)

        preset_colors_layout = QGridLayout()
        preset_colors = [("Red", "#FF0000"), ("Green", "#00FF00"), ("Blue", "#0000FF"),
                         ("White", "#FFFFFF"), ("Scarlet", "#FF1000"), ("Violet", "#45009F"),
                         ("Amber", "#FF7F00"), ("Teal blue", "#00799E"), ("Pink", "#D60082")]

        for i, (color_name, color_hex) in enumerate(preset_colors):
            color_button = self.create_color_button(color_name, color_hex)
            preset_colors_layout.addWidget(color_button, i // 3, i % 3)

        color_layout.addLayout(preset_colors_layout)
        main_layout.addWidget(color_group)

        # Effects group
        effects_group = QGroupBox("Effects")
        effects_layout = QHBoxLayout()
        effects_group.setLayout(effects_layout)

        self.effect_combo = QComboBox()
        self.effect_combo.addItems(["RAINBOW", "PROGRESS"])
        self.effect_combo.setFixedWidth(100)  # Reduce width of the dropdown to match input size
        effects_layout.addWidget(self.effect_combo)

        effect_button = self.create_button("EFFECT", self.apply_effect)
        effects_layout.addWidget(effect_button)

        main_layout.addWidget(effects_group)

        # Dynamic group
        dynamic_group = QGroupBox("Dynamic")
        dynamic_layout = QVBoxLayout()  # Changed to QVBoxLayout to stack the "Transition Speed" group underneath
        dynamic_group.setLayout(dynamic_layout)

        dynamic_button_layout = QHBoxLayout()
        dynamic_button_layout.addStretch()  # Add stretch to center the button
        dynamic_button = self.create_button("DYNAMIC", lambda: self.send_command("DYNAMIC"))
        dynamic_button_layout.addWidget(dynamic_button)
        dynamic_button_layout.addStretch()  # Add stretch to center the button
        dynamic_layout.addLayout(dynamic_button_layout)

        # Transition speed group (now under Dynamic group)
        tspeed_group = QGroupBox("Transition Speed")
        tspeed_layout = QGridLayout()
        tspeed_group.setLayout(tspeed_layout)

        tspeed_up = self.create_button("Speed +", lambda: self.send_command("TSPEED:UP"))
        tspeed_down = self.create_button("Speed -", lambda: self.send_command("TSPEED:DOWN"))
        tspeed_layout.addWidget(tspeed_up, 0, 0)
        tspeed_layout.addWidget(tspeed_down, 1, 0)

        self.tspeed_input = QLineEdit()
        self.tspeed_input.setPlaceholderText("0-100")
        self.tspeed_input.setFixedWidth(100)
        self.tspeed_input.setValidator(QIntValidator(0, 100))
        self.tspeed_input.setStyleSheet("border: 1px solid gray; padding: 2px;")

        set_tspeed = self.create_button("Set Speed", self.set_manual_tspeed)
        set_tspeed.setFixedWidth(100)
        set_tspeed.setFixedHeight(30)

        tspeed_layout.addWidget(self.tspeed_input, 0, 1)
        tspeed_layout.addWidget(set_tspeed, 1, 1)

        dynamic_layout.addWidget(tspeed_group)  # Adding Transition Speed group under Dynamic group

        main_layout.addWidget(dynamic_group)

    def create_button(self, text, function):
        button = QPushButton(text)
        button.clicked.connect(function)
        button.setFixedWidth(100)
        button.setFixedHeight(30)
        button.setStyleSheet("""
            QPushButton {
                border: 2px solid #d0d0d0;
                border-radius: 10px;
                background-color: white;
                padding: 5px;
                color: black;
            }
            QPushButton:pressed {
                background-color: #f0f0f0;
            }
        """)
        return button

    def create_color_button(self, text, color_hex):
        button = QPushButton(text)
        button.setFixedSize(100, 30)  # Reduced width and height
        button.setStyleSheet(f"""
            QPushButton {{
                border-radius: 10px;
                background-color: {color_hex};
                color: black;
                border: 2px solid #d0d0d0;
                text-align: center;
                padding: 5px;
            }}
            QPushButton:pressed {{
                background-color: #d0d0d0;
            }}
        """)
        button.clicked.connect(lambda _, c=color_hex: self.set_static_color(c))
        return button

    def connect_to_server(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect(self.server_address)
            self.status_label.setText("Status: Connected")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
            print(f"Connected to {self.server_address}")
            response = self.sock.recv(1024)
            print('Server:', response.decode('utf-8'))
        except socket.error as e:
            self.status_label.setText(f"Status: Connection failed - {e}")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")
            print(f"Socket error occurred: {e}")

    def send_command(self, command):
        if self.sock:
            try:
                self.sock.sendall(command.encode('utf-8'))
                print(f"Sent command: {command}")
            except socket.error as e:
                print(f"Error sending command: {e}")
                self.status_label.setText("Status: Connection lost")
                self.status_label.setStyleSheet("color: red; font-weight: bold;")
        else:
            print("Not connected to server")

    def choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.set_static_color(color.name())

    def set_static_color(self, color):
        command = f"STATIC:{color.replace('#', '0x')}"
        self.send_command(command)

    def set_manual_brightness(self):
        brightness = self.brightness_input.text()
        if brightness:
            self.send_command(f"BRIGHTNESS:{brightness}")

    def set_manual_tspeed(self):
        speed = self.tspeed_input.text()
        if speed:
            self.send_command(f"TSPEED:{speed}")

    def apply_effect(self):
        selected_effect = self.effect_combo.currentText()
        self.send_command(f"EFFECT:{selected_effect}")

    def closeEvent(self, event):
        if self.sock:
            self.sock.close()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LEDRemoteGUI()
    window.show()
    sys.exit(app.exec_())
