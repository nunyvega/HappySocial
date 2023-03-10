from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('index/', views.index, name='index'),
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('signout/', views.signout, name='signout'),
    path('settings/', views.settings, name='settings'),
    path('upload', views.upload, name='upload'),
    path('like-post', views.like_post, name='like-post'),
    path('profile/<str:pk>', views.profile, name='profile'),
    path('follow', views.follow, name='follow'),
    path('search', views.search, name='search'),
    path('friends', views.friends, name='friends'),
    path('unfollow/<str:pk>', views.unfollow, name='unfollow'),
    path('chat/', views.chat, name='chat'),
    path('chat/<str:room_name>/', views.room, name='room'),
    path('api/all-posts/',views.all_posts_list_api, name='all_posts_list_api'),
    path('api/user-posts/<str:user>',views.user_posts_api, name='user_posts_api'),
    path('api/post-detail/<str:pk>',views.post_detail_api, name='post_detail_api'),
    path('api/all-profiles/',views.all_profiles_list_api, name='all_profiles_list_api'),
    path('api/profile-detail/<str:pk>',views.profile_detail_api, name='profile_detail_api'),

]