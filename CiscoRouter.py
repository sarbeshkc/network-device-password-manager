import paramiko
import time
import logging
from getpass import getpass

# Set up logging
logging.basicConfig(
    filename='cisco_router_update.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class CiscoRouter:
    def __init__(self, ip, username, current_password, enable_password=None):
        self.ip = ip
        self.username = username
        self.current_password = current_password
        self.enable_password = enable_password or current_password
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def connect(self):
        try:
            self.ssh.connect(
                self.ip,
                username=self.username,
                password=self.current_password,
                timeout=10
            )
            self.channel = self.ssh.invoke_shell()
            time.sleep(1)
            return True
        except Exception as e:
            logging.error(f"Connection failed: {str(e)}")
            return False

    def send_command(self, command, wait_time=1):
        self.channel.send(command + '\n')
        time.sleep(wait_time)
        output = ""
        while self.channel.recv_ready():
            output += self.channel.recv(1024).decode('ascii')
        return output

    def change_password(self, new_password):
        try:
            if not self.connect():
                raise Exception("Failed to connect to router")

            # Enter enable mode
            self.send_command('enable')
            self.send_command(self.enable_password)
            
            # Enter configuration mode
            self.send_command('configure terminal')
            
            # Update username and password
            self.send_command(f'username {self.username} privilege 15 secret {new_password}')
            
            # Exit config mode and save
            self.send_command('end')
            self.send_command('write memory')
            
            logging.info("Password updated successfully")
            print("Password updated successfully!")
            return True

        except Exception as e:
            logging.error(f"Failed to update password: {str(e)}")
            print(f"Error: {str(e)}")
            return False

        finally:
            self.ssh.close()

def main():
    # Get router details
    ip = input("Enter router IP address: ")
    username = input("Enter username: ")
    current_password = getpass("Enter current password: ")
    enable_password = getpass("Enter enable password (press Enter if same as current password): ") or current_password
    new_password = getpass("Enter new password: ")

    # Validate new password
    if len(new_password) < 8:
        print("Password must be at least 8 characters long")
        return

    # Initialize and update router
    router = CiscoRouter(ip, username, current_password, enable_password)
    router.change_password(new_password)

if __name__ == "__main__":
    main()