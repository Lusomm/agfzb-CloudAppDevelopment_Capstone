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
from .models import *
from .restapis import post_request

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

def get_dealerships(request):
    context={}
    url = "https://eu-de.functions.appdomain.cloud/api/v1/web/bf2b9022-af47-4dff-9073-a5bce06a94fe/dealership-package/get-dealership"
    # Get dealers from the URL
    context["dealership_list"] = get_dealers_from_cf(url)
    return render(request, 'djangoapp/index.html', context)

def get_dealer_details(request, dealer_id):
    if request.method == "GET":
        context ={}
        url = "https://eu-de.functions.appdomain.cloud/api/v1/web/bf2b9022-af47-4dff-9073-a5bce06a94fe/dealership-package/get-review"
        # Get dealers from the URL
        context["dealer_id"] = dealer_id
        context["dealer_reviews"] = reviews = get_dealer_reviews_from_cf(url, dealer_id)
        return render(request, 'djangoapp/dealer_details.html', context)
    
def add_review_form(request, dealer_id):
    context = {}
    dealer_url = "https://eu-de.functions.appdomain.cloud/api/v1/web/bf2b9022-af47-4dff-9073-a5bce06a94fe/dealership-package/get-review"
    dealer = get_dealer_reviews_from_cf(dealer_url, dealer_id=dealer_id)
    context["dealer"] = dealer
    context["dealer_id"] = dealer_id
    if request.method == 'GET':
        cars = CarModel.objects.all()
        context["cars"] = cars
        return render(request, 'djangoapp/add_review.html', context)
        

def add_review(request, dealer_id):
    if request.user.is_authenticated:
            username = request.user.username
            print(request.POST)
            payload = dict()
            car_id = request.POST["car"]
            car = CarModel.objects.get(pk=car_id)
            payload["time"] = datetime.utcnow().isoformat()
            payload["name"] = username
            payload["dealership"] = dealer_id
            payload["id"] = dealer_id
            payload["review"] = request.POST["review"]
            payload["purchase"] = False
            if "purchasecheck" in request.POST:
                if request.POST["purchasecheck"] == 'on':
                    payload["purchase"] = True
            payload["purchase_date"] = request.POST["purchase_date"]
            payload["car_make"] = car.carMake.name
            payload["car_model"] = car.name
            payload["car_year"] = int(car.year.strftime("%Y"))
            new_payload = {}
            new_payload["review"] = payload
            review_post_url = "https://eu-de.functions.appdomain.cloud/api/v1/web/bf2b9022-af47-4dff-9073-a5bce06a94fe/dealership-package/post-review"
            post_request(review_post_url, new_payload, dealership=dealer_id)
            return redirect("djangoapp:dealer_details", dealer_id)
        
        


# Create a `add_review` view to submit a review
# def add_review(request, dealer_id):
# ...

