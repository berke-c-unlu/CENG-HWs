# CENG 495 Homework 1
This is the first homework of CENG 495 course. The homework is about creating a simple e-commerce website using Render as PaaS and MongoDB Atlas as DBaaS. The website is deployed on render and the database is hosted on MongoDB Atlas.

Website URL: https://e-commerce-hw1-495.onrender.com/

## Why Flask for this homework?
Flask has a very nice and easy-to-follow tutorials to create a website. It is also very easy to deploy on Render. Also, it is very easy to connect to MongoDB Atlas using Flask.
I've followed tutorials in Flask's official website to create this website.

## HTML and CSS
I've used Bootstrap for the frontend of the website. It has very detailed docs and it is easy to find everything needed. I've written some javascript code to make the website more interactive. I did not write any style sheet for the website. I've used Bootstrap's default style sheet and I've added style for some elements.

## MongoDB Atlas usage
I've created a database on MongoDB Atlas and I've created two collections in it. One for the products and one for the users. I've used MongoDB Atlas' connection string to connect to the database. I've used pymongo to connect to the database. I've used pymongo to insert, update, delete and query documents in the database.

I've stored username, password and is_admin option in the users collection. Username and password are used to authenticate user. I've authorized the user by looking is_admin option.

I've stored reviews in the products and users collection separately. There is a reviews array in users collection and and every object in the array has product_id, review and rating. There is also a reviews array in products collection and every object in the array has user_id, review and rating. I've used this structure to make it easier to query the reviews while deleting an user or a product. Also, it made easy to calculate the average rating of a product or an user.

## Render usage
Render uses requirements.txt in this repository to install requirements of flask. Render uses gunicorn to initiate the website. Pymongo and flask are needed to run the website.

## Design and Implementation of the website

### Navbar
There is a fixed navbar on the top of the website. It has a logo that redirects to the home page. If current user have not logged in before, it can only sees logo and login button in the navbar. After logging in, if user is an admin, it can see add tabs and delete tabs beside login, profile and logout buttons. If user is not an admin, it can only see login, profile and logout buttons.

### Login
If an user is registered by admin, then the user can login to the website using username and password. 

If an user does not enter username/password or enters wrong username/password, they will get an error message. If an user enters correct username/password, it will be redirected to the home page.

If an user logs in successfully, the program creates a session for the user. The sesssion stores username, user_id and is_admin option. After logging out, the session is deleted.

### Home Page
There is products in the home page. The products are listed in a grid. Each product has a picture, name, brief description, price, rating and a button to view the full details of the product. This button is used to navigate to the product page.

### Product Page
There is a product page for each product. The product page contains all spesifications of the product. There is a table that contains reviews and ratings given for the product. There is also a form to add a review for the product. The form has a text area for review and a number input for rating. The rating must be between 1 and 5. If the user has already reviewed the product, the review is updated. If the user has not reviewed the product, a new review is added.

If the user is not logged in, it cannot write a review. This attempt redirects user to the login page with an error message.

### Profile Page
There is a profile page for each user. The profile page contains username, average_rating given by this user and reviews that this user made.

### Add Product Page
There is an add product page. This page is only visible to admins. Admins can add a new product using this page. The form has a select input for the category of the product. The input fields are validated using javascript according to the category of the object. If the user skips an input, the product will not be added.

### Add User Page
There is an add user page. This page is only visible to admins. Admins can add a new user using this page. The form has username and password inputs and select input for admin privileges. If the user skips an input, the user will not be added.


### Delete Product Page

There is a delete product page. This page is only visible to admins. Admins can delete a product using this page. The page lists all products. Admins can select a product and delete it. If the product is deleted, all reviews of the product are deleted from the users collection.

### Delete User Page

There is a delete user page. This page is only visible to admins. Admins can delete a user using this page. The page lists all users. Admins can select a user and delete it. If the user is deleted, all reviews of the user are deleted from the products collection.


### Logout
When an user clicks logout button, the session is deleted and the user is redirected to the home page.



## How to use the website as regular user

### Login

Firstly, an user must login to the website using login button in the navbar.

### Writing a review

After logging in, the user can click view button in each product to view the product page. Then the user can write a review for the product.

### Viewing profile

After logging in, the user can click profile button in the navbar to view the profile page to see its reviews and average rating.

### Logout

After logging in, the user can click logout button in the navbar to logout from the website.


## How to use the website as admin

An admin can do everything that a regular user can do. In addition, an admin can add a new product, add a new user, delete a product and delete an user.

### Add Product

After logging in, the admin can click add product button in the navbar to add a new product.

### Add User

After logging in, the admin can click add user button in the navbar to add a new user.

### Delete Product

After logging in, the admin can click delete product button in the navbar to delete a product. The reviews of the product are deleted from the users collection.

### Delete User

After logging in, the admin can click delete user button in the navbar to delete a user. The reviews of the user are deleted from the products collection.



