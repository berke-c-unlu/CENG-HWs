from flask import Flask, render_template, url_for, request, redirect, session, flash, get_flashed_messages
import secrets
from flask_pymongo import pymongo
from flask.helpers import get_root_path
from markupsafe import escape
from bson.objectid import ObjectId

app = Flask(__name__)

# MongoDB username password and connection string
USERNAME = "admin"
PASSWORD = "X4xRb0eiIJR1mOky"
CONNECTION_STRING = "mongodb+srv://"+ USERNAME + ":"+ PASSWORD + "@ceng-495-hw1-cluster.gowisyo.mongodb.net/?retryWrites=true&w=majority"

# Secret key for session
app.secret_key = secrets.token_urlsafe(16)


client = pymongo.MongoClient(CONNECTION_STRING)
print("Connected to MongoDB")

db = client.ecommerceDB
Products = db.Products
Users = db.Users
print("Retrieved collections from database")


@app.route('/', methods=['GET', 'POST'])
def get_home():

    # Get filter option from form
    # If no filter option is selected, default to All
    filter_option = request.form.get('filter', 'All')
    
    # Filter products
    if filter_option == 'All':
        products = Products.find()
    elif filter_option == 'Monitors':
        products = Products.find({'type': 'Monitors'})
    elif filter_option == 'Clothing':
        products = Products.find({'type': 'Clothing'})
    elif filter_option == 'Computer Components':
        products = Products.find({'type': 'Computer Components'})
    elif filter_option == 'Snacks':
        products = Products.find({'type': 'Snacks'})

    if get_flashed_messages():
        return render_template('index.html', products=products, error=get_flashed_messages()[0])

    
    # Render home page with products
    return render_template('index.html', products=products)


@app.route('/login', methods=['GET'])
def get_login():
    # If user is already logged in, redirect to home page
    if 'user' in session:
        flash("You are already logged in")
        return redirect(url_for('get_home'))
    

    # If there is an error, display it
    if get_flashed_messages():
        return render_template('login.html', error=get_flashed_messages()[0])
    
    # Render login page
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def post_login():
    # Get username and password from form
    user = request.form['username'] if request.form['username'] != "" else None
    password = request.form['password'] if request.form['password'] != "" else None

    # If username or password is empty, return error
    if(user == None or password == None):
        print("Please enter a username/password")
        return render_template('login.html', error="Please enter a username/password")

    # search in database
    print("Searching in database")
    user_in_db = list(Users.find({'username': user}))

    # User does not exist
    if len(user_in_db) == 0:
        print("User does not exist")
        return render_template('login.html', error="User does not exist")
    
    # Password is incorrect
    if user_in_db[0]['password'] != password:
        print("Password is incorrect")
        return render_template('login.html', error="Password is incorrect")

    # User exists
    print("User exists, logging in")

    # Add user to session
    session['user'] = user
    session['id'] = str(user_in_db[0]['_id'])
    if user_in_db[0]['is_admin'] == True:
        session['is_admin'] = True
    else:
        session['is_admin'] = False

    # Redirect to home page
    return redirect(url_for('get_home'))


# View product page
@app.route('/product/<product_id>', methods=['GET'])
def get_product(product_id):
    # Get product from database
    curr_product = Products.find({'_id': ObjectId(product_id)})

    # return the product page with the product
    return render_template('product.html', product=product_id, current=curr_product)

@app.route('/product/<product_id>', methods=['POST'])
def post_product(product_id):

    # if user is not logged in redirect to login page
    # Restrict this page
    if 'user' not in session:
        flash("Please login to review")
        return redirect('/login')
    
    # get product and user id
    current_product = Products.find({'_id': ObjectId(product_id)})
    user_id = session['id']

    # Get review and rating from form
    review = request.form['review']
    rating = int(request.form['rating'])

    # User review
    user_review = {'product_id': ObjectId(product_id), 'p_name': current_product[0]['name'], 'review': review, 'rating': rating}

    # Product review
    product_review = {'user_id': ObjectId(user_id), 'u_name': session['user'], 'review': review, 'rating': rating}
    
    # Check whether user make a review before
    existing_review = list(Users.find({'_id': ObjectId(user_id), 'reviews.product_id': ObjectId(product_id)}))

    # Update user reviews
    update_user_review(user_review, existing_review, user_id, product_id)

    # Check whether user make a review before
    existing_review = list(Products.find({'_id': ObjectId(product_id), 'reviews.user_id': ObjectId(user_id)}))

    # Update product reviews
    update_product_review(product_review, existing_review, user_id, product_id)

    return redirect(url_for('get_product', product_id=product_id, current=current_product))



