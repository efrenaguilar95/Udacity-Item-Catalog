# Item Catalog Project

This project is a web application that allows users to view a list of items within a given set of categories.
All items can be viewed by all users; however, only users that are signed in to the application (via Google Account) are allowed to add items.
Furthermore, users are only allowed to edit and delete items that they have created. 

This project was assigned to me as part of the Udacity Full Stack Nanodegree course. It showcases my ability to develop a RESTful web application using the Python framework Flask, to successfully implement and integrate third-party OAuth authentication, to sucessfully connect this web application to a back-end database with full CRUD (create, read, update and delete) operations for users, and to create a basic json API for developers who wish to access and use the publicly available data of the web application.

## Getting started
### Prerequisites
To run this project you will need:
* [Python 3](https://www.python.org/downloads/)
* [VirtualBox 5.1](https://www.virtualbox.org/wiki/Download_Old_Builds_5_1)
* [Vagrant](https://www.vagrantup.com/downloads.html)
* [Udacity-provided VM](https://s3.amazonaws.com/video.udacity-data.com/topher/2018/April/5acfbfa3_fsnd-virtual-machine/fsnd-virtual-machine.zip)

### Installing
You will first need to download **VirtualBox 5.1**. You can download it [here](https://www.virtualbox.org/wiki/Download_Old_Builds_5_1).

You will then need to install **Vagrant**. You can dowload it [here](https://www.vagrantup.com/downloads.html). (Be sure to grant it network permissions if prompted)

Unzip the [Udacity-provided VM](https://s3.amazonaws.com/video.udacity-data.com/topher/2018/April/5acfbfa3_fsnd-virtual-machine/fsnd-virtual-machine.zip) and navigate to the **vagrant** directory.

In here, create a **new directory** and place all of the provided folders and files from this project.

Go back to the **vagrant** directory, open a terminal and run the following command:
```
vagrant up
```
This will tell Vagrant to download and install the Linux OS, which my take some time.

When this is done, run the following command to connect to the VM:
```
vagrant ssh
```
Navigate to the **/vagrant** directory:
```
cd /vagrant
```
Navigate to the directory you created:
```
cd "your directory name"
```
In here run the following command to set up the database:
```
python databaseSetup.py
```
After this, run the following command to populate the database with some example data (Optional):
```
python databasePopulator.py
```
With this setup completed, try running the app!
```
python application.py
```
Once the app is running, you should be able to connect to the app at [localhost:8000](http://localhost:8000)

Note: You will need a Google account to access many of the features of this app, as well as Google OAuth2 access (your own client ID, and client secret key). Go [here](https://console.developers.google.com/) to get that set up if you do not have this already. The files to insert your client_id and client_secret are "client_secrets.json" and "templates/login.html"

## JSON Enpoint/API Info
There are 3 endpoints in this application for the retrieval of data in JSON format

* */catalog.json* Returns the entire Category/Item dataset
* *catalog/"categoryName".json* Returns the dataset for all the items in a single Category
* *catalog/"categoryName"/"itemTitle".json* Returns the dataset for a single Item


## Author
Efren Aguilar

## Acknowledgements
[Udacity](https://www.udacity.com/) for providing the virtual machine configuration and all the knowledge it took to make this!