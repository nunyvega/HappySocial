from rest_framework import serializers
from coreApp.models import Post, Profile

class PostSerializer(serializers.ModelSerializer):
    # Define the model (Post) and fields that will be shown in the API (all fields)
    class Meta:
        model = Post
        fields = '__all__'

class ProfileSerializer(serializers.ModelSerializer):
    # Define the model (Profile) and fields that will be shown in the API (all fields)
    class Meta:
        model = Profile
        fields = '__all__'