# Update user rating, if user made a review before update the review, else create a new review
def update_user_review(user_review, searched_review, user_id, product_id):
    # If not, create a new review    
    if len(searched_review) == 0:
        Users.update_one({'_id': ObjectId(user_id)}, {'$push': {'reviews': user_review }})
        user_reviews = list(Users.find({'_id': ObjectId(session['id'])}))[0]['reviews']
        
    # If yes, update the review
    else:
        Users.update_one({'_id': ObjectId(user_id), 'reviews.product_id': ObjectId(product_id)}, {'$set': {'reviews.$': user_review}})
        user_reviews = list(Users.find({'_id': ObjectId(session['id'])}))[0]['reviews']

    # Update user reviews
    new_user_rating = calculate_user_rating(user_reviews)
    Users.update_one({'_id': ObjectId(user_id)}, {'$set': {'average_rating': new_user_rating}})

# Update product rating, if product has a review before update the review, else create a new review
def update_product_review(product_review, searched_review, user_id, product_id):
    # If not, create a new review
    if len(searched_review) == 0:
        Products.update_one({'_id': ObjectId(product_id)}, {'$push': {'reviews': product_review }})
        product_reviews = list(Products.find({'_id': ObjectId(product_id)}))[0]['reviews']

    # If yes, update the review
    else:
        Products.update_one({'_id': ObjectId(product_id), 'reviews.user_id': ObjectId(user_id)}, {'$set': {'reviews.$': product_review}})
        product_reviews = list(Products.find({'_id': ObjectId(product_id)}))[0]['reviews']
    
    # Update product reviews
    new_product_rating = calculate_product_rating(product_reviews)
    Products.update_one({'_id': ObjectId(product_id)}, {'$set': {'rating': new_product_rating}})


def calculate_user_rating(review_tuples):
    if len(review_tuples) == 0:
        return 0.0
    else:
        return sum(list(map(lambda x: x['rating'], review_tuples))) / len(review_tuples)

def calculate_product_rating(review_tuples):
    if len(review_tuples) == 0:
        return 0.0
    else:
        return sum(list(map(lambda x: x['rating'], review_tuples))) / len(review_tuples)


@app.route('/logout')
def logout():
    # if user is not logged in redirect to home page
    if 'user' not in session:
        flash("Please login before logout")
        return redirect('/login')

    # Remove user from session
    print("Logging out", session['user'])
    session.pop('user', None)
    session.pop('is_admin', None)
    session.pop('id', None)

    # Redirect to home page
    return redirect('/')


@app.route('/profile')
def profile():
    # if user is not logged in redirect to home page
    if 'user' not in session:
        flash("Please login to view profile")
        return redirect('/login')
        
    # Get current user
    current_user = session['id']

    # Get user from database
    user = Users.find_one({'_id': ObjectId(current_user)})

    # Render profile page
    return render_template('profile.html', user=user)




@app.route('/add-user', methods=['GET'])
def get_add_user():
    # if user is not logged in redirect to home page
    if 'user' not in session and ('is_admin' not in session or session['is_admin'] == False):
        flash("Please login to add user, only admin can add user")
        return redirect('/login')

    # Render add user page
    return render_template('add_user.html')

@app.route('/add-user', methods=['POST'])
def post_add_user():
    # if user is not logged in redirect to home page
    if 'user' not in session and ('is_admin' not in session or session['is_admin'] == False):
        flash("Please login to add user, only admin can add user")
        return redirect('/login')


    # Get username and password and admin chocie from form
    username = request.form['username']
    password = request.form['password']
    is_admin = request.form.get('is_admin')

    if is_admin == "" or username == "" or password == "":
        flash("Please fill in all fields")
        return redirect('/add-user')

    is_admin = True if is_admin == 'True' else False

    # Check if username already exists
    # If it does, render add user, page do not add user
    all_users = list(Users.find({}))
    if username in all_users:
        flash("Username already exists")
        return redirect('/add-user')

    # Add user to database
    Users.insert_one({'username': username,
                        'password': password,
                        'average_rating': 0.0,
                        'reviews': [],
                        'is_admin': is_admin,
    })


    return redirect('/add-user')



@app.route('/add-item', methods=['GET'])
def get_add_item():
    # if user is not logged in redirect to home page
    if 'user' not in session and ('is_admin' not in session or session['is_admin'] == False):
        flash("Please login to add item, only admin can add item")
        return redirect('/login')

    # Render add item page
    return render_template('add_item.html')

