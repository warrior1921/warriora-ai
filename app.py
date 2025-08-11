import os
import sqlite3
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from groq import Groq
import getpass

app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # Change this to a strong secret key

owner_name = getpass.getuser()


# Database Setup
DB_FILE = "chatbot.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # User table
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    # Messages table
    c.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            sender TEXT,
            text TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Groq API
api_key = os.getenv("GROQ_API_KEY") or "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"
client = Groq(api_key=api_key)

introduced = False

vishesh_info = (
    "Vishesh Kannaujiya is a 17-year-old student focused on technology, software engineering, "
    "and full-stack development. He is the developer of Warriora, an AI assistant created "
    "to demonstrate his learning and skills in IT."
)

varsha_info = (
    "Varsha Gupta has been an exceptional mentor and guide for Vishesh since the very beginning of his technology learning journey. "
    "She has been a pivotal influence in shaping his early growth in IT. She has taught vishesh the adca course in her computer institute named SUMITRA HIGH-TECH INSTITUTION & EDUCATION POINT. SHE IS THE DIRECTOR AT SUMITRA HIGH-TECH INSTITUTION & EDUCATION POINT."
)

# ------------------- Auth Routes -------------------

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if request.method == 'POST':
        user_message = request.form['message'].strip().lower()

        # Get previous message from session (if any)
        prev_message = session.get('last_message')

        # Basic context logic
        if "thank" in user_message and prev_message:
            bot_reply = "You're welcome! Glad I could help 😊"
        elif "again" in user_message and prev_message:
            bot_reply = f"Sure! Here’s what I said before: {prev_message}"
        else:
            bot_reply = "Hi there! How can I help you?"

        # Save this message for next time
        session['last_message'] = bot_reply

        return render_template("chat.html", bot_reply=bot_reply)

    return render_template("chat.html")
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()
        session['username'] = username

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT id, password FROM users WHERE username=?", (username,))
        user = c.fetchone()
        conn.close()

        if user and user[1] == password:
            session["user_id"] = user[0]
            return redirect(url_for("index"))
        else:
            return render_template("auth.html", error="Invalid username or password")

    return render_template("auth.html")
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/register", methods=["POST"])
def register():
    username = request.form.get("username").strip()
    password = request.form.get("password").strip()

    if not username or not password:
        return render_template("auth.html", error="Please fill all fields")

    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()
        return render_template("auth.html", success="Account created! Please log in.")
    except sqlite3.IntegrityError:
        return render_template("auth.html", error="Username already exists")

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("login"))

# ------------------- Chat Routes -------------------
@app.route("/", methods=["GET"])
def index():
    if "user_id" not in session:
        return redirect(url_for("login"))

    # Load user's chat history from DB
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT sender, text FROM messages WHERE user_id=? ORDER BY id", (session["user_id"],))
    messages = [{"sender": row[0], "text": row[1]} for row in c.fetchall()]
    conn.close()

    return render_template("index.html", messages=messages)

# Store per-user conversation in session
def get_conversation():
    return session.get("conversation", [])

def update_conversation(role, content):
    conversation = session.get("conversation", [])
    conversation.append({"role": role, "content": content})
    session["conversation"] = conversation[-10:]  # keep last 10 messages


@app.route("/chat_api", methods=["POST"])
def chat_api():
    if "user_id" not in session:
        return jsonify({"reply": "You must be logged in to chat."})

    global introduced
    user_id = session["user_id"]

    data = request.get_json()
    user_message = data.get("message", "").strip()
    if not user_message:
        return jsonify({"reply": "Please enter a message."})

    save_message(user_id, "user", user_message)
    user_message_lower = user_message.lower()

    # Conversation lists
    questions_about_creator = [
        "who is vishesh kannaujiya", "tell me about vishesh kannaujiya",
        "who created you", "tell me about your creator", "about vishesh kannaujiya",
        "your creator", "your developer", "who made you", "developer of warriora",
        "creator of warriora", "who is vishesh", "who is vk", "tell me about vishesh",
        "are you created by vishesh", "are you developed by vishesh",
        "are you created by vk"
    ]

    questions_about_mentor = [
        "who is vk's teacher", "is vishesh a student of varsha gupta",
        "is vishesh a student of varsha", "who is vishesh's teacher", "who is vk teacher",
        "who is the teacher of vk", "who is vishesh teacher", "who is varsha gupta",
        "tell me about varsha gupta", "vk's mentor", "vishesh's mentor", "mentor of vishesh",
        "teacher of vishesh", "who is varsha", "tell me about varsha",
        "who is vk's mentor", "who is vishesh's mentor", "who is vk mentor",
        "who is vishesh mentor", "professor of vishesh", "who taught vishesh",
        "who taught vk", "who teaches vishesh"
    ]

    # Get conversation history
    conversation = get_conversation()

    # Add system prompt only at start of conversation
    if not conversation:
        system_prompt = (
            "You are Warriora, an AI assistant created by Vishesh Kannaujiya. "
            "You can remember recent messages in this chat to maintain context for follow-ups. "
            "When answering, be clear and organized, using bullet points or numbered lists."
        )
        conversation.append({"role": "system", "content": system_prompt})

    # Special greeting
    if not introduced and user_message_lower in ["hi", "hello", "hey"]:
        owner_name = session.get("username", "Guest")
        bot_message = (
            f"Hello {owner_name}, I'm Warriora, your AI assistant. "
            "My knowledge is up to 2023 only, so please keep your questions within that range."
        )
        introduced = True

    # Creator question
    elif any(phrase in user_message_lower for phrase in questions_about_creator):
        bot_message = f"Vishesh Kannaujiya is my creator. {vishesh_info}"

    # Mentor question
    elif any(phrase in user_message_lower for phrase in questions_about_mentor):
        bot_message = f"My mentor is Varsha Gupta. {varsha_info}"

    # User asks their name
    elif user_message_lower in ["what is my name","what is my name?", "tell me my name", "do you know my name", "who am i"]:
        owner_name = session.get("username", "Guest")
        bot_message = f"{owner_name}."

    else:
        # Add user's new message to conversation
        conversation.append({"role": "user", "content": user_message})

        # Call AI with full context
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=conversation,
        )
        bot_message = completion.choices[0].message.content

    # Save both in DB and session history
    update_conversation("user", user_message)
    update_conversation("assistant", bot_message)
    save_message(user_id, "bot", bot_message)

    return jsonify({"reply": bot_message})


# Save message to DB
def save_message(user_id, sender, text):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO messages (user_id, sender, text) VALUES (?, ?, ?)", (user_id, sender, text))
    conn.commit()
    conn.close()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
