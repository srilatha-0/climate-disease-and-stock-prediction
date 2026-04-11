from flask import Flask, request, jsonify
import joblib   # or pickle

app = Flask(__name__)

# load your trained model
model = joblib.load("src/disease-stock.pkl")   # change path if needed

@app.route("/")
def home():
    return "Flask API is running"

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()

    # assuming your model takes list of features
    features = data["features"]

    prediction = model.predict([features])

    return jsonify({
        "prediction": int(prediction[0])
    })

if __name__ == "__main__":
    app.run(debug=True)