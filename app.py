import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from pymongo import MongoClient
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv
from bson.objectid import ObjectId


load_dotenv(".env")
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("No MongoDB URI found in environment variables. Please set MONGO_URI.")
SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key") 


app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.secret_key = SECRET_KEY


# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client["users"]            
users_collection = db["users"]  


# default landing page: login 
@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        
        user = users_collection.find_one({"username": username})

        if not user:
            flash("Username not found. Please try again.", "error")
            return redirect(url_for("index"))
        
        if user['password'] != password:
            flash("Invalid password. Please try again.", "error")
            return redirect(url_for("index"))
        
        session['username'] = username
        return redirect(url_for("home"))
    
    return render_template("index.html")

# register page
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")
        password2 = request.form.get("password2")

        # Check if username exists
        if users_collection.find_one({"username": username}):
            flash("Username already exists. Please choose another.", "error")
            return redirect(url_for("signup"))
        
        # Check if passwords match
        if password != password2:
            flash("Passwords do not match. Please try again.", "error")
            return redirect(url_for("signup"))
        
        # Insert new user into the database
        new_user = {"username": username, "password": password}
        users_collection.insert_one(new_user)
        session['username'] = username
        return redirect(url_for("home"))

    return render_template("signup.html")

# add dream page
from datetime import datetime
from bson import ObjectId

@app.route("/add_dream", methods=["GET", "POST"])
def add_dream():
    # Ensure the user is logged in
    if "username" not in session:
        flash("Please log in to add a dream.", "error")
        return redirect(url_for("index"))
    
    if request.method == "POST":
        # Get date parts from the form
        day = request.form.get("day")
        month = request.form.get("month")
        year = request.form.get("year")
        try:
            dream_date = datetime.strptime(f"{day}-{month}-{year}", "%d-%m-%Y")
        except ValueError:
            flash("Invalid date provided. Please use valid day, month, and year.", "error")
            return redirect(url_for("add_dream"))
        
        # Get the dream description
        description = request.form.get("dream-description")
        
        # Optionally, get the tags from a hidden input or a comma-separated string
        tags_str = request.form.get("tags", "")
        tags = [tag.strip() for tag in tags_str.split(",") if tag.strip()] if tags_str else []
        
        # Construct a new dream object
        import uuid
        dream_data = {
        "id": str(uuid.uuid4()), 
        "date": dream_date,
        "description": description,
        "tags": tags
}

        
        username = session.get("username")
        result = users_collection.update_one(
            {"username": username},
            {"$push": {"dreams": dream_data}}
        )
        
        if result.modified_count:
            flash("Dream added successfully!", "success")
        else:
            flash("Failed to add dream. Please try again.", "error")
        
        # Redirect back to add_dream page so notifications appear there
        return redirect(url_for("add_dream"))
    
    return render_template("add_dream.html")


# home page
@app.route("/home", methods = ["GET", "POST"])
def home():
    username = session.get("username")
    if not username:
        return redirect(url_for("index"))
    
    user_doc = users_collection.find_one({"username": username})
    dreams = user_doc.get("dreams", [])
    
    search_query = request.args.get("query", "").strip()
    if search_query:
        dreams = [dream for dream in dreams if search_query.lower() in dream.get("description", "").lower()]

    return render_template("home.html", username=username, dreams=dreams)

# analysis page
@app.route('/analysis')
def analysis():
    username = session.get("username")
    if not username:
        flash("Please log in.", "error")
        return redirect(url_for("index"))

    # 1) MOOD DISTRIBUTION
    pipeline_tags = [
        {"$match": {"username": username}},
        {"$unwind": {"path": "$dreams", "preserveNullAndEmptyArrays": True}},
        {"$unwind": {"path": "$dreams.tags", "preserveNullAndEmptyArrays": True}},
        {"$addFields": {"tag": {"$ifNull": ["$dreams.tags", "No Tag"]}}},
        {"$group": {"_id": "$tag", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    tag_trends = list(users_collection.aggregate(pipeline_tags))

    # 2) MONTHLY DREAM FREQUENCY
    # Group dreams by year and month of the dream date, then count.
    pipeline_months = [
        {"$match": {"username": username}},
        {"$unwind": {"path": "$dreams", "preserveNullAndEmptyArrays": True}},
        {
            "$group": {
                "_id": {
                    "year": {"$year": "$dreams.date"},
                    "month": {"$month": "$dreams.date"}
                },
                "count": {"$sum": 1}
            }
        },
        # Sort by year, then by month
        {"$sort": {"_id.year": 1, "_id.month": 1}}
    ]
    month_trends = list(users_collection.aggregate(pipeline_months))

    return render_template(
        'analysis.html',
        tag_trends=tag_trends,
        month_trends=month_trends
    )

#edit_dream page
@app.route("/edit_dream")
def edit_dream():
    dream_id = request.args.get("dream_id")
    username = session.get("username")
    
    if not username or not dream_id:
        flash("Invalid access. Please select a dream to edit.", "error")
        return redirect(url_for("home"))
    

    app.logger.debug(f"edit_dream: username={username}, dream_id={dream_id}")
    
    
    user_doc = users_collection.find_one({"username": username})
    if not user_doc or "dreams" not in user_doc:
        flash("User data error.", "error")
        return redirect(url_for("home"))
    
   
    dream = None
    for d in user_doc["dreams"]:
        if d.get("id") == dream_id:
            dream = d
            break
    
    if not dream:
        flash("Dream not found.", "error")
        return redirect(url_for("home"))
    
    tags = ["Happy", "Funny", "Excited", "XXXX"]
    
    return render_template("edit_dream.html", dream=dream, tags=tags)

@app.route("/update_dream", methods=["POST"])
def update_dream():
    username = session.get("username")
    if not username:
        flash("Please log in.", "error")
        return redirect(url_for("index"))


    dream_id = request.form.get("dream_id")
    action = request.form.get("action")  


    day = request.form.get("day")
    month = request.form.get("month")
    year = request.form.get("year")
    description = request.form.get("dream-description")
    tags_str = request.form.get("tags", "")
    tags = [tag.strip() for tag in tags_str.split(",") if tag.strip()] if tags_str else []

    user_doc = users_collection.find_one({"username": username})
    if not user_doc or "dreams" not in user_doc:
        flash("User data error.", "error")
        return redirect(url_for("home"))


    dream_list = user_doc["dreams"]
    target_dream = None
    for d in dream_list:
        if d.get("id") == dream_id:
            target_dream = d
            break

    if not target_dream:
        flash("Dream not found.", "error")
        return redirect(url_for("home"))


    if action == "edit":

        from datetime import datetime
        try:
            new_date = datetime.strptime(f"{day}-{month}-{year}", "%d-%m-%Y")
        except ValueError:
            flash("Invalid date provided.", "error")
            return redirect(url_for("edit_dream", dream_id=dream_id))

        target_dream["date"] = new_date
        target_dream["description"] = description
        target_dream["tags"] = tags


        users_collection.update_one(
            {"username": username, "dreams.id": dream_id},
            {"$set": {
                "dreams.$.date": new_date,
                "dreams.$.description": description,
                "dreams.$.tags": tags
            }}
        )
        flash("Dream updated successfully!", "success")

    elif action == "delete":
       
        dream_list = [d for d in dream_list if d.get("id") != dream_id]

        users_collection.update_one(
            {"username": username},
            {"$set": {"dreams": dream_list}}
        )
        flash("Dream deleted successfully!", "success")

    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
