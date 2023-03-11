from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Profile, Post, LikePost, FollowersCount
from itertools import chain
import random


## Display home page for authenticated users.
#   Provide the posts of users that the current user is following and
#   also suggest new users to follow. If the current user is staff, the function redirects to
#   the admin page.
#   Args:
#   - request: A request object that contains metadata about the current request
#   Returns:
#   - A render object that renders the 'index.html' template with the user_profile, posts,
#   and suggestions_username_profile_list as context data.
##
@login_required(login_url="signin")
def index(request):
    # Redirect to admin page for staff users
    if request.user.is_staff:
        return redirect("admin:index")

    # Get current user profile
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    # Get users that the current user is following
    user_following_list = []
    user_following = FollowersCount.objects.filter(follower=request.user.username)

    for users in user_following:
        user_following_list.append(users.user)

    # Get posts of users that the current user is following
    feed = []
    for usernames in user_following_list:
        feed_lists = Post.objects.filter(user=usernames)
        feed.append(feed_lists)

    feed_list = list(chain(*feed))

    # Get suggestions for new users to follow
    all_users = User.objects.all()
    user_following_all = []

    # Exclude users already followed by the current user
    for user in user_following:
        user_list = User.objects.get(username=user.user)
        user_following_all.append(user_list)

    new_suggestions_list = [
        x for x in list(all_users) if (x not in list(user_following_all))
    ]
    current_user = User.objects.filter(username=request.user.username)
    final_suggestions_list = [
        x for x in list(new_suggestions_list) if (x not in list(current_user))
    ]
    random.shuffle(final_suggestions_list)

    # Get profiles of suggested users
    username_profile = []
    username_profile_list = []

    for users in final_suggestions_list:
        username_profile.append(users.id)

    for ids in username_profile:
        profile_lists = Profile.objects.filter(id_user=ids)
        username_profile_list.append(profile_lists)

    suggestions_username_profile_list = list(chain(*username_profile_list))

    # Return the index page with user_profile, feed_list and suggested users data
    return render(
        request,
        "index.html",
        {
            "user_profile": user_profile,
            "posts": feed_list,
            "suggestions_username_profile_list": suggestions_username_profile_list[:3],
        },
    )


## Display settings page for authenticated users and update profile information.
#   If the current user is staff, the function redirects to the admin page.
#   Args:
#   - request: A request object that contains metadata about the current request
#   Returns:
#   - A render object that renders the 'settings.html' template with the user_profile as context data.
#   - If request method is POST, it updates user profile information and redirects to the settings page.
##
@login_required(login_url="signin")
def settings(request):
    # Redirect to admin page for staff users
    if request.user.is_staff:
        return redirect("admin:index")

    # Get current user profile
    user_profile = Profile.objects.get(user=request.user)

    if request.method == "POST":

        # If image is not uploaded, use the previous profile image
        if request.FILES.get("image") == None:
            image = user_profile.profileimg
            bio = request.POST["bio"]
            location = request.POST["location"]

            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()

        # If image is uploaded, use the new profile image
        if request.FILES.get("image") != None:
            image = request.FILES.get("image")
            bio = request.POST["bio"]
            location = request.POST["location"]

            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()

        return redirect("settings")

    return render(request, "settings.html", {"user_profile": user_profile})


## Upload image and caption as a new post to the website.
#   Args:
#   - request: A request object that contains metadata about the current request
#   Returns:
#   - A redirect object to the home page of the website
##
@login_required(login_url="signin")
def upload(request):
    if request.method == "POST":
        image = request.FILES.get("image_upload")
        caption = request.POST["caption"]
        user = request.user.username

        # Check if user is authenticated and if image and caption are not empty
        if not user or (not image and not caption):
            return redirect("/")

        # Create new post and save it
        new_post = Post.objects.create(user=user, image=image, caption=caption)
        new_post.save()

        return redirect("/")
    else:
        return redirect("/")


## Toggle like status of a post for the current user.
#   Add a like to the post if it wasn't liked yet, otherwise remove the like.
#   Args:
#   - request: A request object that contains metadata about the current request
#   Returns:
#   - A redirect object to the home page of the website
##
@login_required(login_url="signin")
def like_post(request):
    if request.method == "GET":
        username = request.user.username
        post_id = request.GET.get("post_id")

        post = Post.objects.get(id=post_id)
        like_filter = LikePost.objects.filter(
            post_id=post_id, username=username
        ).first()

        # If the user has not liked the post yet, add new LikePost object and increase the number of likes
        if like_filter == None:
            new_like = LikePost.objects.create(post_id=post_id, username=username)
            new_like.save()
            post.no_of_likes += 1
            post.save()

        # If the user has already liked the post, delete LikePost object and decrease the number of likes
        else:
            like_filter.delete()
            post.no_of_likes -= 1
            post.save()

        return redirect("/")

    else:
        return redirect("/")


