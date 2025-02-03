import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from tkinter.ttk import Style
from database import Database
from datetime import datetime
import os

class AuthWindow:
    def __init__(self, root, on_success):
        self.root = root
        self.root.title("Secure File System")
        
        # Set window size for desktop
        window_width = 1200
        window_height = 800
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        self.root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        
        self.on_success = on_success
        self.db = Database()
        
        # Configure style
        self.setup_styles()
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both', padx=20, pady=20)
        
        self.setup_login_ui()
    
    def setup_styles(self):
        style = Style()
        
        # Modern color scheme
        self.colors = {
            'primary': '#2C3E50',    # Dark blue
            'secondary': '#3498DB',   # Light blue
            'accent': '#E74C3C',      # Red
            'background': '#ECF0F1',  # Light gray
            'text': '#2C3E50',        # Dark blue
            'white': '#FFFFFF'        # White
        }
        
        style.configure('Custom.TFrame', 
                       background=self.colors['background'])
        
        style.configure('Custom.TLabel',
                       background=self.colors['background'],
                       foreground=self.colors['text'],
                       font=('Helvetica', 14))
        
        style.configure('Header.TLabel',
                       background=self.colors['background'],
                       foreground=self.colors['primary'],
                       font=('Helvetica', 32, 'bold'))
        
        style.configure('Custom.TButton',
                       font=('Helvetica', 14),
                       padding=15)
        
        style.map('Custom.TButton',
                 background=[('active', self.colors['primary'])])
        
        style.configure('TNotebook',
                       background=self.colors['background'])
        
        style.configure('TNotebook.Tab',
                       padding=[30, 15],
                       font=('Helvetica', 12))

    def create_entry(self, parent, placeholder, show=None):
        entry = tk.Entry(parent,
                        font=('Helvetica', 14),
                        bg=self.colors['white'],
                        fg=self.colors['text'],
                        show=show,
                        width=50)  # Increased width
        entry.insert(0, placeholder)
        entry.bind('<FocusIn>', lambda e: self.on_entry_click(e, placeholder))
        entry.bind('<FocusOut>', lambda e: self.on_focus_out(e, placeholder))
        return entry

    def setup_login_ui(self):
        login_tab = ttk.Frame(self.notebook, style='Custom.TFrame', padding=40)
        self.notebook.add(login_tab, text='Login')
        
        self.frame = ttk.Frame(login_tab, style='Custom.TFrame', padding=40)
        self.frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # Logo or icon
        ttk.Label(self.frame,
                 text="🔐",
                 font=('Helvetica', 64),
                 background=self.colors['background']).pack(pady=30)
        
        ttk.Label(self.frame,
                 text="Welcome to Secure File System",
                 style='Header.TLabel').pack(pady=30)
        
        self.email_entry = self.create_entry(self.frame, "Email")
        self.email_entry.pack(pady=20, ipady=12)
        
        self.password_entry = self.create_entry(self.frame, "Password", show="*")
        self.password_entry.pack(pady=20, ipady=12)
        
        login_btn = ttk.Button(self.frame,
                             text="Login",
                             style='Custom.TButton',
                             command=self.login)
        login_btn.pack(pady=30, ipadx=40)
        
        ttk.Separator(self.frame, orient='horizontal').pack(fill='x', pady=30)
        
        ttk.Button(self.frame,
                  text="Create New Account",
                  style='Custom.TButton',
                  command=self.show_signup_ui).pack(pady=15)

    def setup_signup_ui(self):
        signup_tab = ttk.Frame(self.notebook, style='Custom.TFrame', padding=40)
        self.notebook.add(signup_tab, text='Sign Up')
        self.notebook.select(signup_tab)
        
        self.frame = ttk.Frame(signup_tab, style='Custom.TFrame', padding=40)
        self.frame.place(relx=0.5, rely=0.5, anchor='center')
        
        ttk.Label(self.frame,
                 text="Create New Account",
                 style='Header.TLabel').pack(pady=30)
        
        self.username_entry = self.create_entry(self.frame, "Username")
        self.username_entry.pack(pady=20, ipady=12)
        
        self.email_entry = self.create_entry(self.frame, "Email")
        self.email_entry.pack(pady=20, ipady=12)
        
        self.password_entry = self.create_entry(self.frame, "Password", show="*")
        self.password_entry.pack(pady=20, ipady=12)
        
        ttk.Button(self.frame,
                  text="Sign Up",
                  style='Custom.TButton',
                  command=self.signup).pack(pady=30)
        
        ttk.Button(self.frame,
                  text="Back to Login",
                  style='Custom.TButton',
                  command=lambda: self.back_to_login(signup_tab)).pack(pady=15)

    def login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()
        
        if self.db.check_login(email, password):
            self.on_success(email)
        else:
            messagebox.showerror("Error", "Invalid credentials")

    def signup(self):
        username = self.username_entry.get()
        email = self.email_entry.get()
        password = self.password_entry.get()
        
        if self.db.add_user(username, email, password):
            messagebox.showinfo("Success", "Account created successfully!")
            self.back_to_login(self.notebook.select())
        else:
            messagebox.showerror("Error", "Failed to create account")

    def back_to_login(self, tab_to_close):
        self.notebook.forget(tab_to_close)
        self.notebook.select(0)

    def on_entry_click(self, event, placeholder):
        if event.widget.get() == placeholder:
            event.widget.delete(0, "end")
            if placeholder == "Password":
                event.widget.config(show="*")
            event.widget.config(fg='black')

    def on_focus_out(self, event, placeholder):
        if event.widget.get() == '':
            event.widget.insert(0, placeholder)
            if placeholder == "Password":
                event.widget.config(show='')
            event.widget.config(fg='grey')

    def show_signup_ui(self):
        """Method to handle signup button click"""
        self.setup_signup_ui()

    def setup_file_manager_ui(self):
        """Setup the main file manager interface after login"""
        self.clear_notebook()
        
        # Create main file manager tab
        file_tab = ttk.Frame(self.notebook, style='Custom.TFrame', padding=40)
        self.notebook.add(file_tab, text='File Manager')
        
        # Main centered container
        main_container = ttk.Frame(file_tab, style='Custom.TFrame')
        main_container.place(relx=0.5, rely=0.5, anchor='center')
        
        # Header with welcome message
        ttk.Label(main_container,
                 text="🗄️ Secure File Manager",
                 style='Header.TLabel').pack(pady=30)
        
        ttk.Label(main_container,
                 text=f"Welcome, {self.current_user}",
                 style='Custom.TLabel').pack(pady=10)
        
        # File operations frame
        operations_frame = ttk.Frame(main_container, style='Custom.TFrame')
        operations_frame.pack(pady=20, fill='both', expand=True)
        
        # Upload section
        upload_frame = ttk.Frame(operations_frame, style='Custom.TFrame')
        upload_frame.pack(pady=20)
        
        ttk.Button(upload_frame,
                   text="Upload File",
                   style='Custom.TButton',
                   command=self.upload_file).pack(pady=10)
        
        # Security level for upload
        security_frame = ttk.Frame(upload_frame, style='Custom.TFrame')
        security_frame.pack(pady=10)
        
        ttk.Label(security_frame,
                 text="Security Level:",
                 style='Custom.TLabel').pack(side='left', padx=10)
        
        self.security_level = ttk.Combobox(security_frame,
                                          values=['Private', 'Shared', 'Public'],
                                          state='readonly',
                                          width=20)
        self.security_level.set('Private')
        self.security_level.pack(side='left', padx=10)
        
        # Files list section
        files_frame = ttk.Frame(main_container, style='Custom.TFrame')
        files_frame.pack(pady=20, fill='both', expand=True)
        
        ttk.Label(files_frame,
                 text="Your Secure Files",
                 style='Custom.TLabel').pack(pady=10)
        
        # Create files treeview
        self.files_tree = ttk.Treeview(files_frame,
                                      columns=('Name', 'Size', 'Modified', 'Security'),
                                      show='headings',
                                      height=8)
        
        # Configure columns
        self.files_tree.heading('Name', text='File Name')
        self.files_tree.heading('Size', text='Size')
        self.files_tree.heading('Modified', text='Last Modified')
        self.files_tree.heading('Security', text='Security Level')
        
        self.files_tree.column('Name', width=250)
        self.files_tree.column('Size', width=100)
        self.files_tree.column('Modified', width=150)
        self.files_tree.column('Security', width=100)
        
        self.files_tree.pack(pady=10)
        
        # File operations buttons
        button_frame = ttk.Frame(main_container, style='Custom.TFrame')
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame,
                   text="Download",
                   style='Custom.TButton',
                   command=self.download_file).pack(side='left', padx=10)
        
        ttk.Button(button_frame,
                   text="Delete",
                   style='Custom.TButton',
                   command=self.delete_file).pack(side='left', padx=10)
        
        ttk.Button(button_frame,
                   text="Share",
                   style='Custom.TButton',
                   command=self.share_file).pack(side='left', padx=10)
        
        # Refresh file list
        self.refresh_file_list()

    def upload_file(self):
        """Handle secure file upload"""
        file_path = filedialog.askopenfilename()
        if file_path:
            try:
                # Get file info
                file_name = os.path.basename(file_path)
                security_level = self.security_level.get()
                
                # Read and encrypt file
                with open(file_path, 'rb') as file:
                    file_data = file.read()
                    encrypted_data = self.encrypt_file(file_data)
                
                # Save to secure storage
                self.db.save_file(
                    user=self.current_user,
                    filename=file_name,
                    data=encrypted_data,
                    security_level=security_level
                )
                
                # Log action
                self.log_action(f"Uploaded file: {file_name}")
                
                # Refresh display
                self.refresh_file_list()
                messagebox.showinfo("Success", "File uploaded securely!")
                
            except Exception as e:
                messagebox.showerror("Error", f"Upload failed: {str(e)}")

    def refresh_file_list(self):
        """Update the file list display"""
        # Clear existing items
        for item in self.files_tree.get_children():
            self.files_tree.delete(item)
        
        # Get user's files from database
        user_files = self.db.get_user_files(self.current_user)
        
        # Populate treeview
        for file in user_files:
            self.files_tree.insert('', 'end', values=(
                file['name'],
                self.format_size(file['size']),
                file['modified_date'],
                file['security_level']
            ))

    def format_size(self, size):
        """Format file size for display"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    def encrypt_file(self, data):
        """Encrypt file data before storage"""
        # Implement encryption logic here
        pass

    def download_file(self):
        """Handle secure file download"""
        selected = self.files_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a file to download")
            return
        
        try:
            file_name = self.files_tree.item(selected[0])['values'][0]
            save_path = filedialog.asksaveasfilename(
                defaultextension="",
                initialfile=file_name
            )
            
            if save_path:
                # Get and decrypt file
                encrypted_data = self.db.get_file_data(file_name, self.current_user)
                decrypted_data = self.decrypt_file(encrypted_data)
                
                # Save file
                with open(save_path, 'wb') as file:
                    file.write(decrypted_data)
                
                # Log action
                self.log_action(f"Downloaded file: {file_name}")
                messagebox.showinfo("Success", "File downloaded successfully!")
                
        except Exception as e:
            messagebox.showerror("Error", f"Download failed: {str(e)}")

    def delete_file(self):
        # Implement secure file deletion
        pass

    def share_file(self):
        # Implement secure file sharing
        pass

    def generate_keys(self):
        # Implement key generation
        pass

    def backup_keys(self):
        # Implement key backup
        pass

    def modify_permissions(self):
        # Implement permission modification
        pass

    def export_audit_log(self):
        # Implement audit log export
        pass

    def change_password(self):
        # Implement password change
        pass

    def clear_notebook(self):
        for item in self.notebook.tabs():
            self.notebook.forget(item)

    def decrypt_file(self, data):
        # Implement decryption logic here
        pass

    def log_action(self, action):
        """Log user actions for audit"""
        self.db.log_action(
            self.current_user,
            action,
            datetime.now()
        )
