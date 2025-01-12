import paramiko
import time
import logging
from getpass import getpass

# Set up logging
logging.basicConfig(
    filename='hp_switch_update.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class HPSwitch:
    def __init__(self, ip, username, current_password):
        self.ip = ip
        self.username = username
        self.current_password = current_password
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
            time.sleep(1)  # Wait for shell prompt
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
                raise Exception("Failed to connect to switch")

            # Enter configuration mode
            self.send_command('configure terminal')
            
            # Change password
            self.send_command(f'password manager user-name {self.username} plaintext {new_password}')
            
            # Save configuration
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
    # Get switch details
    ip = input("Enter switch IP address: ")
    username = input("Enter username: ")
    current_password = getpass("Enter current password: ")
    new_password = getpass("Enter new password: ")

    # Validate new password
    if len(new_password) < 8:
        print("Password must be at least 8 characters long")
        return

    # Initialize and update switch
    switch = HPSwitch(ip, username, current_password)
    switch.change_password(new_password)

if __name__ == "__main__":
    main()