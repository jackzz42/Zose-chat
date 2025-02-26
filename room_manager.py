from collections import defaultdict
import time

class RoomManager:
    def __init__(self):
        self.rooms = {}
        self.banned_ips = defaultdict(set)
        self.failed_attempts = defaultdict(int)

    def room_exists(self, room_id):
        """Check if a room ID already exists"""
        return room_id in self.rooms

    def create_room(self, room_id, password, host_username, security_key):
        """Create a new room with security key"""
        self.rooms[room_id] = {
            'password': password,
            'security_key': security_key,  # Add security key
            'host': host_username,
            'users': {},  # Changed to dict to store username->ip mapping
            'created_at': time.time()
        }

    def validate_room(self, room_id, password, security_key):
        """Validate room credentials including security key"""
        if room_id not in self.rooms:
            return False
        room = self.rooms[room_id]
        return (room['password'] == password and 
                room['security_key'] == security_key)

    def add_user(self, room_id, username, ip_address):
        """Add user to room"""
        if room_id in self.rooms:
            if ip_address in self.banned_ips[room_id]:
                return False
            self.rooms[room_id]['users'][username] = ip_address
            return True
        return False

    def remove_user(self, room_id, ip_address):
        """Remove user from room"""
        if room_id in self.rooms:
            users_to_remove = []
            for username, ip in self.rooms[room_id]['users'].items():
                if ip == ip_address:
                    users_to_remove.append(username)

            for username in users_to_remove:
                del self.rooms[room_id]['users'][username]

    def ban_user(self, room_id, ip_address):
        """Ban user from room"""
        if room_id in self.rooms:
            self.banned_ips[room_id].add(ip_address)
            self.remove_user(room_id, ip_address)

    def get_user_ip(self, room_id, username):
        """Get IP address for a username in a room"""
        if room_id in self.rooms:
            return self.rooms[room_id]['users'].get(username)
        return None

    def record_failed_attempt(self, ip_address):
        """Record failed login attempt"""
        self.failed_attempts[ip_address] += 1
        if self.failed_attempts[ip_address] >= 3:
            return True
        return False

    def get_room_users(self, room_id):
        """Get list of users in room"""
        if room_id in self.rooms:
            return [(username, ip) for username, ip in self.rooms[room_id]['users'].items()]
        return []