from flask_app import app
from flask_bcrypt import Bcrypt
from flask import render_template, redirect,request,session,flash,url_for
from flask_app.config.mysqlconnection import connectToMySQL
import re

from flask_app.models import message
from flask_app.models import chat

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
NAME_REGEX= re.compile(r'[a-zA-Z]+$') 
PASSWORD_REGEX= re.compile(r'^(?=.{8,})(?=.*[a-z])(?=.*[0-9])(?=.*[A-Z])(?=.*[@#$%^&+=]).*$')

class User:
    def __init__(self, data):
        self.id = data['id']
        self.fname = data['fname']
        self.lname = data['lname']
        self.nick = data['nick']
        self.email = data['email']
        self.picture = data['picture']
    
    @classmethod
    def get_user_by_id(cls, id):
        query = 'SELECT * FROM users WHERE id = %(id)s;'
        data = {'id': id}
        result = connectToMySQL().query_db(query, data)
        if result:
            return cls(result[0])
        else:
            return None

    @classmethod
    def check_login(cls, email, pswrd):
        query = 'SELECT users.id, users.email, logins.pwd FROM users LEFT JOIN logins ON users.id = logins.users_id WHERE email =  %(email)s;'
        data = {'email': email}
        result = connectToMySQL().query_db(query, data)
        if result and Bcrypt().check_password_hash(result[0]['pwd'], pswrd):
            return result[0]['id']
        else:
            flash(['Invalid Email/Password',1])
            return None
        
    @classmethod
    def create_login(cls, data):
        query = 'INSERT INTO logins (pwd, users_id) VALUES (%(pswrd)s, %(user_id)s);'
        return connectToMySQL().query_db(query, data)

    @classmethod
    def save(cls,data):
        query = 'INSERT INTO users (fname, lname, email,created_at) VALUES (%(fname)s, %(lname)s, %(email)s, now());'
        return connectToMySQL().query_db(query, data)
    

    @staticmethod
    def validate_entry(data):
        is_valid = True
        if len(data['fname']) <2:
            flash(['The first name should have at least 2 characters',0])
            is_valid= False
        if not NAME_REGEX.match(data['fname']):
            flash(['Your first name should not have numbers',0])
            is_valid= False
        if len(data['lname']) <2:
            flash(['The last name should have at least 2 characters',0])
            is_valid= False
        if not NAME_REGEX.match(data['lname']):
            flash(['Your last name should not have numbers',0])
            is_valid= False
        if not EMAIL_REGEX.match(data['email']): 
            flash(['Invalid email address!',0])
            is_valid = False
        if len(data['pswrd']) <8:
            flash(['The password should have at least 8 characters',0])
            is_valid = False
        if data['pswrd_confirm'] !=data['pswrd']:
            flash(['The password confirmation is not matching with the original password',0])
            is_valid= False
        if not PASSWORD_REGEX.match(data['pswrd']):
            flash(['Your password should have at least 8 characters with at least one lowercase and one uppercase ASCII character and also at least one character from the set @#$%^&+=, plus a number',0])
            is_valid= False
        return is_valid

    @classmethod
    def getbyemail(cls, data):
        query = 'select * from users where email = %(email)s;'
        mysql = connectToMySQL()
        result = mysql.query_db(query, data)
        if len(result) > 0:
            return cls(result[0])
        else:
            return None