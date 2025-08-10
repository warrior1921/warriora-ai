import os
from flask import Flask, render_template, request, jsonify
from groq import Groq

app = Flask(__name__)

# Use environment variable or fallback to actual API key (keep it secret!)
api_key = os.getenv("GROQ_API_KEY") or "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"
client = Groq(api_key=api_key)

conversation_history = []
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

@app.route("/", methods=["GET"])
def index():
    # Render the chat page with the current conversation history
    return render_template("index.html", messages=conversation_history)


@app.route("/chat_api", methods=["POST"])
def chat_api():
    global introduced, conversation_history

    data = request.get_json()
    user_message = data.get("message", "").strip()
    if not user_message:
        return jsonify({"reply": "Please enter a message."})

    conversation_history.append({"sender": "user", "text": user_message})
    user_message_lower = user_message.lower()

    questions_about_creator = [
         "who is vishesh kannaujiya",
            "tell me about vishesh kannaujiya",
            "who created you",
            "tell me about your creator",
            "about vishesh kannaujiya",
            "your creator",
            "your developer",
            "who made you",
            "developer of warriora",
            "creator of warriora",
            "who is vishesh",
            "who is vk",
            "tell me about vishesh",
            "are you created by vishesh",
            "are you developed by vishesh",
            "are you created by vk",
    ]

    questions_about_mentor = [
        "who is vk's teacher",
        "is vishesh a student of varsha gupta",
        "is vishesh a student of varsha",
        "who is vishesh's teacher",
        "who is vk teacher",
        "who is the teacher of vk",
        "who is vishesh teacher",
        "who is varsha gupta",
        "tell me about varsha gupta",
        "vk's mentor",
        "vishesh's mentor",
        "mentor of vishesh",
        "teacher of vishesh",
        "who is varsha",
        "tell me about varsha",
        "who is vk's mentor",
        "who is vishesh's mentor",
        "who is vk mentor",
        "who is vishesh mentor",
        "professor of vishesh",
        "who taught vishesh",
        "who taught vk",
        "who teaches vishesh",
    ]

    if not introduced and user_message_lower in ["hi", "hello", "hey"]:
        bot_message = (
            "Hello! I'm Warriora, your AI assistant. "
            "My knowledge is up to 2023 only, so please keep your questions within that range."
        )
        introduced = True

    elif any(phrase in user_message_lower for phrase in questions_about_creator):
        system_prompt = (
            f"You are Warriora, an AI assistant created by Vishesh Kannaujiya. "
            f"Here is some info about Vishesh: {vishesh_info} "
            "Answer the user's question about Vishesh or your creator naturally and informatively."
        )
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        )
        bot_message = completion.choices[0].message.content

    elif any(phrase in user_message_lower for phrase in questions_about_mentor):
        system_prompt = (
            f"You are Warriora, an AI assistant created by Vishesh Kannaujiya. "
            f"Here is some info about Vishesh's mentor: {varsha_info} "
            "Answer the user's question about your mentor or teacher naturally and informatively."
        )
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        )
        bot_message = completion.choices[0].message.content

    else:
        system_prompt = (
            "You are Warriora, an AI assistant created by Vishesh Kannaujiya. "
            "Answer clearly and in an organized way, using numbered lists or bullet points. "
            "Put each point on a new line."
        )
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        )
        bot_message = completion.choices[0].message.content

    conversation_history.append({"sender": "bot", "text": bot_message})

    return jsonify({"reply": bot_message})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
