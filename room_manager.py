from collections import defaultdict
import time
import bleach

class RoomManager:
    def __init__(self):
        self.rooms = {}
        self.banned_ips = defaultdict(set)
        self.failed_attempts = defaultdict(int)

    def sanitize_input(self, input_text):
        """Sanitize input to prevent malicious data injection."""
        return bleach.clean(input_text)

    def room_exists(self, room_id):
        """Check if a room ID already exists."""
        return room_id in self.rooms

    def create_room(self, room_id, password, host_username, security_key):
        """Create a new room with a security key."""
        room_id = self.sanitize_input(room_id)
        host_username = self.sanitize_input(host_username)
        self.rooms[room_id] = {
            'password': password,
            'security_key': security_key,
            'host': host_username,
            'users': {},
            'created_at': time.time()
        }

    def validate_room(self, room_id, password, security_key):
        """Validate room credentials including security key."""
        room_id = self.sanitize_input(room_id)
        if room_id not in self.rooms:
            return False
        room = self.rooms[room_id]
        return (room['password'] == password and room['security_key'] == security_key)

    def add_user(self, room_id, username, ip_address):
        """Add user to the room if not banned."""
        room_id = self.sanitize_input(room_id)
        username = self.sanitize_input(username)
        if room_id in self.rooms:
            if ip_address in self.banned_ips[room_id]:
                return False  # User is banned
            self.rooms[room_id]['users'][username] = ip_address
            return True
        return False

    def remove_user(self, room_id, ip_address):
        """Remove user from the room by IP address."""
        room_id = self.sanitize_input(room_id)
        if room_id in self.rooms:
            users_to_remove = [u for u, ip in self.rooms[room_id]['users'].items() if ip == ip_address]
            for username in users_to_remove:
                del self.rooms[room_id]['users'][username]

    def ban_user(self, room_id, ip_address):
        """Ban a user from a room and remove them."""
        room_id = self.sanitize_input(room_id)
        if room_id in self.rooms:
            self.banned_ips[room_id].add(ip_address)
            self.remove_user(room_id, ip_address)

    def get_user_ip(self, room_id, username):
        """Get the IP address associated with a username in a room."""
        room_id = self.sanitize_input(room_id)
        username = self.sanitize_input(username)
        if room_id in self.rooms:
            return self.rooms[room_id]['users'].get(username)
        return None

    def record_failed_attempt(self, ip_address):
        """Track failed login attempts and trigger ban if exceeded."""
        self.failed_attempts[ip_address] += 1
        if self.failed_attempts[ip_address] >= 3:
            return True  # Ban should be triggered
        return False

    def get_room_users(self, room_id):
        """Retrieve a list of users currently in a room."""
        room_id = self.sanitize_input(room_id)
        if room_id in self.rooms:
            return [(username, ip) for username, ip in self.rooms[room_id]['users'].items()]
        return []
