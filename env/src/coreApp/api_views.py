from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from .models import Profile, Post, LikePost, FollowersCount
from .serializers import PostSerializer, ProfileSerializer

### API logic for endpoints

## API view to get all posts (only accessible to admins)
# Only for admins
# Args:
# - request: A request object that contains metadata about the current request
# Returns:
# - A JsonResponse object that contains all posts in serialized form
@login_required(login_url="signin")
def all_posts_list_api(request):
    if request.user.is_staff:
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return JsonResponse({"posts": serializer.data})
    else:
        return HttpResponseForbidden(
            "You do not have permission to access this resource."
        )


## API view to get user posts (only accessible to posts owner and admins)
# Args:
# - request: A request object that contains metadata about the current request
# - user: username of the user whose posts are to be retrieved
# Returns:
# - A JsonResponse object that contains user posts in serialized form
@login_required(login_url="signin")
def user_posts_api(request, user):
    if request.user.username != user and not request.user.is_staff:
        return HttpResponseForbidden(
            "You do not have permission to access this resource."
        )

    user_posts = Post.objects.filter(user=user)
    serializer = PostSerializer(user_posts, many=True)
    return JsonResponse({"posts": serializer.data})


## API view to get post detail (only accessible to post owner and admins)
# Args:
# - request: A request object that contains metadata about the current request
# - pk: primary key of the post
# Returns:
# - A JsonResponse object that contains post detail in serialized form
@login_required(login_url="signin")
def post_detail_api(request, pk):
    post = Post.objects.get(id=pk)

    if request.user.username != post.user and not request.user.is_staff:
        return HttpResponseForbidden(
            "You do not have permission to access this resource."
        )

    post = Post.objects.get(id=pk)
    serializer = PostSerializer(post, many=False)
    return JsonResponse({"post": serializer.data})


## API view to get the data of a profile (only accessible to profile owner and admins)
# Args:
# - request: A request object that contains metadata about the current request
# - pk: primary key of the post
# Returns:
# - A JsonResponse object that contains profile info in serialized form
@login_required(login_url="signin")
def profile_detail_api(request, pk):
    user_object = User.objects.get(username=pk)
    profile = Profile.objects.get(user=user_object)

    # Check if the current user is authorized to access the resource
    # It should be the user whose profile is being accessed or an admin
    if request.user.username != profile.user.username and not request.user.is_staff:
        return HttpResponseForbidden(
            "You do not have permission to access this resource."
        )

    serializer = ProfileSerializer(profile, many=False)
    return JsonResponse({"profile": serializer.data})


## API view to get all profiles (only accessible to admins)
# Args:
# - request: A request object that contains metadata about the current request
# Returns:
# - A JsonResponse object that contains all profiles in serialized form
@login_required(login_url="signin")
def all_profiles_list_api(request):
    if request.user.is_staff:
        profiles = Profile.objects.all()
        serializer = ProfileSerializer(profiles, many=True)
        return JsonResponse({"profiles": serializer.data})
    else:
        return HttpResponseForbidden(
            "You do not have permission to access this resource."
        )
