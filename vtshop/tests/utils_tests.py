"""A utility module for our tests."""

from django.contrib.auth.hashers import make_password

from vtshop.models import User
from vtshop.forms import UserForm

########################
##### CREATE USERS #####
########################

def create_administrator():
    """
    Create an administrator User, without "going through app logic",
    e.g. from Django admin IF.
    """
    
    administrator = User.objects.create(
        email = "administrator@vt.com",
        password = make_password("12345678&"),
        first_name = "admin_first_name",
        last_name = "admin_last_name",
        company = "vt",
        role = "ADMINISTRATOR", 
    )

    return administrator

def create_employee1():
    """Create an employee, using app logic."""

    user_form = UserForm()
    user_form.cleaned_data = {
        "email": "employee1@vt.com",
        "password": "12345678&",
        "first_name": "emp1_first_name",
        "last_name": "emp1_last_name", 
    }

    return user_form.create_user(role="EMPLOYEE")

def create_employee2():
    """Create another employee, using app logic."""

    user_form = UserForm()
    user_form.cleaned_data = {
        "email": "employee2@vt.com",
        "password": "12345678&",
        "first_name": "emp2_first_name",
        "last_name": "emp2_last_name", 
    }

    return user_form.create_user(role="EMPLOYEE")

def create_customer1():
    """Create an customer, using app logic."""

    user_form = UserForm()
    user_form.cleaned_data = {
        "email": "customer1@test.com",
        "password": "12345678&",
        "first_name": "cust1_first_name",
        "last_name": "cust1_last_name", 
    }

    return user_form.create_user(role="CUSTOMER")

def create_customer2():
    """Create another customer, using app logic."""

    user_form = UserForm()
    user_form.cleaned_data = {
        "email": "customer2@test.com",
        "password": "12345678&",
        "first_name": "cust2_first_name",
        "last_name": "cust2_last_name", 
    }

    return user_form.create_user(role="CUSTOMER")