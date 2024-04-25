import os
import transformers
import requests
import torch
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# Create handle to Slack
app = App(token=os.environ["SLACK_BOT_TOKEN"])

url = "http://ia1.wse.jhu.edu:8080/v1/completions"
model_name = "meta-llama/Meta-Llama-3-8B-Instruct"
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

        # TODO:
        # 1. collect conversation history
        # 2. fix the issue with EOS token

        data = {
            "model": model_name,
            "messages": [
                {"role": "user", "content": body_without_user_id}
            ],
            "max_tokens": 100,
            "temperature": 0,
            "stop_token_ids": [128001, 128009],
            "stop_reason": 128001,
        }

        response = requests.post(url, headers=headers, json=data)
        print(response.json())
        output = response.json()["choices"][0]["text"]
        # say this output in the thread
        if "thread_ts" in body["event"]:
            thread_ts = body["event"]["thread_ts"]
            say(text=output, thread_ts=thread_ts)
        else:
            say(text=output)
    except Exception as e:
        print("Error: %s" % e)
        say("I'm sorry, I don't know the answer to that question. Here is an error message: ```%s```" % e)


# Set up the Slack interface to start servicing requests
print("Starting Slack handler - bot is ready to answer your questions!")
SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
