from flask import Flask, jsonify

app = Flask(__name__)

# Home Page
@app.route('/')
def home():
    return "Welcome to the Flask Testing App!"

# Sample API Endpoint
@app.route('/api/sample', methods=['GET'])
def sample_api():
    data = {
        'message': 'This is a sample API response',
        'status': 'success'
    }
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
