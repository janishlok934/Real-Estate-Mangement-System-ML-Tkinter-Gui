from flask import Flask
from flask_socketio import SocketIO, send
import eventlet

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins='*')


@socketio.on('message')
def handle_message(msg):
    print(f"Received: {msg}")
    # Basic chatbot response
    if "hello" in msg.lower():
        response = "Hi there! How can I help you?"
    elif "bye" in msg.lower():
        response = "Goodbye! Have a great day."
    elif "name" in msg.lower():
        response = "I am a simple chatbot created in Python."
    else:
        response = f"You said: {msg}"

    send(response, broadcast=True)


if __name__ == '__main__':
    print("Starting Chatbot Server...")
    socketio.run(app, host='localhost', port=5000)
