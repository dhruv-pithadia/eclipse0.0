from flask_mysqldb import MySQL
from flask import Flask

def init_db(app):
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = 'dhruv1104'
    app.config['MYSQL_DB'] = 'eclipse-latest'
    return MySQL(app)