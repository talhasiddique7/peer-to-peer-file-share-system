import socket
import threading
import hashlib
import os

user_db = {}  # Stores user credentials and group memberships
logged_in_users = {}  # Tracks currently logged-in users
groups = {}  # Stores group information and files
base_file_directory = './uploads/'  # Base directory for storing files

# Ensure base directory exists
os.makedirs(base_file_directory, exist_ok=True)

# Register a new user
def register_user(username, password):
    if username in user_db:
        return "User already exists."
    user_db[username] = {
        'password': hashlib.sha256(password.encode()).hexdigest(),
        'groups': []
    }
    return "Registration successful."

# Login an existing user
def login_user(username, password):
    if username not in user_db:
        return "User not found."
    if user_db[username]['password'] == hashlib.sha256(password.encode()).hexdigest():
        logged_in_users[username] = True
        return "Login successful."
    return "Invalid credentials."

# Logout a user
def logout_user(username):
    if username in logged_in_users:
        del logged_in_users[username]
        return "Logout successful."
    return "User not logged in."

# Create a new group
def create_group(username, group_id):
    if group_id in groups:
        return "Group ID already exists."
    groups[group_id] = {
        'admin': username,
        'members': [username],
        'files': {},
        'requests': []
    }
    user_db[username]['groups'].append(group_id)
    return f"Group '{group_id}' created successfully."

# Send a join request to a group
def request_join_group(username, group_id):
    if group_id not in groups:
        return "Group not found."
    if username in groups[group_id]['members']:
        return "Already a member."
    if username in groups[group_id]['requests']:
        return "Join request already sent."
    groups[group_id]['requests'].append(username)
    return "Join request sent."

# View join requests (Admin only)
def view_requests(admin, group_id):
    if group_id not in groups or groups[group_id]['admin'] != admin:
        return "Unauthorized action."
    if not groups[group_id]['requests']:
        return "No pending requests."
    return ','.join(groups[group_id]['requests'])

# Approve or reject join requests
def handle_request(admin, group_id, user, decision):
    if group_id not in groups or groups[group_id]['admin'] != admin:
        return "Unauthorized action."
    if user not in groups[group_id]['requests']:
        return "No such request."

    groups[group_id]['requests'].remove(user)
    if decision == "approve":
        groups[group_id]['members'].append(user)
        user_db[user]['groups'].append(group_id)
        return f"{user} approved to join group '{group_id}'."
    return f"{user}'s request to join group '{group_id}' was rejected."

# Check if the user is an admin of the group
def is_admin(username, group_id):
    return "True" if groups[group_id]['admin'] == username else "False"

# View groups the user belongs to (Read from user_db)
def view_groups(username):
    if user_db[username]['groups']:
        return ','.join(user_db[username]['groups'])
    return "No groups available."

def upload_file(username, group_id, file_name, sha1_hash):
    # Ensure the group exists
    if group_id not in groups:
        return "Group not found."

    # Create the group directory if it doesn't exist
    group_directory = os.path.join(base_file_directory, group_id)
    os.makedirs(group_directory, exist_ok=True)  # Create the directory

    # Define the full path for the file
    file_path = os.path.join(group_directory, file_name)

    # Store the file information in the group's file record
    groups[group_id]['files'][file_name] = {'sha1': sha1_hash, 'owner': username}

    # Acknowledge the upload
    return f"UPLOAD_ACK: File '{file_name}' uploaded successfully to group '{group_id}'."

# Delete a file from a group (Admin only)
def delete_file(username, group_id, file_name):
    if file_name in groups[group_id]['files'] and groups[group_id]['files'][file_name]['owner'] == username:
        del groups[group_id]['files'][file_name]
        return f"File '{file_name}' deleted successfully."
    return "Unauthorized or file not found."

# Download a file from a group

def download_file(conn, group_id, file_name):
    # Validate if the group and file exist
    file_path = os.path.join(base_file_directory, group_id, file_name)
    
    if os.path.exists(file_path):
        conn.sendall("START_DOWNLOAD".encode())  # Notify the client to start downloading

        # Send file in chunks
        with open(file_path, 'rb') as f:
            while chunk := f.read(4096):
                conn.sendall(chunk)

        # Send end-of-file marker
        conn.sendall(b"END_OF_FILE")
        print(f"File '{file_name}' sent successfully.")
    else:
        conn.sendall("File not found.".encode())

# View files in a group
def view_files(group_id):
    if group_id not in groups:
        return "Group not found."
    if not groups[group_id]['files']:
        return "No files available."
    return ','.join(groups[group_id]['files'].keys())

# Handle client requests
def handle_client(conn, addr):
    print(f"Connected to {addr}")
    try:
        while True:
            data = conn.recv(1024).decode()
            if not data:
                break

            command, *params = data.split(":")
            if command == "REGISTER":
                response = register_user(*params)
            elif command == "LOGIN":
                response = login_user(*params)
            elif command == "LOGOUT":
                response = logout_user(params[0])
            elif command == "CREATE_GROUP":
                response = create_group(*params)
            elif command == "REQUEST_JOIN":
                response = request_join_group(*params)
            elif command == "VIEW_REQUESTS":
                response = view_requests(*params)
            elif command == "HANDLE_REQUEST":
                response = handle_request(*params)
            elif command == "IS_ADMIN":
                response = is_admin(*params)
            elif command == "VIEW_GROUPS":
                response = view_groups(params[0])
            elif command == "UPLOAD_FILE":
                response = upload_file(*params)
            elif command == "DELETE_FILE":
                response = delete_file(*params)
            elif command == "DOWNLOAD_FILE":
                # Handle file download here
                download_file(conn, *params)
                return  # End connection after file download
            elif command == "VIEW_FILES":
                response = view_files(params[0])
            else:
                response = "Invalid command."

            if command != "DOWNLOAD_FILE":
                conn.sendall(response.encode())
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()


# Start the tracker server
def start_tracker_server(host='0.0.0.0', port=5000):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    print(f"Tracker server running on {host}:{port}")
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()

if __name__ == "__main__":
    start_tracker_server()
