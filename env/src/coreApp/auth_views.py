from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from .models import Profile

## Views related to user authentication

## Render the signup page for GET requests and process user sign up for POST requests.
#   On submission of sign up form, create a new user, log them in and create a profile object
#   Args:
#   - request: A request object that contains metadata about the current request
#   Returns:
#   - If the request method is GET, return a render object that renders the 'signup.html' template.
#   - If the request method is POST and the form is valid, return a redirect object to the settings page.
#   - If the request method is POST and the form is invalid, return a redirect object to the signup page.
##
def signup(request):
    if request.method == "POST":
        # Get form data from request object
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        password2 = request.POST["password2"]

        # Check if passwords match
        if password == password2:
            # Check if username or email is taken
            if User.objects.filter(username=username).exists():
                # Display error message if username is taken
                messages.info(request, "Username taken")
                return redirect("signup")
            elif User.objects.filter(email=email).exists():
                # Display error message if email is taken
                messages.info(request, "Email taken")
                return redirect("signup")
            else:
                # Create new user
                user = User.objects.create_user(
                    username=username, email=email, password=password
                )
                user.save()

                # Log user in and redirect to settings
                user = auth.authenticate(username=username, password=password)
                auth.login(request, user)

                # Create profile object for the user
                user_model = User.objects.get(username=username)
                new_profile = Profile(user=user_model, id_user=user_model.id)
                new_profile.save()
                return redirect("settings")
        else:
            # Display error message if passwords don't match
            messages.info(request, "Password not matching")
            return redirect("signup")

    else:
        # Return the signup page for GET requests
        return render(request, "signup.html")


## Authenticate user login credentials and redirect to home page
#   if the login is successful. If the request method is GET, the function
#   renders the 'signin.html' template.
#   Args:
#   - request: A request object that contains metadata about the current request
#   Returns:
#   - A render object that renders the 'signin.html' template if the request method is GET.
#   If the request method is POST, the function attempts to authenticate the user's login 
#   credentials and redirects to the home page if the authentication is successful.
##
def signin(request):
    if request.method == "POST":
        # Retrieve login credentials from the POST request
        username = request.POST["username"]
        password = request.POST["password"]

        # Authenticate the user's credentials
        user = auth.authenticate(username=username, password=password)

        # Redirect to home page if authentication is successful, otherwise display error message
        if user is not None:
            auth.login(request, user)
            return redirect("index")
        else:
            messages.info(request, "Invalid credentials")
            return redirect("signin")

    else:
        # Render signin page if request method is GET
        return render(request, "signin.html")


## Log out the current user.
#   Args:
#   - request: A request object that contains metadata about the current request
#   Returns:
#   - A redirect object that redirects the user to the signin page.
##
def signout(request):
    # Logout user
    auth.logout(request)

    # Redirect to signin page
    return redirect("signin")
