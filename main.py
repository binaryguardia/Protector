import tkinter as tk
from auth import AuthWindow
from file_manager import FileManager
import subprocess
import sys
import threading
from flask import Flask

def start_share_server():
    try:
        # Start the Flask server in a separate process
        subprocess.Popen([sys.executable, 'share_server.py'],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE)
        print("Share server started successfully")
    except Exception as e:
        print(f"Error starting share server: {e}")

def main():
    start_share_server()
    
    root = tk.Tk()
    root.title("Secure File Manager")
    root.geometry("800x600")  # Increased initial size
    app = AuthWindow(root, lambda username: go_to_file_manager(root, username))
    root.mainloop()

def go_to_file_manager(root, username):
    for widget in root.winfo_children():
        widget.destroy()
    file_manager = FileManager(root, username, lambda: go_back_to_auth(root))
    file_manager.setup_ui()

def go_back_to_auth(root):
    for widget in root.winfo_children():
        widget.destroy()
    app = AuthWindow(root, lambda username: go_to_file_manager(root, username))

if __name__ == "__main__":
    main()
