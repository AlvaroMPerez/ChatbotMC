from flask import Flask
import os
from dotenv import load_dotenv
from controllers.webhook_controller import webhook_bp
from db.init_db import init_db

load_dotenv()

app = Flask(__name__)
app.register_blueprint(webhook_bp)

PORT = int(os.getenv('PORT', 5050))


if __name__ == '__main__':
    init_db()
    print(f"Server is listening on port: {PORT}")
    app.run(host='0.0.0.0', port=PORT, debug=True)