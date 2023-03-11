from django.contrib import admin
from .models import Profile, Post, LikePost, FollowersCount

# Register modules to show them in the admin panel

admin.site.register(Profile)
admin.site.register(Post)
admin.site.register(LikePost)
admin.site.register(FollowersCount)