@app.route('/add-item', methods=['POST'])
def post_add_item():
    # if user is not logged in redirect to home page
    if 'user' not in session and ('is_admin' not in session or session['is_admin'] == False):
        flash("Please login to add item, only admin can add item")
        return redirect('/login')


    # Get all the information from the form
    type = request.form.get('category')
    name = request.form['name']
    description = request.form['description']
    price = int(request.form['price'])
    seller = request.form['seller']
    image = request.form['imageurl']

    # If any of the fields are empty, render add item page
    if type== "" or name == "" or description == "" or price == 0 or seller == "" or image == "":
        flash("Please fill in all fields")
        return redirect('/add-item')

    # If type is Monitors or Computer Components, get spec from form
    if type == 'Monitors' or type == 'Computer Components':
        spec = request.form['spec']

        # If spec is empty, render add item page
        if spec == "":
            flash("Please fill in all fields")
            return redirect('/add-item')
        
        # Add item to database
        Products.insert_one({'name': name, 
                                'description': description, 
                                'price': price, 
                                'seller': seller, 
                                'image': image, 
                                'rating': 0.0, 
                                'reviews': [], 
                                'type': type, 
                                'spec': spec
        })

    # If type is Clothing, get colour and size from form
    if type == 'Clothing':
        colour = request.form['colour']
        size = request.form['size']

        # If colour or size is empty, render add item page
        if colour == "" or size == "":
            flash("Please fill in all fields")
            return redirect('/add-item')
        
        
        # Add item to database
        Products.insert_one({'name': name,
                                'description': description,
                                'price': price,
                                'seller': seller,
                                'image': image,
                                'rating': 0.0,
                                'reviews': [],
                                'type': type,
                                'colour': colour,
                                'size': size
        })

    # If type is Snacks, add item to database
    if type == 'Snacks':
        Products.insert_one({'name': name,
                                'description': description,
                                'price': price,
                                'seller': seller,
                                'image': image,
                                'rating': 0.0,
                                'reviews': [],
                                'type': type
        })
    
    return redirect(url_for('get_add_item'))

@app.route('/delete-user', methods=['GET'])
def get_delete_user():
    # if user is not logged in redirect to home page
    if 'user' not in session and ('is_admin' not in session or session['is_admin'] == False):
        flash("Please login to delete user, only admin can delete user")
        return redirect('/login')
    
    if get_flashed_messages():
        return render_template('delete_user.html', users=Users.find(), error=get_flashed_messages()[0])

    users = Users.find()
    return render_template('delete_user.html', users=users)


@app.route('/delete-user', methods=['POST'])
def post_delete_user():
    # if user is not logged in redirect to home page
    if 'user' not in session and ('is_admin' not in session or session['is_admin'] == False):
        flash("Please login to delete user, only admin can delete user")
        return redirect('/login')

    # If user tries to delete themselves, redirect to delete user page
    if 'user' in session:
        # Do not delete the current user
        if session['user'] == request.form['username']:
            flash("You cannot delete yourself")
            return redirect('/delete-user')

    # get username from form
    username = request.form['username']

    # Get user
    user = Users.find_one({'username': username})

    # Get all reviews of user
    reviews = user['reviews']

    # Delete all reviews inside products
    for review in reviews:
        product_id = review['product_id']

        # Delete review
        Products.update_one({'_id': ObjectId(product_id)}, {'$pull': {'reviews': {'user_id': user['_id']}}})

    
    # Calculate new average rating for products
    for product in Products.find():
        product_reviews = product['reviews']
        new_rating = calculate_product_rating(product_reviews)

        # Update product rating
        Products.update_one({'_id': product['_id']}, {'$set': {'rating': new_rating}})


    # Delete user from database
    Users.delete_one({'username': username})

    # get all users to render page
    users = Users.find()

    return redirect(url_for('get_delete_user', users=users))



@app.route('/delete-item', methods=['GET'])
def get_delete_item():
    # if user is not logged in redirect to home page
    if 'user' not in session and ('is_admin' not in session or session['is_admin'] == False):
        flash("Please login to delete item, only admin can delete item")
        return redirect('/login')

    items = Products.find()
    print("Admin page DELETE ITEM GET request")
    return render_template('delete_item.html', items=items)


@app.route('/delete-item', methods=['POST'])
def post_delete_item():
    # if user is not logged in redirect to home page
    if 'user' not in session and ('is_admin' not in session or session['is_admin'] == False):
        flash("Please login to delete item, only admin can delete item")
        return redirect('/login')

    # get item name from form
    item = request.form['name']

    # Get product
    product = Products.find_one({'name': item})

    # Get all reviews of the product
    reviews_of_the_product = product['reviews']

    # Delete reviews inside user database
    for review in reviews_of_the_product:
        user_id = review['user_id']

        # Delete review from user database that matches with product id
        Users.update_one({'_id': ObjectId(user_id)}, {'$pull': {'reviews': {'product_id': product['_id']}}})

    # Calculate user average rating
    for user in Users.find():
        user_reviews = user['reviews']
        new_rating = calculate_user_rating(user_reviews)

        # Update user average rating
        Users.update_one({'_id': user['_id']}, {'$set': {'average_rating': new_rating}})


    # Delete item from database
    Products.delete_one({'name': item})

    # get all items to render page
    products = Products.find()

    return redirect(url_for('get_delete_item', products=products))