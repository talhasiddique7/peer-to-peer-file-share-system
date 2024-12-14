import socket
import hashlib
import os

base_file_directory = './uploads/'
# Helper function to compute SHA1 hash
def compute_sha1(file_path):
    sha1 = hashlib.sha1()
    with open(file_path, 'rb') as f:
        while chunk := f.read(4096):
            sha1.update(chunk)
    return sha1.hexdigest()

# Send a message to the tracker and receive a response
def send_message(tracker_ip, tracker_port, message):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((tracker_ip, tracker_port))
    client_socket.send(message.encode())
    response = client_socket.recv(1024).decode()
    client_socket.close()
    return response

def register(tracker_ip, tracker_port):
    username = input("Enter username: ")
    password = input("Enter password: ")
    print(send_message(tracker_ip, tracker_port, f"REGISTER:{username}:{password}"))

def login(tracker_ip, tracker_port):
    while True:
        username = input("Enter username: ")
        password = input("Enter password: ")
        response = send_message(tracker_ip, tracker_port, f"LOGIN:{username}:{password}")
        print(response)
        if "successful" in response:
            return username

def logout(tracker_ip, tracker_port, username):
    print(send_message(tracker_ip, tracker_port, f"LOGOUT:{username}"))
    return None  # Reset username to return to login menu

def create_group(tracker_ip, tracker_port, username):
    group_id = input("Enter group ID: ")
    print(send_message(tracker_ip, tracker_port, f"CREATE_GROUP:{username}:{group_id}"))

def request_join_group(tracker_ip, tracker_port, username):
    group_id = input("Enter group ID to request join: ")
    print(send_message(tracker_ip, tracker_port, f"REQUEST_JOIN:{username}:{group_id}"))

def view_requests(tracker_ip, tracker_port, username):
    group_id = input("Enter group ID: ")
    print(send_message(tracker_ip, tracker_port, f"VIEW_REQUESTS:{username}:{group_id}"))

def handle_request(tracker_ip, tracker_port, username):
    group_id = input("Enter group ID: ")
    user = input("Enter the username to approve/reject: ")
    decision = input("Approve or reject (approve/reject): ").strip().lower()
    print(send_message(tracker_ip, tracker_port, f"HANDLE_REQUEST:{username}:{group_id}:{user}:{decision}"))

def view_groups(tracker_ip, tracker_port, username):
    response = send_message(tracker_ip, tracker_port, f"VIEW_GROUPS:{username}")
    if response == "No groups available.":
        print(response)
        return None

    groups = response.split(',')
    for i, group in enumerate(groups, 1):
        print(f"{i}. {group}")
    try:
        group_id = groups[int(input("Select a group: ")) - 1]
        group_menu(tracker_ip, tracker_port, username, group_id)
    except (IndexError, ValueError):
        print("Invalid selection.")

def group_menu(tracker_ip, tracker_port, username, group_id):
    is_admin = send_message(tracker_ip, tracker_port, f"IS_ADMIN:{username}:{group_id}") == "True"

    while True:
        if is_admin:
            print("\n1. Upload File\n2. Delete File\n3. Download File\n4. View Files\n5. View Requests\n6. Handle Request\n7. Back")
        else:
            print("\n1. View Files\n2. Download File\n3. Back")

        choice = input("Choose an option: ")

        if is_admin and choice == '1':
            upload_file(tracker_ip, tracker_port, username, group_id)
        elif not is_admin and choice=='1':
            view_files(tracker_ip, tracker_port, group_id)
        elif is_admin and choice == '2':
            delete_file(tracker_ip, tracker_port, username, group_id)
        elif (is_admin and choice == '3') or (not is_admin and choice == '2'):
            download_file(tracker_ip, tracker_port, group_id)
        elif choice == '4':
            view_files(tracker_ip, tracker_port, group_id)
        elif is_admin and choice == '5':
            view_requests(tracker_ip, tracker_port, username)
        elif is_admin and choice == '6':
            handle_request(tracker_ip, tracker_port, username)
        elif (is_admin and choice == '7') or (not is_admin and choice == '3'):
            break
        else:
            print("Invalid option.")

def view_files(tracker_ip, tracker_port, group_id):
    response = send_message(tracker_ip, tracker_port, f"VIEW_FILES:{group_id}")
    if response == "No files available." or response == "Group not found.":
        print(response)
    else:
        print("Available files:")
        files = response.split(',')
        for file in files:
            print(file)

def upload_file(tracker_ip, tracker_port, username, group_id):
    file_path = input("Enter file path: ")
    
    if not os.path.exists(file_path):
        print("File not found.")
        return
    
    # Compute the SHA1 hash of the file
    sha1_hash = compute_sha1(file_path)
    
    # Send the upload command to the tracker
    response = send_message(tracker_ip, tracker_port, f"UPLOAD_FILE:{username}:{group_id}:{os.path.basename(file_path)}:{sha1_hash}")
    
    if response.startswith("UPLOAD_ACK"):
        # Upload the file if the tracker acknowledges the upload
        group_directory = os.path.join(base_file_directory, group_id)
        os.makedirs(group_directory, exist_ok=True)  # Create the group directory if it doesn't exist
        
        # Copy the file to the group's directory
        destination_file_path = os.path.join(group_directory, os.path.basename(file_path))
        with open(file_path, 'rb') as src_file:
            with open(destination_file_path, 'wb') as dest_file:
                dest_file.write(src_file.read())
        
        print(f"File '{os.path.basename(file_path)}' uploaded successfully to group '{group_id}'.")
    else:
        print("Upload failed:", response)

def delete_file(tracker_ip, tracker_port, username, group_id):
    file_name = input("Enter file name to delete: ")
    print(send_message(tracker_ip, tracker_port, f"DELETE_FILE:{username}:{group_id}:{file_name}"))

# Download a file from the tracker and save it to a specified location
def download_file(tracker_ip, tracker_port, group_id):
    file_name = input("Enter the name of the file you want to download: ")
    download_location = input("Enter the location where you want to save the file: ")

    if not os.path.isdir(download_location):
        print("Invalid download location.")
        return

    # Create a socket and send the download request
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((tracker_ip, tracker_port))
        sock.sendall(f"DOWNLOAD_FILE:{group_id}:{file_name}".encode())

        response = sock.recv(1024).decode()
        if response != "START_DOWNLOAD":
            print(f"Error: {response}")
            return

        # Open the file and start receiving data
        file_path = os.path.join(download_location, file_name)
        with open(file_path, 'wb') as f:
            while True:
                chunk = sock.recv(4096)
                if chunk.endswith(b"END_OF_FILE"):
                    f.write(chunk[:-11])  # Remove the EOF marker
                    break
                f.write(chunk)

        print(f"File '{file_name}' downloaded successfully to '{download_location}'.")



if __name__ == "__main__":
    tracker_ip = '127.0.0.1'
    tracker_port = 5000

    while True:
        username = None
        while not username:
            print("\n1. Register\n2. Login")
            choice = input("Choose an option: ")
            if choice == '1':
                register(tracker_ip, tracker_port)
            elif choice == '2':
                username = login(tracker_ip, tracker_port)

        while username:
            print("\n1. Create Group\n2. Request to Join Group\n3. View Groups\n4. Logout")
            choice = input("Choose an option: ")

            if choice == '1':
                create_group(tracker_ip, tracker_port, username)
            elif choice == '2':
                request_join_group(tracker_ip, tracker_port, username)
            elif choice == '3':
                view_groups(tracker_ip, tracker_port, username)
            elif choice == '4':
                username = logout(tracker_ip, tracker_port, username)
            else:
                print("Invalid option.")
