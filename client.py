import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
import os
import socket
import hashlib

# Network communication functions
def send_message(tracker_ip, tracker_port, message):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((tracker_ip, tracker_port))
    client_socket.send(message.encode())
    response = client_socket.recv(1024).decode()
    client_socket.close()
    return response

# Helper function to compute SHA1
def compute_sha1(file_path):
    sha1 = hashlib.sha1()
    with open(file_path, 'rb') as f:
        while chunk := f.read(4096):
            sha1.update(chunk)
    return sha1.hexdigest()

# GUI Application Class
class P2PApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("P2P File Sharing App")
        self.geometry("400x300")
        self.username = None
        self.tracker_ip = '127.0.0.1'
        self.tracker_port = 5000
        self.show_login_screen()

    # ---------------- Login Screen ----------------
    def show_login_screen(self):
        self.clear_screen()
        tk.Label(self, text="Login to P2P App", font=("Arial", 16)).pack(pady=10)
        tk.Label(self, text="Username:").pack()
        self.username_entry = tk.Entry(self)
        self.username_entry.pack()
        tk.Label(self, text="Password:").pack()
        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.pack()

        tk.Button(self, text="Login", command=self.login).pack(pady=5)
        tk.Button(self, text="Register", command=self.register).pack()

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        response = send_message(self.tracker_ip, self.tracker_port, f"LOGIN:{username}:{password}")
        if "successful" in response:
            self.username = username
            self.show_main_menu()
        else:
            messagebox.showerror("Error", response)

    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        response = send_message(self.tracker_ip, self.tracker_port, f"REGISTER:{username}:{password}")
        messagebox.showinfo("Info", response)

    # ---------------- Main Menu ----------------
    def show_main_menu(self):
        self.clear_screen()
        tk.Label(self, text=f"Welcome, {self.username}", font=("Arial", 16)).pack(pady=10)

        tk.Button(self, text="Create Group", command=self.create_group).pack(pady=5)
        tk.Button(self, text="Join Group", command=self.request_join_group).pack(pady=5)
        tk.Button(self, text="View Groups", command=self.view_groups).pack(pady=5)
        tk.Button(self, text="Logout", command=self.logout).pack(pady=5)

    # ---------------- Manage Join Requests ----------------
    def view_requests(self, group_id):
        response = send_message(self.tracker_ip, self.tracker_port, f"VIEW_REQUESTS:{group_id}")
        if response == "No pending requests.":
            messagebox.showinfo("Info", response)
        else:
            requests = response.split(",")
            self.show_requests_menu(group_id, requests)

    def show_requests_menu(self, group_id, requests):
        self.clear_screen()
        if not requests or requests == ['']:
            tk.Label(self, text="No pending join requests", font=("Arial", 14), fg="red").pack(pady=10)
        else:
            tk.Label(self, text="Pending Join Requests", font=("Arial", 16)).pack(pady=10)
            for req in requests:
                if ":" in req:
                    try:
                        requester = req.split(":")[1]
                        frame = tk.Frame(self)
                        frame.pack(pady=5)
                        tk.Label(frame, text=f"User: {requester}").pack(side="left")
                        tk.Button(frame, text="Accept", command=lambda u=requester: self.manage_request(group_id, u, "ACCEPT")).pack(side="left")
                        tk.Button(frame, text="Reject", command=lambda u=requester: self.manage_request(group_id, u, "REJECT")).pack(side="left")
                    except ValueError:
                        print(f"Invalid request format: {req}")
                        tk.Label(self, text=f"Invalid request format: {req}", fg="red").pack(pady=10)
                else:
                    print(f"Invalid request format: {req}")
                    tk.Label(self, text=f"Invalid request format: {req}", fg="red").pack(pady=10)
        
        tk.Button(self, text="Back", command=lambda: self.group_operations(group_id)).pack(pady=10)

    def manage_request(self, group_id, requester, action):
        response = send_message(self.tracker_ip, self.tracker_port, f"MANAGE_REQUEST:{self.username}:{group_id}:{requester}:{action}")
        messagebox.showinfo("Info", response)
        self.view_requests(group_id)

    # ---------------- Group Functions ----------------
    def create_group(self):
        group_id = simpledialog.askstring("Input", "Enter Group ID:")
        if group_id:
            response = send_message(self.tracker_ip, self.tracker_port, f"CREATE_GROUP:{self.username}:{group_id}")
            messagebox.showinfo("Info", response)

    def request_join_group(self):
        group_id = simpledialog.askstring("Input", "Enter Group ID:")
        if group_id:
            response = send_message(self.tracker_ip, self.tracker_port, f"REQUEST_JOIN:{self.username}:{group_id}")
            messagebox.showinfo("Info", response)

    def view_groups(self):
        response = send_message(self.tracker_ip, self.tracker_port, f"VIEW_GROUPS:{self.username}")
        if response == "No groups available.":
            messagebox.showinfo("Info", response)
        else:
            groups = response.split(",")
            self.show_group_menu(groups)

    def logout(self):
        response = send_message(self.tracker_ip, self.tracker_port, f"LOGOUT:{self.username}")
        messagebox.showinfo("Info", response)
        self.username = None
        self.show_login_screen()

    # ---------------- Group Menu ----------------
    def show_group_menu(self, groups):
        self.clear_screen()
        tk.Label(self, text="Your Groups", font=("Arial", 16)).pack(pady=10)
        for group in groups:
            tk.Button(self, text=group, command=lambda g=group: self.group_operations(g)).pack(pady=5)
        tk.Button(self, text="Back", command=self.show_main_menu).pack(pady=10)

    def group_operations(self, group_id):
        self.clear_screen()
        tk.Label(self, text=f"Group: {group_id}", font=("Arial", 16)).pack(pady=10)
        
        tk.Button(self, text="Upload File", command=lambda: self.upload_file(group_id)).pack(pady=5)
        tk.Button(self, text="View Files", command=lambda: self.view_files(group_id)).pack(pady=5)
        tk.Button(self, text="Download File", command=lambda: self.download_file(group_id)).pack(pady=5)
        tk.Button(self, text="Manage Join Requests", command=lambda: self.view_requests(group_id)).pack(pady=5)
        
        tk.Button(self, text="Back", command=self.show_main_menu).pack(pady=10)

    def upload_file(self, group_id):
        file_path = filedialog.askopenfilename(title="Select File to Upload")
        if file_path:
            sha1_hash = compute_sha1(file_path)
            response = send_message(self.tracker_ip, self.tracker_port, f"UPLOAD_FILE:{self.username}:{group_id}:{os.path.basename(file_path)}:{sha1_hash}")
            messagebox.showinfo("Info", response)

    def view_files(self, group_id):
        response = send_message(self.tracker_ip, self.tracker_port, f"VIEW_FILES:{group_id}")
        if response == "No files available." or response == "Group not found.":
            messagebox.showinfo("Info", response)
        else:
            files = response.split(",")
            file = simpledialog.askstring("Files", f"Files:\n{', '.join(files)}\nEnter file name to download:")
            if file:
                self.download_file(group_id, file)

    def download_file(self, group_id, file_name):
        download_location = filedialog.askdirectory(title="Select Download Location")
        if download_location:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((self.tracker_ip, self.tracker_port))
                sock.sendall(f"DOWNLOAD_FILE:{group_id}:{file_name}".encode())
                response = sock.recv(1024).decode()
                if response == "START_DOWNLOAD":
                    file_path = os.path.join(download_location, file_name)
                    with open(file_path, 'wb') as f:
                        while True:
                            chunk = sock.recv(4096)
                            if not chunk:
                                break
                            f.write(chunk)
                    messagebox.showinfo("Info", "File downloaded successfully.")
                else:
                    messagebox.showerror("Error", response)

    def clear_screen(self):
        for widget in self.winfo_children():
            widget.destroy()

# Run the application
if __name__ == "__main__":
    app = P2PApp()
    app.mainloop()
