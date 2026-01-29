import discordoauth2
from flask import Flask, request, redirect
import json
import dotenv
import os
from main import verify_user


dotenv.load_dotenv(".env")
client = discordoauth2.Client(1464978953981788242, os.environ['OAUTH_TOKEN'], "http://localhost:8080/auth")
app = Flask(__name__)

@app.route("/auth")
def auth():
    code = request.args.get("code")
    if not code:
        return "No code provided", 400
    token = client.exchange_code(code)
    f = open('auth.json',)
    data = json.load(f)
    f.close()
    info = token.fetch_identify()
    data[info['id']] = f"{token.token},{token.refresh_token}"
    f = open('auth.json', 'w')
    json.dump(data, f)
    f.close()
    verify_user(info['id'])
    return "done"

app.run(host="0.0.0.0", port=8080)