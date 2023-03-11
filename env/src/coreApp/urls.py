from django.urls import path
from . import api_views, auth_views, views

urlpatterns = [
    ## Home URLs ##
    path("", views.index, name="index"),
    path("index/", views.index, name="index"),
    ## Authentication URLs ##
    path("signup/", auth_views.signup, name="signup"),
    path("signin/", auth_views.signin, name="signin"),
    path("signout/", auth_views.signout, name="signout"),
    ## Chat URLs ##
    path("chat/", views.chat, name="chat"),
    path("chat/<str:room_name>/", views.room, name="room"),
    ## API URLs ##
    path("api/all-posts/", api_views.all_posts_list_api, name="all_posts_list_api"),
    path("api/user-posts/<str:user>", api_views.user_posts_api, name="user_posts_api"),
    path("api/post-detail/<str:pk>", api_views.post_detail_api, name="post_detail_api"),
    path(
        "api/all-profiles/", api_views.all_profiles_list_api, name="all_profiles_list_api"
    ),
    path(
        "api/profile-detail/<str:pk>",
        api_views.profile_detail_api,
        name="profile_detail_api",
    ),
    ## Other URLs ##
    path("upload", views.upload, name="upload"),
    path("follow", views.follow, name="follow"),
    path("search", views.search, name="search"),
    path("friends", views.friends, name="friends"),
    path("settings/", views.settings, name="settings"),
    path("like-post", views.like_post, name="like-post"),
    path("profile/<str:pk>", views.profile, name="profile"),
    path("unfollow/<str:pk>", views.unfollow, name="unfollow"),
]