## Display profile page for the user.
#   Display user's profile with their posts, followers and following count.
#   Args:
#   - request: A request object that contains metadata about the current request.
#   - pk: The username of the user whose profile page is to be displayed.
#   Returns:
#   - A render object that renders the 'profile.html' template with user's profile details and
#   posts as context data.
##
@login_required(login_url="signin")
def profile(request, pk):
    # Redirect to admin page for staff users
    if request.user.is_staff:
        return redirect("admin:index")

    # Get user's profile and posts
    user_object = User.objects.get(username=pk)
    user_profile = Profile.objects.get(user=user_object)
    user_posts = Post.objects.filter(user=pk)
    user_posts_length = len(user_posts)

    # Check if visitor already follows user
    follower = request.user.username
    visitor_object = User.objects.get(username=request.user.username)
    visitor_profile = Profile.objects.get(user=visitor_object)
    user = pk

    if FollowersCount.objects.filter(follower=follower, user=user).exists():
        follow_status = True
    else:
        follow_status = False

    # Get followers and following count
    user_followers = len(FollowersCount.objects.filter(user=pk))
    user_following = len(FollowersCount.objects.filter(follower=pk))

    # Return the profile page with user profile data and posts
    context = {
        "user_profile": user_profile,
        "user_object": user_object,
        "user_posts": user_posts,
        "user_posts_length": user_posts_length,
        "follow_status": follow_status,
        "user_followers": user_followers,
        "user_following": user_following,
        "visitor_profile": visitor_profile,
    }
    return render(request, "profile.html", context)


## Handle follow and unfollow requests for authenticated users.
#   Args:
#   - request: A request object that contains metadata about the current request.
#   Returns:
#   - A redirect object that redirects the user to the profile page of the user being followed or unfollowed.
##
@login_required(login_url="signin")
def follow(request):
    # Redirect to admin page for staff users
    if request.user.is_staff:
        return redirect("admin:index")

    if request.method == "POST":
        follower = request.POST["follower"]
        user = request.POST["user"]

        if FollowersCount.objects.filter(follower=follower, user=user).exists():
            delete_follow = FollowersCount.objects.filter(
                follower=follower, user=user
            ).first()
            delete_follow.delete()
            return redirect("/profile/" + user)

        else:
            new_follow = FollowersCount.objects.create(follower=follower, user=user)
            new_follow.save()
            return redirect("/profile/" + user)
    else:
        return redirect("/")


## Render the search page with a list of profiles containing the value entered by the user.
#   Args:
#   - request: A request object that contains metadata about the current request
#   Returns:
#   - A render object that renders the 'search.html' template with the user_profile and
#   username_profile_list as context data.
##
@login_required(login_url="signin")
def search(request):
    # Redirect to admin page for staff users
    if request.user.is_staff:
        return redirect("admin:index")

    # Get user profile
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    # Get profiles containing the username entered by the user
    username_object = User.objects.filter(username__icontains=username)
    username_profile = []
    username_profile_list = []

    for users in username_object:
        username_profile.append(users.id)

    for ids in username_profile:
        profile_lists = Profile.objects.filter(id_user=ids)
        username_profile_list.append(profile_lists)

    username_profile_list = list(chain(*username_profile_list))

    # Return the search page with username_profile_list data
    return render(
        request,
        "search.html",
        {"user_profile": user_profile, "username_profile_list": username_profile_list},
    )


## Render the friends page with the list of friends of the current user.
#   Args:
#   - request: A request object that contains metadata about the current request
#   Returns:
#   - Object with the 'friends.html' template with the friends_list, user_object,
#   and visitor_profile as context data.
##
@login_required(login_url="signin")
def friends(request):
    # Redirect to admin page for staff users
    if request.user.is_staff:
        return redirect("admin:index")

    # Get user profile and list of friends
    user_object = User.objects.get(username=request.user.username)
    friends = FollowersCount.objects.filter(follower=user_object.username)
    friends_list = []
    username_profile_list = []
    visitor_object = User.objects.get(username=request.user.username)
    visitor_profile = Profile.objects.get(user=visitor_object)

    # Get profiles for each friend in friends_list
    for friend in friends:
        friends_list.append(friend.user)

    for ids in friends_list:
        user = User.objects.get(username=ids)
        profile_lists = Profile.objects.get(user=user.id)
        username_profile_list.append(profile_lists)

    # Return the friends page with friends_list data
    return render(
        request,
        "friends.html",
        {
            "friends_list": username_profile_list,
            "user_object": user_object,
            "visitor_profile": visitor_profile,
        },
    )


## Unfollow a user
#   Args:
#   - request: A request object that contains metadata about the current request
#   - pk: The primary key of the user to unfollow
#   Returns:
#   - A redirect object that redirects to the friends page.
##
@login_required(login_url="signin")
def unfollow(request, pk):
    if request.user.is_staff:
        return redirect("admin:index")

    if request.method == "POST":
        follower = request.user.username
        user = pk

        if FollowersCount.objects.filter(follower=follower, user=user).exists():
            delete_follow = FollowersCount.objects.filter(
                follower=follower, user=user
            ).first()
            delete_follow.delete()
            return redirect("/friends")
    else:
        return redirect("/")


## Display the chat index page
#   Args:
#   - request: A request object that contains metadata about the current request
#   Returns:
#   - A render object that renders the 'chat/index.html' template with the visitor_profile as context data.
##
@login_required(login_url="signin")
def chat(request):
    if request.user.is_staff:
        return redirect("admin:index")

    visitor_object = User.objects.get(username=request.user.username)
    visitor_profile = Profile.objects.get(user=visitor_object)

    return render(request, "chat/index.html", {"visitor_profile": visitor_profile})


## Display the chat room page
#   Args:
#   - request: A request object that contains metadata about the current request
#   - room_name: The name of the chat room to join
#   Returns:
#   - A render object that renders the 'chat/room.html' template with the room_name, user, and visitor_profile as context data.
##
@login_required(login_url="signin")
def room(request, room_name):
    if request.user.is_staff:
        return redirect("admin:index")

    visitor_object = User.objects.get(username=request.user.username)
    visitor_profile = Profile.objects.get(user=visitor_object)

    return render(
        request,
        "chat/room.html",
        {
            "room_name": room_name,
            "user": request.user.username,
            "visitor_profile": visitor_profile,
        },
    )
