# P2P File Sharing System

A peer-to-peer (P2P) file sharing system implemented using Python and Tkinter for the GUI. This system allows users to create groups, join groups, upload and download files, and manage join requests.

## Features

- User Registration and Login
- Create and Join Groups
- Upload and Download Files
- View and Manage Join Requests
- View Files in Groups

## Requirements

- Python 3.x
- Tkinter (usually included with Python)
- Anaconda (optional, for managing Python environments)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/talhasiddique7/peer-to-peer-file-share-system.git
cd peer-to-peer-file-share-system
```

## Usage

1. Start the tracker server:

```bash
python tracker.py


```

2. Run the client application:

```bash
python client.py


```

## Project Structure

- `client.py`: Contains the client-side code for the P2P file sharing system.
- `tracker.py`: Contains the server-side code for managing users, groups, and file transfers.
- `README.md`: This file.

## Functions

### Client (client.py)

- `send_message(tracker_ip, tracker_port, message)`: Sends a message to the tracker server and returns the response.
- `compute_sha1(file_path)`: Computes the SHA1 hash of a file.
- `P2PApp`: Main GUI application class.
  - `show_login_screen()`: Displays the login screen.
  - `login()`: Handles user login.
  - `register()`: Handles user registration.
  - `show_main_menu()`: Displays the main menu.
  - `view_requests(group_id)`: Views join requests for a group.
  - `show_requests_menu(group_id, requests)`: Displays the join requests menu.
  - `manage_request(group_id, requester, action)`: Manages join requests.
  - `create_group()`: Creates a new group.
  - `request_join_group()`: Sends a join request to a group.
  - `view_groups()`: Views the groups the user belongs to.
  - `logout()`: Logs out the user.
  - `show_group_menu(groups)`: Displays the group menu.
  - `group_operations(group_id)`: Displays the group operations menu.
  - `upload_file(group_id)`: Uploads a file to a group.
  - `view_files(group_id)`: Views files in a group.
  - `prompt_download_file(group_id)`: Prompts the user to enter a file name to download.
  - `download_file(group_id, file_name)`: Downloads a file from a group.
  - `clear_screen()`: Clears the current screen.

### Server (tracker.py)

- `register_user(username, password)`: Registers a new user.
- `login_user(username, password)`: Logs in an existing user.
- `logout_user(username)`: Logs out a user.
- `create_group(username, group_id)`: Creates a new group.
- `request_join_group(username, group_id)`: Sends a join request to a group.
- `view_requests(admin, group_id)`: Views join requests for a group (admin only).
- `manage_request(admin, group_id, user, decision)`: Approves or rejects join requests.
- `is_admin(username, group_id)`: Checks if the user is an admin of the group.
- `view_groups(username)`: Views the groups the user belongs to.
- `upload_file(username, group_id, file_name, sha1_hash)`: Uploads a file to a group.
- `delete_file(username, group_id, file_name)`: Deletes a file from a group (admin only).
- `download_file(conn, group_id, file_name)`: Downloads a file from a group.
- `view_files(group_id)`: Views files in a group.
- `handle_client(conn, addr)`: Handles client requests.
- `start_tracker_server(host, port)`: Starts the tracker server.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.
