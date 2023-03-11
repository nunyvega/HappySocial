from django.db import models
from django.contrib.auth import get_user_model
import uuid
from datetime import datetime

User = get_user_model()

# Model for user profiles
# Each profile is associated with a specific user and has a unique identifier
# Each profile has a description(bio), location and profileimg, the profile picture
class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    id_user = models.IntegerField()
    bio = models.TextField(max_length=500, blank=True)
    profileimg = models.ImageField(
        upload_to="profile_images", default="blank-profile-picture.jpg"
    )
    location = models.CharField(max_length=80, blank=True)

    def __str__(self):
        # Return the username of the associated user
        return self.user.username


# Model for posts
# Each post has a unique identifier using uuid (Universally unique identifier)
# Each post includes the user/creator, an optional image and a caption/text.
# It automatically adds the date and saves the number of likes of the post
class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.CharField(
        max_length=100,
    )
    image = models.ImageField(upload_to="post_images")
    caption = models.TextField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    no_of_likes = models.IntegerField(default=0)

    def __str__(self):
        # Return the username of the user who created the post
        return self.user


# Model for tracking likes on posts
# It includes the username of the user who liked the post, the id of the post
# and the date of the like
class LikePost(models.Model):
    username = models.CharField(max_length=100)
    post_id = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Return the username of the user who liked the post
        return self.username


# Model for tracking followers
# It includes the username of the user who is being followed
# and the username of the user who is following
class FollowersCount(models.Model):
    user = models.CharField(max_length=100)
    follower = models.CharField(max_length=100)

    def __str__(self):
        return self.user
