from flask import Flask, jsonify, render_template

app = Flask(__name__)
app.secret_key = "nous-app-secret-key"

@app.route('/')
def index():
    try:
        return render_template('index.html')
    except:
        return jsonify({
            "status": "ok",
            "message": "NOUS Personal Assistant is running successfully"
        })

@app.route('/health')
def health():
    return jsonify({"status": "ok", "version": "1.0.0"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)