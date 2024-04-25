import os
import requests
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# Create handle to Slack
app = App(token=os.environ["SLACK_BOT_TOKEN"])

url = "http://ia1.wse.jhu.edu:8080/v1/completions"
headers = {"Content-Type": "application/json"}

@app.event("app_mention")
def event_test(say, body):
    print("received question, working on answer.")
    try:
        # This gets the question text from the user
        print("The message is: %s" % body)

        user_id = body["authorizations"][0]["user_id"]
        body_without_user_id = body["event"]["text"].replace(f"<@{user_id}>", "")
        print("The message is: %s" % body_without_user_id)

        data = {
            "model": "meta-llama/Meta-Llama-3-8B-Instruct",
            "prompt": body_without_user_id,
            "max_tokens": 200,
            "temperature": 0,
            "stop_token_ids": [128001, 128009]
        }


        response = requests.post(url, headers=headers, json=data)
        print(response.json())
        output = response.json()["choices"][0]["text"]
        say(output)
    except Exception as e:
        print("Error: %s" % e)
        say("I'm sorry, I don't know the answer to that question. Here is an error message: ```%s```" % e)


# Set up the Slack interface to start servicing requests
print("Starting Slack handler - bot is ready to answer your questions!")
SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
