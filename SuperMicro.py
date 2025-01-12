import requests
import urllib3
import logging
from getpass import getpass

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Set up logging
logging.basicConfig(
    filename='supermicro_update.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class SupermicroServer:
    def __init__(self, ip, username, current_password, port=443):
        self.ip = ip
        self.username = username
        self.current_password = current_password
        self.port = port
        self.base_url = f"https://{ip}:{port}"
        self.session = requests.Session()
        self.session.verify = False  # For self-signed certificates

    def login(self):
        try:
            login_url = f"{self.base_url}/cgi/login.cgi"
            payload = {
                "name": self.username,
                "pwd": self.current_password
            }
            
            response = self.session.post(login_url, data=payload, timeout=10)
            response.raise_for_status()
            
            if "Set-Cookie" in response.headers:
                logging.info("Successfully logged into IPMI")
                return True
            
            logging.error("Login failed - no session cookie received")
            return False

        except requests.RequestException as e:
            logging.error(f"Login failed: {str(e)}")
            return False

    def change_password(self, new_password):
        try:
            if not self.login():
                raise Exception("Failed to login to IPMI")

            change_url = f"{self.base_url}/cgi/config_user.cgi"
            payload = {
                "username": self.username,
                "password": new_password,
                "confirm_password": new_password,
                "op": "config_user"
            }

            response = self.session.post(change_url, data=payload, timeout=10)
            response.raise_for_status()

            if "successful" in response.text.lower():
                logging.info("Password changed successfully")
                print("Password updated successfully!")
                return True
            
            logging.error("Failed to change password - unexpected response")
            return False

        except Exception as e:
            logging.error(f"Failed to update password: {str(e)}")
            print(f"Error: {str(e)}")
            return False

        finally:
            self.session.close()

def main():
    # Get server details
    ip = input("Enter server IPMI IP address: ")
    username = input("Enter IPMI username (default is ADMIN): ") or "ADMIN"
    current_password = getpass("Enter current password: ")
    new_password = getpass("Enter new password: ")
    port = input("Enter IPMI port (default is 443): ") or 443

    # Validate new password
    if len(new_password) < 8:
        print("Password must be at least 8 characters long")
        return

    # Initialize and update server
    server = SupermicroServer(ip, username, current_password, int(port))
    server.change_password(new_password)

if __name__ == "__main__":
    main()