import logging

def log_command(command: str, user_id: int, username: str):
    logging.info(f"User {username} (ID: {user_id}) used command: {command}")
    
