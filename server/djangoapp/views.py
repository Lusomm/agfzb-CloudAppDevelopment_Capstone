from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
# from .restapis import related methods
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json
from .restapis import get_dealers_from_cf
from .restapis import get_dealers_by_state_from_cf
from .restapis import get_dealer_reviews_from_cf
from django.db import models
from django.core import serializers
from django.utils.timezone import now
import uuid
import json
from django.views.decorators.csrf import csrf_exempt

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


def get_about(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/about.html', context)


def get_contact(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/contact.html', context)

@csrf_exempt
def login_request(request):
    context = {}
    # Handles POST request
    if request.method == "POST":
        # Get username and password from request.POST dictionary
        username = request.POST['username']
        password = request.POST['psw']
        # Try to check if provide credential can be authenticated
        user = authenticate(username=username, password=password)
        if user is not None:
            # If user is valid, call login method to login current user
            login(request, user)
            return redirect('djangoapp:index')
        else:
            # If not, return to login page again
            return render(request, 'djangoapp:index', context)
    else:
        return render(request, 'djangoapp:index', context)
    
    
# Create a `logout_request` view to handle sign out request
def logout_request(request):
    # Get the user object based on session id in request
    print("Log out the user `{}`".format(request.user.username))
    # Logout user in the request
    logout(request)
    # Redirect user back to course list view
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_index(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/index.html', context)

def registration_request(request):
    context = {}
    # If it is a GET request, just render the registration page
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    # If it is a POST request
    elif request.method == 'POST':
        # Get user information from request.POST
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            # Check if user already exists
            User.objects.get(username=username)
            user_exist = True
        except:
            # If not, simply log this is a new user
            logger.debug("{} is new user".format(username))
        # If it is a new user
        if not user_exist:
            # Create user in auth_user table
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            # Login the user and redirect to course list page
            login(request, user)
            return redirect("djangoapp:index")
        else:
            return render(request, 'djangoapp/registration.html', context)

# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):
# ...
def get_dealerships(request):
    if request.method == "GET":
        url = "https://eu-de.functions.appdomain.cloud/api/v1/web/bf2b9022-af47-4dff-9073-a5bce06a94fe/dealership-package/get-dealership"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        # Concat all dealer's short name
        dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        # Return a list of dealer short name
        return HttpResponse(dealer_names)

def get_dealer_details(request, dealer_id):
    if request.method == "GET":
        url = "https://eu-de.functions.appdomain.cloud/api/v1/web/bf2b9022-af47-4dff-9073-a5bce06a94fe/dealership-package/get-review"
        # Get dealers from the URL
        reviews = get_dealer_reviews_from_cf(url, dealer_id)
        # Concat all dealer's short name
        dealer_reviews = '    '.join([review.review for review in reviews])
        # Return a list of dealer short name
        return HttpResponse(dealer_reviews)

def add_review(request, dealer_id):
    url = "https://eu-de.functions.appdomain.cloud/api/v1/web/bf2b9022-af47-4dff-9073-a5bce06a94fe/dealership-package/post-review"
    if request.user.is_authenticated:
        review = dict()
        review["id"] = request.id
        review["name"] = request.name
        review["dealership"] = request.dealership
        review["review"] = request.review
        review["purchase"] = request.purchase
        review["purchase_date"] = request.purchase_date
        review["car_make"] = request.car_make
        review["car_model"] = request.car_model
        review["car_year"] = request.car_year
        json_payload = dict()
        json_payload["review"] = review
        response = post_request(url, json_payload, dealer_id)
        return HttpResponse(response)
        
        


# Create a `add_review` view to submit a review
# def add_review(request, dealer_id):
# ...

