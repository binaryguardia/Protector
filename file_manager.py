import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import os
from cryptography.fernet import Fernet
import requests
import random
import string
from github import Github, InputFileContent
from datetime import datetime
import time

class FileManager:
    def __init__(self, root, username, go_back_callback):
        self.root = root
        self.username = username
        self.go_back_callback = go_back_callback
        self.key = self.load_or_generate_key()
        self.cipher = Fernet(self.key)
        
        # Create main container
        self.main_frame = ttk.Frame(self.root, padding="40")
        self.main_frame.pack(expand=True, fill='both')
        
        # Create centered content frame
        self.content_frame = ttk.Frame(self.main_frame, style='Custom.TFrame')
        self.content_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # Setup styles
        self.setup_styles()
        
        # User's file directory
        self.user_dir = f"files/{username}"
        if not os.path.exists(self.user_dir):
            os.makedirs(self.user_dir)
        
        # GitHub configuration
        self.github_token = "ghp_your_github_token_here"  # Get this from GitHub
        try:
            self.github = Github(self.github_token)
            self.github_user = self.github.get_user()
        except Exception as e:
            print(f"GitHub initialization error: {e}")
            messagebox.showerror("GitHub Error", 
                               "Failed to connect to GitHub. Please check your token.")
        
        # Configure server URL with proper formatting
        self.server_url = "http://127.0.0.1:5000"  # Flask server URL
        self.max_retries = 3
        self.retry_delay = 1  # seconds

    def setup_styles(self):
        style = ttk.Style()
        
        # Color scheme
        self.colors = {
            'primary': '#2C3E50',    # Dark blue
            'secondary': '#3498DB',   # Light blue
            'background': '#ECF0F1',  # Light gray
            'text': '#2C3E50',        # Dark blue
            'white': '#FFFFFF'        # White
        }
        
        # Configure styles
        style.configure('Custom.TFrame',
                       background=self.colors['background'])
        
        style.configure('Header.TLabel',
                       background=self.colors['background'],
                       foreground=self.colors['primary'],
                       font=('Helvetica', 24, 'bold'))
        
        style.configure('Custom.TLabel',
                       background=self.colors['background'],
                       foreground=self.colors['text'],
                       font=('Helvetica', 12))
        
        style.configure('Custom.TButton',
                       font=('Helvetica', 12),
                       padding=10)

    def setup_ui(self):
        self.root.title("Protector - File Manager")
        
        # Clear any existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Main container using pack
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.pack(expand=True, fill='both')
        
        # Header
        ttk.Label(self.main_frame, 
                 text=f"Welcome, {self.username}!", 
                 style='Header.TLabel').pack(pady=(0, 20))
        
        # Buttons frame
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Button(button_frame, 
                   text="Upload File",
                   command=self.upload_file).pack(side='left', padx=5)
        ttk.Button(button_frame,
                   text="Download File",
                   command=self.download_file).pack(side='left', padx=5)
        ttk.Button(button_frame,
                   text="Share File",
                   command=self.share_file).pack(side='left', padx=5)
        
        # File list frame
        list_frame = ttk.Frame(self.main_frame)
        list_frame.pack(fill='both', expand=True)
        
        ttk.Label(list_frame,
                 text="Your Files",
                 style='Custom.TLabel').pack(pady=(0, 10))
        
        # Create file tree
        self.file_tree = ttk.Treeview(list_frame,
                                     columns=('Name', 'Size', 'Modified'),
                                     show='headings',
                                     height=10)
        
        # Configure columns
        self.file_tree.heading('Name', text='File Name')
        self.file_tree.heading('Size', text='Size')
        self.file_tree.heading('Modified', text='Last Modified')
        
        self.file_tree.column('Name', width=250)
        self.file_tree.column('Size', width=100)
        self.file_tree.column('Modified', width=150)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame,
                                 orient='vertical',
                                 command=self.file_tree.yview)
        self.file_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack tree and scrollbar
        self.file_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Bottom button frame
        bottom_frame = ttk.Frame(self.main_frame)
        bottom_frame.pack(pady=(20, 0))
        
        ttk.Button(bottom_frame,
                   text="Go Back",
                   command=self.go_back).pack()
        
        # Update file list
        self.update_file_list()

    def upload_file(self):
        file_path = filedialog.askopenfilename(title="Select a file to upload")
        if file_path:
            try:
                # Read and encrypt file
                with open(file_path, "rb") as file:
                    encrypted_data = self.cipher.encrypt(file.read())
                
                # Save to user's directory
                filename = os.path.basename(file_path)
                save_path = os.path.join(self.user_dir, f"encrypted_{filename}")
                
                with open(save_path, "wb") as encrypted_file:
                    encrypted_file.write(encrypted_data)
                
                messagebox.showinfo("Success", "File uploaded and encrypted successfully!")
                self.update_file_list()
                
            except Exception as e:
                messagebox.showerror("Error", f"Upload failed: {str(e)}")

    def download_file(self):
        selected = self.file_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a file to download")
            return
        
        try:
            file_name = self.file_tree.item(selected[0])['values'][0]
            file_path = os.path.join(self.user_dir, file_name)
            
            save_path = filedialog.asksaveasfilename(
                defaultextension="",
                initialfile=file_name.replace("encrypted_", "")
            )
            
            if save_path:
                with open(file_path, "rb") as encrypted_file:
                    decrypted_data = self.cipher.decrypt(encrypted_file.read())
                
                with open(save_path, "wb") as decrypted_file:
                    decrypted_file.write(decrypted_data)
                
                messagebox.showinfo("Success", "File downloaded successfully!")
        
        except Exception as e:
            messagebox.showerror("Error", f"Download failed: {str(e)}")

    def update_file_list(self):
        # Clear existing items
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        
        # List files in user's directory
        if os.path.exists(self.user_dir):
            for file in os.listdir(self.user_dir):
                if file.startswith("encrypted_"):
                    file_path = os.path.join(self.user_dir, file)
                    size = os.path.getsize(file_path)
                    modified = os.path.getmtime(file_path)
                    
                    self.file_tree.insert('', 'end', values=(
                        file,
                        self.format_size(size),
                        self.format_date(modified)
                    ))

    def format_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    def format_date(self, timestamp):
        from datetime import datetime
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M')

    def share_file(self):
        selected = self.file_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a file to share")
            return
        
        try:
            file_name = self.file_tree.item(selected[0])['values'][0]
            file_path = os.path.join(self.user_dir, file_name)
            
            # Decrypt the file
            with open(file_path, 'rb') as encrypted_file:
                encrypted_data = encrypted_file.read()
                decrypted_data = self.cipher.decrypt(encrypted_data)
            
            # Create temporary decrypted file
            temp_path = os.path.join(self.user_dir, f"temp_{file_name}")
            with open(temp_path, 'wb') as temp_file:
                temp_file.write(decrypted_data)
            
            try:
                # Generate random password
                password = self.generate_password()
                
                # Create multipart form data
                files = {
                    'file': (file_name.replace('encrypted_', ''), 
                            open(temp_path, 'rb'), 
                            'application/octet-stream')
                }
                data = {
                    'username': self.username,
                    'password': password
                }
                
                # Send to server using HTTP
                response = requests.post(
                    'http://127.0.0.1:5000/share',
                    files=files,
                    data=data
                )
                
                if response.status_code == 200:
                    share_url = response.json()["link"]
                    # Ensure URL is HTTP
                    if share_url.startswith('https://'):
                        share_url = 'http://' + share_url[8:]
                    self.show_share_dialog(share_url, password)
                else:
                    raise Exception(f"Server error: {response.text}")
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                
        except Exception as e:
            messagebox.showerror("Error", f"Sharing failed: {str(e)}")

    def show_share_dialog(self, share_url, password):
        # Create custom dialog
        share_dialog = tk.Toplevel(self.root)
        share_dialog.title("Share File")
        
        # Center the dialog
        dialog_width = 500
        dialog_height = 200
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - dialog_width) // 2
        y = (screen_height - dialog_height) // 2
        share_dialog.geometry(f'{dialog_width}x{dialog_height}+{x}+{y}')
        
        # Create main frame
        main_frame = ttk.Frame(share_dialog, padding="20")
        main_frame.pack(expand=True, fill='both')
        
        # Link section
        ttk.Label(main_frame, text="Shareable Link:", 
                 font=('Helvetica', 10, 'bold')).pack(pady=(0, 5))
        link_entry = ttk.Entry(main_frame, width=50)
        link_entry.insert(0, share_url)
        link_entry.pack(pady=(0, 10))
        
        # Password section
        ttk.Label(main_frame, text="Password:", 
                 font=('Helvetica', 10, 'bold')).pack(pady=(0, 5))
        pass_entry = ttk.Entry(main_frame, width=50)
        pass_entry.insert(0, password)
        pass_entry.pack(pady=(0, 10))
        
        def copy_link():
            self.root.clipboard_clear()
            self.root.clipboard_append(share_url)
            copy_link_btn.config(text="Link Copied!")
            self.root.after(2000, lambda: copy_link_btn.config(text="Copy Link"))
        
        def copy_password():
            self.root.clipboard_clear()
            self.root.clipboard_append(password)
            copy_pass_btn.config(text="Password Copied!")
            self.root.after(2000, lambda: copy_pass_btn.config(text="Copy Password"))
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        # Copy buttons
        copy_link_btn = ttk.Button(button_frame, text="Copy Link", 
                                 command=copy_link)
        copy_link_btn.pack(side='left', padx=5)
        
        copy_pass_btn = ttk.Button(button_frame, text="Copy Password", 
                                 command=copy_password)
        copy_pass_btn.pack(side='left', padx=5)
        
        # Close button
        ttk.Button(button_frame, text="Close", 
                  command=share_dialog.destroy).pack(side='left', padx=5)
        
        # Make entries read-only
        link_entry.config(state='readonly')
        pass_entry.config(state='readonly')
        
        # Make dialog modal
        share_dialog.transient(self.root)
        share_dialog.grab_set()
        self.root.wait_window(share_dialog)

    def load_or_generate_key(self):
        key_file = os.path.join("keys", f"{self.username}_key.key")
        os.makedirs("keys", exist_ok=True)
        
        if os.path.exists(key_file):
            with open(key_file, "rb") as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, "wb") as f:
                f.write(key)
            return key

    def generate_password(self):
        chars = string.ascii_letters + string.digits + string.punctuation
        return ''.join(random.choice(chars) for _ in range(12))

    def go_back(self):
        self.go_back_callback()

    def create_github_gist(self, file_path, file_name, password):
        try:
            # Read file content
            with open(file_path, 'rb') as file:
                content = file.read()
                
            # Create gist description
            description = f"Shared file: {file_name} (Encrypted)"
            
            # Create gist with encrypted content
            gist = self.github_user.create_gist(
                public=False,  # Make it private
                files={
                    file_name: InputFileContent(  # Use imported InputFileContent
                        content=self.cipher.encrypt(content).decode()
                    )
                },
                description=description
            )
            
            # Store gist info in database
            self.db.save_gist_info(
                gist_id=gist.id,
                file_name=file_name,
                password=password,
                created_at=datetime.now(),
                owner=self.username
            )
            
            return gist.html_url
            
        except Exception as e:
            raise Exception(f"Failed to create Gist: {str(e)}")

    def connect_to_server(self):
        """Attempt to connect to the server with retries"""
        for attempt in range(self.max_retries):
            try:
                response = requests.get(f"{self.server_url}/health")
                if response.status_code == 200:
                    return True
            except requests.exceptions.ConnectionError:
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                continue
        return False
