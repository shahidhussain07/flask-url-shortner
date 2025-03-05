from flask import Flask, request, redirect, render_template
from pymongo import MongoClient
import config
import string
import random

# initialize flask app
app = Flask(__name__)

# connect to mongodb
client = MongoClient(config.MONGO_URI)
# Create database named demo if they don't exist already 
db = client.get_database()
# Create collection named data if it doesn't exist already 
collection = db.urls


#function to generate short code 
def generate_short_code(length = 6):
    charatcers = string.ascii_letters + string.digits
    return ''.join(random.choices(charatcers, k=length))


# home route
@app.route('/', methods=['POST','GET'])
def home():
    if request.method == 'POST':
        original_url = request.form.get("url")
        if original_url :
            # Check if URL is already shortened
            existing_url = collection.find_one({"original_url": original_url})
            if existing_url:
                return render_template("index.html", short_url=request.host_url + existing_url["short_code"])

            # generate short unique code
            short_code = generate_short_code()
            while collection.find_one({"short_code" :short_code}):
                short_code = generate_short_code()

             # Store in MongoDB
            collection.insert_one({"original_url": original_url, "short_code": short_code})
            return render_template('index.html', short_url=request.host_url+short_code)


    return render_template('index.html')


@app.route('/<short_code>')
def redirect_url(short_code):
    url_entry = collection.find_one({"short_code" : short_code})
    if url_entry:
        return redirect(url_entry["original_url"])

    return "URL not found", 404


if __name__ == '__main__':
    app.run(debug=True)