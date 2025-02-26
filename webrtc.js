class P2PConnection {
    constructor(roomId, username, onMessage, onPeerConnect, onPeerDisconnect, useChacha = false) {
        this.roomId = roomId;
        this.username = username;
        this.peers = new Map();
        this.onMessage = onMessage;
        this.onPeerConnect = onPeerConnect;
        this.onPeerDisconnect = onPeerDisconnect;
        this.cryptoHandler = new CryptoHandler(useChacha);
        this.encryptionKey = null;
        this.sharedSecret = null;

        // Generate initial X25519 keypair
        this.initializeKeyPair();
    }

    async initializeKeyPair() {
        const keyPair = await this.cryptoHandler.generateX25519KeyPair();
        this.privateKey = keyPair.privateKey;
        this.publicKey = keyPair.publicKey;
    }

    async initConnection(targetPeer) {
        const configuration = {
            iceServers: [
                { urls: 'stun:stun.l.google.com:19302' }
            ]
        };

        const connection = new RTCPeerConnection(configuration);
        const dataChannel = connection.createDataChannel('chat');

        dataChannel.onmessage = async (event) => {
            try {
                // Rotate key if needed before decryption
                if (this.sharedSecret) {
                    this.encryptionKey = await this.cryptoHandler.rotateKey(this.sharedSecret);
                }

                const decryptedMessage = await this.cryptoHandler.decryptMessage(
                    this.encryptionKey,
                    event.data
                );
                this.onMessage(JSON.parse(decryptedMessage));
            } catch (error) {
                console.error('Failed to decrypt message:', error);
            }
        };

        dataChannel.onopen = () => {
            console.log('Data channel opened');
            this.onPeerConnect(targetPeer);
        };

        dataChannel.onclose = () => {
            console.log('Data channel closed');
            this.onPeerDisconnect(targetPeer);
            this.peers.delete(targetPeer);
        };

        connection.onicecandidate = (event) => {
            if (event.candidate) {
                socket.emit('p2p_signal', {
                    type: 'ice_candidate',
                    candidate: event.candidate,
                    target: targetPeer,
                    room: this.roomId
                });
            }
        };

        return { connection, dataChannel };
    }

    async createOffer(targetPeer) {
        const { connection, dataChannel } = await this.initConnection(targetPeer);

        const offer = await connection.createOffer();
        await connection.setLocalDescription(offer);

        // Include our public key in the offer
        socket.emit('p2p_signal', {
            type: 'offer',
            offer: offer,
            publicKey: await crypto.subtle.exportKey("raw", this.publicKey),
            target: targetPeer,
            room: this.roomId
        });

        this.peers.set(targetPeer, { connection, dataChannel });
    }

    async handleOffer(offer, fromPeer, peerPublicKey) {
        const { connection, dataChannel } = await this.initConnection(fromPeer);

        await connection.setRemoteDescription(offer);
        const answer = await connection.createAnswer();
        await connection.setLocalDescription(answer);

        // Generate shared secret from peer's public key
        const importedPeerKey = await crypto.subtle.importKey(
            "raw",
            peerPublicKey,
            { name: "X25519" },
            true,
            []
        );
        this.sharedSecret = await this.cryptoHandler.deriveSharedSecret(
            this.privateKey,
            importedPeerKey
        );

        // Generate initial encryption key
        this.encryptionKey = await this.cryptoHandler.rotateKey(this.sharedSecret);

        socket.emit('p2p_signal', {
            type: 'answer',
            answer: answer,
            publicKey: await crypto.subtle.exportKey("raw", this.publicKey),
            target: fromPeer,
            room: this.roomId
        });

        this.peers.set(fromPeer, { connection, dataChannel });
    }

    async handleAnswer(answer, fromPeer, peerPublicKey) {
        const peer = this.peers.get(fromPeer);
        if (peer) {
            await peer.connection.setRemoteDescription(answer);

            // Generate shared secret from peer's public key
            const importedPeerKey = await crypto.subtle.importKey(
                "raw",
                peerPublicKey,
                { name: "X25519" },
                true,
                []
            );
            this.sharedSecret = await this.cryptoHandler.deriveSharedSecret(
                this.privateKey,
                importedPeerKey
            );

            // Generate initial encryption key
            this.encryptionKey = await this.cryptoHandler.rotateKey(this.sharedSecret);
        }
    }

    async handleIceCandidate(candidate, fromPeer) {
        const peer = this.peers.get(fromPeer);
        if (peer) {
            await peer.connection.addIceCandidate(candidate);
        }
    }

    async sendMessage(message) {
        try {
            // Rotate key if needed before encryption
            if (this.sharedSecret) {
                this.encryptionKey = await this.cryptoHandler.rotateKey(this.sharedSecret);
            }

            const encryptedMessage = await this.cryptoHandler.encryptMessage(
                this.encryptionKey,
                JSON.stringify({
                    type: 'message',
                    content: message,
                    sender: this.username,
                    timestamp: Date.now()
                })
            );

            this.peers.forEach(({ dataChannel }) => {
                if (dataChannel.readyState === 'open') {
                    dataChannel.send(encryptedMessage);
                }
            });
        } catch (error) {
            console.error('Failed to send message:', error);
        }
    }

    async sendFile(file) {
        try {
            const reader = new FileReader();
            reader.onload = async (e) => {
                // Rotate key if needed before encryption
                if (this.sharedSecret) {
                    this.encryptionKey = await this.cryptoHandler.rotateKey(this.sharedSecret);
                }

                const encryptedFile = await this.cryptoHandler.encryptMessage(
                    this.encryptionKey,
                    JSON.stringify({
                        type: 'file',
                        name: file.name,
                        data: e.target.result,
                        sender: this.username,
                        timestamp: Date.now()
                    })
                );

                this.peers.forEach(({ dataChannel }) => {
                    if (dataChannel.readyState === 'open') {
                        dataChannel.send(encryptedFile);
                    }
                });
            };
            reader.readAsDataURL(file);
        } catch (error) {
            console.error('Failed to send file:', error);
        }
    }
}