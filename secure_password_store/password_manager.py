import logging
from cryptography.fernet import Fernet
import json
import os
import base64
import logging


class PasswordManager:
    def __init__(self, key_file='secret.key', store_file='passwords.json'):
        # Get the directory where the script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Create full paths for both files
        self.key_file = os.path.join(script_dir, key_file)
        self.store_file = os.path.join(script_dir, store_file)
        
        self.key = self.load_or_generate_key()
        self.fernet = Fernet(self.key)
        self.passwords = self.load_passwords()

    def load_or_generate_key(self):
        if os.path.exists(self.key_file):
            with open(self.key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
            return key

    def load_passwords(self):
        if os.path.exists(self.store_file):
            try:
                with open(self.store_file, 'r') as f:
                    encrypted_data = json.load(f)
                # Convert base64 string back to bytes for decryption
                loaded_passwords = {}
                for k, v in encrypted_data.items():
                    loaded_passwords[k] = base64.b64decode(v.encode())
                return loaded_passwords
            except Exception as e:
                logging.info(f"Error loading passwords: {e}")
                return {}
        return {}

    def save_passwords(self):
        """Save passwords to file"""
        try:
            # Convert bytes to base64 strings for JSON serialization
            data_to_save = {k: base64.b64encode(v).decode() for k, v in self.passwords.items()}
            logging.info(f"Debug: Saving data: {list(data_to_save.keys())}")
            
            # Atomic write using temporary file
            temp_file = self.store_file + '.tmp'
            with open(temp_file, 'w') as f:
                json.dump(data_to_save, f, indent=2)
            
            # Replace original file
            os.replace(temp_file, self.store_file)
            print(f"Debug: Passwords saved to {self.store_file}")
            
        except Exception as e:
            print(f"Error saving passwords: {e}")
    
    def add_password(self, identifier, password):
        """Add a new password with validation"""
        if not identifier or not identifier.strip():
            print("Error: Identifier cannot be empty.")
            return False
        
        if not password:
            print("Error: Password cannot be empty.")
            return False
        
        identifier = identifier.strip()
        
        # Check for duplicate identifier
        if identifier in self.passwords:
            print(f"Error: Identifier '{identifier}' already exists. Please choose a unique identifier.")
            return False
        
        try:
            encrypted = self.fernet.encrypt(password.encode())
            self.passwords[identifier] = encrypted
            self.save_passwords()
            print(f"Password for identifier '{identifier}' added successfully.")
            return True
        except Exception as e:
            print(f"Error adding password: {e}")
            return False
    
    def get_password(self, identifier):
        """Retrieve password with better error handling"""
        if not identifier:
            print("Error: Identifier cannot be empty.")
            return None
        
        try:
            encrypted = self.passwords.get(identifier.strip())
            if encrypted:
                return self.fernet.decrypt(encrypted).decode()
            print(f"No password found for identifier '{identifier}'.")
            return None
        except Exception as e:
            print(f"Error retrieving password: {e}")
            return None

# Example usage and testing:
def test_password_manager():
    pm = PasswordManager()
    
    # Test 1: Add passwords
    print("=== Testing Password Addition ===")
    pm.add_password("gmail", "mypassword123")
    pm.add_password("facebook", "fb_password456")
    
    # Test 2: Try to add duplicate identifier
    print("\n=== Testing Duplicate Identifier ===")
    pm.add_password("gmail", "different_password")  # Should fail
    
    # Test 3: Retrieve passwords
    print("\n=== Testing Password Retrieval ===")
    retrieved1 = pm.get_password("gmail")
    retrieved2 = pm.get_password("facebook")
    print(f"Gmail password: {retrieved1}")
    print(f"Facebook password: {retrieved2}")
    
    # Test 4: Try to retrieve non-existent password
    print("\n=== Testing Non-existent Password ===")
    retrieved3 = pm.get_password("nonexistent")
    
    # Test 5: Create new instance to test persistence
    print("\n=== Testing Persistence (New Instance) ===")
    pm2 = PasswordManager()
    retrieved4 = pm2.get_password("gmail")
    print(f"Gmail password from new instance: {retrieved4}")
    
if __name__ == "__main__":
    test_password_manager()