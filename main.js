// Socket.io instance
const socket = io();

let username = null;
let roomId = null;
let isHost = false;
let connectedUsers = new Map(); // Store connected users and their IPs

document.addEventListener('DOMContentLoaded', () => {
    const createRoomForm = document.getElementById('createRoomForm');
    const joinRoomForm = document.getElementById('joinRoomForm');
    const messageForm = document.getElementById('messageForm');
    const fileInput = document.getElementById('fileInput');
    const useChacha = document.getElementById('useChacha');

    if (createRoomForm) {
        createRoomForm.addEventListener('submit', handleCreateRoom);
    }

    if (joinRoomForm) {
        joinRoomForm.addEventListener('submit', handleJoinRoom);
    }

    if (messageForm) {
        messageForm.addEventListener('submit', handleSendMessage);
    }

    if (fileInput) {
        fileInput.addEventListener('change', handleFileSelect);
    }

    // Initialize room if we're in one
    const roomIdElement = document.getElementById('roomId');
    if (roomIdElement) {
        initializeRoom(
            roomIdElement.dataset.roomId,
            roomIdElement.dataset.username,
            roomIdElement.dataset.isHost === 'true',
            roomIdElement.dataset.useChacha === 'true'
        );
    }

    // Log socket connection status
    socket.on('connect', () => {
        console.log('Socket.IO connected');
    });
});

async function handleCreateRoom(e) {
    e.preventDefault();
    const formData = new FormData(e.target);

    try {
        const response = await fetch('/create_room', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        if (data.success) {
            window.location.href = `/room/${data.room_id}`;
        } else {
            alert(data.error || 'Failed to create room');
        }
    } catch (error) {
        console.error('Failed to create room:', error);
        alert('Failed to create room. Please try again.');
    }
}

async function handleJoinRoom(e) {
    e.preventDefault();
    const formData = new FormData(e.target);

    try {
        const response = await fetch('/join_room', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        if (data.success) {
            window.location.href = `/room/${formData.get('room_id')}`;
        } else {
            alert(data.error || 'Failed to join room');
        }
    } catch (error) {
        console.error('Failed to join room:', error);
        alert('Failed to join room. Please try again.');
    }
}

function initializeRoom(rid, uname, host, useChacha = false) {
    roomId = rid;
    username = uname;
    isHost = host;

    console.log(`Initializing room: ${roomId} as ${username} (Host: ${isHost})`);

    socket.emit('join', { room: roomId, useChacha });

    socket.on('user_joined', (data) => {
        console.log('User joined:', data);
        displaySystemMessage(`${data.username} joined the room`);
        connectedUsers.set(data.username, data.ip);
        updateUserList();
    });

    socket.on('user_left', (data) => {
        console.log('User left:', data);
        displaySystemMessage(`${data.username} left the room`);
        connectedUsers.delete(data.username);
        updateUserList();
    });

    socket.on('chat_message', (data) => {
        console.log('Received message:', data);
        displayMessage(data);
    });

    socket.on('file_share', (data) => {
        displayMessage({
            sender: data.sender,
            type: 'file',
            name: data.fileName,
            data: data.fileData
        });
    });

    socket.on('kicked', (data) => {
        if (data.username === username) {
            alert('You have been kicked from the room');
            window.location.href = '/';
        }
    });

    socket.on('banned', (data) => {
        if (data.username === username) {
            alert('You have been banned from the room');
            window.location.href = '/';
        }
    });
}

function updateUserList() {
    const userList = document.getElementById('userList');
    if (!userList) return;

    userList.innerHTML = '';

    connectedUsers.forEach((ip, user) => {
        const li = document.createElement('li');
        li.className = 'mb-2';

        if (isHost) {
            li.innerHTML = `
                ${user} ${ip ? `(${ip})` : ''}
                <div class="btn-group btn-group-sm mt-1">
                    <button onclick="kickUser('${user}')" class="btn btn-danger btn-sm">Kick</button>
                    <button onclick="banUser('${user}')" class="btn btn-danger btn-sm">Ban</button>
                </div>
            `;
        } else {
            li.textContent = user;
        }

        userList.appendChild(li);
    });
}

function kickUser(username) {
    if (isHost) {
        socket.emit('kick_user', { username, room: roomId });
    }
}

function banUser(username) {
    if (isHost) {
        socket.emit('ban_user', { username, room: roomId });
    }
}

async function handleSendMessage(e) {
    e.preventDefault();
    const messageInput = document.getElementById('messageInput');
    const message = messageInput.value.trim();

    if (message) {
        console.log('Sending message:', message);
        socket.emit('chat_message', {
            room: roomId,
            message: message
        });

        messageInput.value = '';
    }
}

async function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        const maxSize = 5 * 1024 * 1024; // 5MB limit
        if (file.size > maxSize) {
            alert('File size must be less than 5MB');
            return;
        }

        const reader = new FileReader();
        reader.onload = function(e) {
            console.log('Sending file:', file.name);
            socket.emit('file_share', {
                room: roomId,
                fileName: file.name,
                fileData: e.target.result
            });
            displaySystemMessage(`Sent file: ${file.name}`);
        };
        reader.readAsDataURL(file);
    }
}

function displayMessage(message) {
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) return;

    const messageElement = document.createElement('div');
    messageElement.className = 'message';

    if (message.type === 'file') {
        messageElement.innerHTML = `
            <strong>${message.sender}:</strong>
            <a href="${message.data}" download="${message.name}" class="btn btn-sm btn-secondary ms-2">
                Download ${message.name}
            </a>
        `;
    } else {
        messageElement.innerHTML = `
            <strong>${message.sender}:</strong>
            ${escapeHtml(message.content)}
        `;
    }

    chatMessages.appendChild(messageElement);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function displaySystemMessage(message) {
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) return;

    const messageElement = document.createElement('div');
    messageElement.className = 'system-message';
    messageElement.textContent = message;
    chatMessages.appendChild(messageElement);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}