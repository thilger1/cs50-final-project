# Pottery Store Flask Application
#### Video Demo: https://www.youtube.com/watch?v=HiLwbyjL4SY&ab_channel=TedHilger

### Description

#### Introduction
Pottery Store Flask Application allows users to shop for pottery and studio merchandise. Users can view information about the pottery studio, register/log-in, add items to their shopping cart, checkout, and view their order history. There is also seperate functionality for an adminstrative user with certain log-in credentials, which enables the admin to add or remove items to the store and view information on users' orders. 

#### How It's Made
This project was made using Flask (Python, HTML5/CSS , and SQL). A log-in and session module enable much of the functionality, including shopping cart, order history, and admin control. 

#### Usage
The About page shows studio information for Togei Kyoshitsu, the pottery studio for which this application was created. Upon clicking the shop option along the navigation bar, the user is redirected to the store where they have the option to shop for pottery or additional studio merchandise. I believe that seperating these two categories better organizes the store for users. I had to learn how to dynamically pull product images from a static folder to display them on the store in a way that would allow new images to be added through the admin UX. This is done through a SQL table that contains the image names that correspond with the images stored in the project's static folder. Through this strategy, maniupulation of the store was made much easier because manipulating the SQL tables is simple. 
By clicking 'View', the user can see additional information on the items including a description that is pulled from a SQL product table. Adding to cart stores the information in the session variable. Checking out stores the items from the user's cart in a SQL purchased table using a for-loop for each item within the cart session. Checking out also removes the items from the store in order to prevent multiple purchases of the same item, and is reflected within the SQL product table. I had to strategize how best to store all of the relevant information, and ultimately decided that multiple tables with different parts of the complete order information was most efficient and simple to manipulate. Specifcially, there is a basic table that creates the order number, one with the user's shipping and payment info, and one with additional details on the purchased products. These all correspond with each other by using the order number. 
On the admin side, showing a different view is possible through using the session variable to verify that the username is proper. Jinja if-statements allow different views for similar webpages. The admin is able to re-add items that were removed from the store from user-orders. The admin can also view information on the orders that were made by users, and add new items to the store. Upon adding the image and necessary information for the new item, a new SQL entry is added to the products table, and the uploaded image is added to the project's static image folder. 




