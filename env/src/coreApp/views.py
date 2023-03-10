from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Profile, Post, LikePost, FollowersCount
from .serializers import PostSerializer, ProfileSerializer
from itertools import chain
import random

# Create your views here.
@login_required(login_url='signin')
def index(request):

    if request.user.is_staff:
        return redirect('admin:index')
    # First get object and the use it to get the profile
    user_object = User.objects.get(username=request.user.username)
    print(user_object)
    user_profile = Profile.objects.get(user=user_object)

    user_following_list = []
    feed = []

    user_following = FollowersCount.objects.filter(follower=request.user.username)

    for users in user_following:
        user_following_list.append(users.user)

    for usernames in user_following_list:
        feed_lists = Post.objects.filter(user=usernames)
        feed.append(feed_lists)

    feed_list = list(chain(*feed))
    # Get all posts

    ##user suggestions
    all_users = User.objects.all()
    user_following_all = []

    for user in user_following:
        user_list = User.objects.get(username=user.user)
        user_following_all.append(user_list)

    new_suggestions_list = [x for x in list(all_users) if (x not in list(user_following_all))]
    current_user = User.objects.filter(username=request.user.username)
    final_suggestions_list = [x for x in list(new_suggestions_list) if (x not in list(current_user))]
    random.shuffle(final_suggestions_list)

    username_profile = []
    username_profile_list = []

    for users in final_suggestions_list:
        username_profile.append(users.id)
    
    for ids in username_profile:
        profile_lists = Profile.objects.filter(id_user = ids)
        username_profile_list.append(profile_lists)

    suggestions_username_profile_list = list(chain(*username_profile_list))

    return render(request, 'index.html', {'user_profile': user_profile, 'posts': feed_list, 'suggestions_username_profile_list': suggestions_username_profile_list[:4]})

def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            if User.objects.filter(username=username).exists():
                messages.info(request, 'Username taken')
                return redirect('signup')
            elif User.objects.filter(email=email).exists():
                messages.info(request, 'Email taken')
                return redirect('signup')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

            # Log user in and redirect to settings
                user = auth.authenticate(username=username, password=password)
                auth.login(request, user)

            # Create profile object for the user
                user_model = User.objects.get(username=username)
                new_profile = Profile(user=user_model, id_user=user_model.id)   
                new_profile.save()
                return redirect('settings')
        else:
            messages.info(request, 'Password not matching')
            return redirect('signup')        

    else:
        return render(request, 'signup.html')

def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('index')
        else:
            messages.info(request, 'Invalid credentials')
            return redirect('signin')

    else:
        return render(request, 'signin.html')

def signout(request):
    auth.logout(request)
    return redirect('signin')

@login_required(login_url='signin')
def settings(request):
    if request.user.is_staff:
        return redirect('admin:index')

    user_profile = Profile.objects.get(user=request.user)

    if request.method == 'POST':

        if request.FILES.get('image') == None:
            image = user_profile.profileimg
            bio = request.POST['bio']
            location = request.POST['location']

            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()
        
        if request.FILES.get('image') != None:
            image = request.FILES.get('image')
            bio = request.POST['bio']
            location = request.POST['location']

            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()
    
        return redirect('settings')

    return render(request, 'settings.html', {'user_profile': user_profile})

@login_required(login_url='signin')
def upload(request):
    if request.method == 'POST':
        image = request.FILES.get('image_upload')
        caption = request.POST['caption']
        user = request.user.username

        if not user or (not image and not caption):
            print('nada')
            return redirect('/')
        
        new_post = Post.objects.create(user=user, image=image, caption=caption)   
        new_post.save()

        return redirect('/')
    else:
        return redirect('/')

@login_required(login_url='signin')
def like_post(request):
    print('inside')
    if request.method == 'GET':
        print('2')
        username = request.user.username
        post_id = request.GET.get('post_id')

        post = Post.objects.get(id=post_id)
        print('3')
        like_filter = LikePost.objects.filter(post_id=post_id, username=username).first()
        print('the value of like_filter is: ', like_filter)

        if like_filter == None:
            print('no like')
            new_like = LikePost.objects.create(post_id=post_id, username=username)
            new_like.save()
            post.no_of_likes += 1
            post.save()
            print('saved')

        else:
            print('liked by user')
            like_filter.delete()
            post.no_of_likes -= 1
            post.save()
            print('removed')

        return redirect('/')

    else:
        return redirect('/')

@login_required(login_url='signin')
def profile(request, pk):
    if request.user.is_staff:
        return redirect('admin:index')

    user_object = User.objects.get(username=pk)
    user_profile = Profile.objects.get(user=user_object)
    user_posts = Post.objects.filter(user=pk)
    user_posts_length = len(user_posts)

    follower = request.user.username
    user = pk

    if FollowersCount.objects.filter(follower=follower, user=user).exists():
        follow_status = True
    else:
        follow_status = False

    user_followers = len(FollowersCount.objects.filter(user=pk))
    user_following = len(FollowersCount.objects.filter(follower=pk))


    context = {
        'user_profile': user_profile,
        'user_object': user_object,
        'user_posts': user_posts,
        'user_posts_length': user_posts_length,
        'follow_status': follow_status,
        'user_followers': user_followers,
        'user_following': user_following
    }
    return render(request, 'profile.html', context)

@login_required(login_url='signin')
def follow(request):
    if request.method == 'POST':
        follower = request.POST['follower']
        user = request.POST['user']
    
        if FollowersCount.objects.filter(follower=follower, user=user).exists():
            delete_follow = FollowersCount.objects.filter(follower=follower, user=user).first()
            delete_follow.delete()
            return redirect('/profile/' + user)
        
        else:
            new_follow = FollowersCount.objects.create(follower=follower, user=user)
            new_follow.save()
            return redirect('/profile/' + user)
    else:
        return redirect('/')

@login_required(login_url='signin')
def search(request):
    if request.user.is_staff:
        return redirect('admin:index')

    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    if request.method == "POST":
        username = request.POST['username']

        # contains inside? 
        username_object = User.objects.filter(username__icontains=username)

        username_profile = []
        username_profile_list = []
        for users in username_object:
            username_profile.append(users.id)
        
        for ids in username_profile:
            profile_lists = Profile.objects.filter(id_user=ids)
            username_profile_list.append(profile_lists)

        username_profile_list = list(chain(*username_profile_list))
    return render(request, 'search.html', {'user_profile': user_profile, 'username_profile_list': username_profile_list})


@login_required(login_url='signin')
def friends(request):
    if request.user.is_staff:
        return redirect('admin:index')
    ## get all the friends of the user
    user_object = User.objects.get(username=request.user.username)
    friends = FollowersCount.objects.filter(follower=user_object.username)
    friends_list = []
    username_profile_list = []

    for friend in friends:
        friends_list.append(friend.user)

    for ids in friends_list:
        user = User.objects.get(username=ids)
        profile_lists = Profile.objects.get(user=user.id)
        username_profile_list.append(profile_lists)

    print('####Friends are', username_profile_list)

    return render(request, 'friends.html', {'friends_list': username_profile_list, 'user_object' : user_object})

@login_required(login_url='signin')
def unfollow(request, pk):
    if request.method == 'POST':
        follower = request.user.username
        user =  pk

        if FollowersCount.objects.filter(follower=follower, user=user).exists():
            delete_follow = FollowersCount.objects.filter(follower=follower, user=user).first()
            delete_follow.delete()
            return redirect('/friends')
    else:
        return redirect('/')


## Logic for chat app
def chat(request):
    return render(request, 'chat/index.html')

def room(request, room_name):
    return render(request, 'chat/room.html', {
        'room_name': room_name, 'user': request.user.username
    })


### API logic for endpoints
# Only for admins
@login_required(login_url='signin')
def all_posts_list_api(request):
    if request.user.is_staff:
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return JsonResponse({'posts':serializer.data})
    else:
        return HttpResponseForbidden('You do not have permission to access this resource.')

@login_required(login_url='signin')
def user_posts_api(request, user):
    if request.user.username != user and not request.user.is_staff:
        return HttpResponseForbidden('You do not have permission to access this resource.')
    
    user_posts = Post.objects.filter(user=user)
    serializer = PostSerializer(user_posts, many=True)
    return JsonResponse({'posts': serializer.data})

@login_required(login_url='signin')
def post_detail_api(request, pk):
    post = Post.objects.get(id=pk)

    if request.user.username != post.user and not request.user.is_staff:
        return HttpResponseForbidden('You do not have permission to access this resource.')

    post = Post.objects.get(id=pk)
    serializer = PostSerializer(post, many=False)
    return JsonResponse({'post': serializer.data})

@login_required(login_url='signin')
def profile_detail_api(request, pk):
    user_object = User.objects.get(username=pk)
    profile = Profile.objects.get(user=user_object)

    if request.user.username != profile.user.username and not request.user.is_staff:
        return HttpResponseForbidden('You do not have permission to access this resource.')

    serializer = ProfileSerializer(profile, many=False)
    return JsonResponse({'profile': serializer.data})

@login_required(login_url='signin')
def all_profiles_list_api(request):
    if request.user.is_staff:
        profiles = Profile.objects.all()
        serializer = ProfileSerializer(profiles, many=True)
        return JsonResponse({'profiles':serializer.data})
    else:
        return HttpResponseForbidden('You do not have permission to access this resource.')