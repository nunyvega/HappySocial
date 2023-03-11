from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from django.contrib.auth.models import User
from coreApp.models import Post, Profile, LikePost, FollowersCount
from coreApp.serializers import PostSerializer, ProfileSerializer
import os


# Tests for the API views that return post lists, user posts,post details, and profile details.
# It uses the client object to Check the response status codes and returned data
class TestAllPostsListAPI(TestCase):
    def setUp(self):
        print('Setting up test environment for TestAllPostsListAPI')
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", email="testuser@example.com", password="testpass"
        )
        self.staff_user = User.objects.create_user(
            username="teststaff",
            email="teststaff@example.com",
            password="testpass",
            is_staff=True,
        )
        self.post = Post.objects.create(
            user=self.user.username,
            caption="Test post",
            image=None,
            no_of_likes=0,
        )

    def test_all_posts_list_api_for_staff_user(self):
        print('Testing test_all_posts_list_api_for_staff_user')
        self.client.force_login(self.staff_user)
        response = self.client.get(reverse("all_posts_list_api"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_all_posts_list_api_for_non_staff_user(self):
        print('Testing test_all_posts_list_api_for_non_staff_user')
        self.client.force_login(self.user)
        response = self.client.get(reverse("all_posts_list_api"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


# Tests for User Posts API View responsible for returning all posts from a specific user.
# The tests ensure that the view returns the correct HTTP status codes and response data for various scenarios
class UserPostsAPITest(TestCase):
    def setUp(self):
        print('Setting up test environment for UserPostsAPITest')
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.post = Post.objects.create(user=self.user, caption="Test post")

    def test_user_posts_api_for_owner(self):
        print('Testing test_user_posts_api_for_owner')
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(
            reverse("user_posts_api", kwargs={"user": "testuser"})
        )
        posts = Post.objects.filter(user=self.user)
        serializer = PostSerializer(posts, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_posts_api_for_staff_user(self):
        print('Testing test_user_posts_api_for_staff_user')
        self.user.is_staff = True
        self.user.save()
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(
            reverse("user_posts_api", kwargs={"user": "testuser"})
        )
        posts = Post.objects.filter(user=self.user)
        serializer = PostSerializer(posts, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_posts_api_for_non_owner_non_staff_user(self):
        print('Testing test_user_posts_api_for_non_owner_non_staff_user')
        User.objects.create_user(username="nonowneruser", password="testpass")
        self.client.login(username="nonowneruser", password="testpass")
        response = self.client.get(
            reverse("user_posts_api", kwargs={"user": "testuser"})
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


# Tests for Post Detail API View which retrieves the details of a specific post,
# The tests verify that the view returns the expected data  on each scenario. APIClient is used to simulate requests to the API.
class TestPostDetailAPI(TestCase):
    def setUp(self):
        print('Setting up test environment for TestPostDetailAPI')
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.post = Post.objects.create(
            user=self.user, caption="Test post", image=None, no_of_likes=0
        )

    def test_post_detail_api_for_post_owner(self):
        print('Testing test_post_detail_api_for_post_owner')
        self.client.login(username="testuser", password="testpass")
        url = reverse("post_detail_api", args=[self.post.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = {"post": PostSerializer(self.post).data}
        self.assertEqual(response.json(), expected_data)

    def test_post_detail_api_for_admin(self):
        print('Testing test_post_detail_api_for_admin')
        admin_user = User.objects.create_superuser(
            username="adminuser", email="admin@test.com", password="adminpass"
        )
        self.client.login(username="adminuser", password="adminpass")
        url = reverse("post_detail_api", args=[self.post.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = {"post": PostSerializer(self.post).data}
        self.assertEqual(response.json(), expected_data)

    def test_post_detail_api_for_non_post_owner_non_admin(self):
        print('Testing test_post_detail_api_for_non_post_owner_non_admin')
        non_admin_user = User.objects.create_user(
            username="nonadminuser", password="nonadminpass"
        )
        self.client.login(username="nonadminuser", password="nonadminpass")
        url = reverse("post_detail_api", args=[self.post.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


# Tests for ProfileDetailAPI view  for both the profile owner and the admin user.
class TestProfileDetailAPI(TestCase):
    def setUp(self):
        print('Setting up test environment for TestProfileDetailAPI')
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.profile = Profile.objects.create(
            user=self.user,
            bio="Test bio",
            location="Test location",
            id_user=1,
        )

    def test_profile_detail_api_for_profile_owner(self):
        print('Testing test_profile_detail_api_for_profile_owner')
        self.client.login(username="testuser", password="testpass")
        url = reverse("profile_detail_api", args=[self.user.username])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = {"profile": ProfileSerializer(self.profile).data}
        self.assertEqual(response.json(), expected_data)

    def test_profile_detail_api_for_admin(self):
        print('Testing test_profile_detail_api_for_admin')
        admin_user = User.objects.create_superuser(
            username="adminuser",
            email="admin@test.com",
            password="adminpass",
        )
        self.client.login(username="adminuser", password="adminpass")
        url = reverse("profile_detail_api", args=[self.user.username])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = {"profile": ProfileSerializer(self.profile).data}
        self.assertEqual(response.json(), expected_data)


# Tests for ProfileDetailAPI view
# It sets up a test client, creates a user and a profile, and tests the API endpoints for the profile detail
class TestAllProfilesListAPI(APITestCase):
    def setUp(self):
        print('Setting up test environment for TestAllProfilesListAPI')
        self.url = reverse("all_profiles_list_api")
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.profile = Profile.objects.create(
            user=self.user,
            bio="Test bio",
            location="Test location",
            id_user=1,
        )
        admin_user = User.objects.create_superuser(
            username="adminuser", email="admin@test.com", password="adminpass"
        )

    def test_all_profiles_list_api_for_staff_user(self):
        print('Testing test_all_profiles_list_api_for_staff_user')
        # log in as staff user
        self.client.login(username="adminuser", password="adminpass")

        # make request to API endpoint
        response = self.client.get(self.url)

        # verify response
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_all_profiles_list_api_for_non_staff_user(self):
        print('Testing test_all_profiles_list_api_for_non_staff_user')
        # log in as non-staff user
        self.client.login(username="testuser", password="testpass")

        # make request to API endpoint
        response = self.client.get(self.url)

        # verify response
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


# Tests for signup signin and signout views
# It tests data validation, redirects, and template rendering
class AuthenticationViewsTestCase(TestCase):
    def setUp(self):
        print('Setting up test environment for AuthenticationViewsTestCase')
        self.client = Client()
        self.signup_url = reverse("signup")
        self.signin_url = reverse("signin")
        self.signout_url = reverse("signout")
        self.user = User.objects.create_user(
            username="testuser", email="testuser@example.com", password="testpass"
        )

    def test_signup_view(self):
        print('Testing test_signup_view')
        # Test GET request to signup view
        response = self.client.get(self.signup_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "signup.html")

        # Test valid POST request to signup view
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpass",
            "password2": "newpass",
        }
        response = self.client.post(self.signup_url, data)
        self.assertRedirects(response, reverse("settings"))

        # Test POST request with invalid password confirmation (should redirect to signup again
        data["password2"] = "notmatching"
        response = self.client.post(self.signup_url, data)
        self.assertRedirects(response, self.signup_url)

        # Test POST request with existing username (should redirect to signup again)
        data["username"] = "testuser"
        response = self.client.post(self.signup_url, data)
        self.assertRedirects(response, self.signup_url)

        # Test POST request with existing email (should redirect to signup again
        data["username"] = "newuser"
        data["email"] = "testuser@example.com"
        response = self.client.post(self.signup_url, data)
        self.assertRedirects(response, self.signup_url)

    def test_signin_view(self):
        print('Testing test_signin_view')
        # Test GET request to signin view
        response = self.client.get(self.signin_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "signin.html")

        # Test POST request with valid credentials
        data = {"username": "testuser", "password": "testpass"}

        # Test POST request with invalid credentials
        data["password"] = "invalid"
        response = self.client.post(self.signin_url, data)
        self.assertRedirects(response, self.signin_url)

    def test_signout_view(self):
        print('Testing test_signout_view')
        # Log in user before testing signout
        self.client.login(username="testuser", password="testpass")

        # Test GET request to signout view
        response = self.client.get(self.signout_url)
        self.assertRedirects(response, self.signin_url)


# Tests for the index view (home page)
# It tests the template rendering and the context data
class TestIndexView(TestCase):
    def tearDown(self):
        print('Tearing down test environment for TestIndexView')
        # Delete profile images to avoid clutter
        if os.path.isfile(self.profile.profileimg.url):
            os.remove(self.profile.profileimg.url)

        # Call super class method
        super().tearDown()

    def setUp(self):
        print('Setting up test environment for TestIndexView')
        self.username = "testuser"
        self.email = "testuser@test.com"
        self.password = "testpass123"

        self.user = User.objects.create_user(
            username=self.username, email=self.email, password=self.password
        )
        self.profile = Profile.objects.create(user=self.user, id_user=self.user.id)

        self.url = reverse("index")
        self.feed = []

    def test_index_view_unauthenticated(self):
        print('Testing test_index_view_unauthenticated')
        response = self.client.get(self.url)
        # It should redirect to the login page
        self.assertEqual(response.status_code, 302)

    def test_index_view_authenticated(self):
        print('Testing test_index_view_authenticated')
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(self.url)
        # It shouldn't redirect, should show the index page
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")

    def test_index_view_feed(self):
        print('Testing test_index_view_feed')
        self.client.login(username=self.username, password=self.password)
        for i in range(5):
            Post.objects.create(user=self.user.username, caption=f"Test post {i+1}")
        response = self.client.get(self.url)
        # Regardless of the number of posts, the feed should show no user's posts
        self.assertEqual(len(response.context["posts"]), 0)
        for post in response.context["posts"]:
            self.assertEqual(post.user, self.username)


# Tests for the settings view (settings page) and the settings form
class SettingsTestCase(TestCase):
    def tearDown(self):
        print('Tearing down test environment for SettingsTestCase')
        # Delete profile images to avoid clutter
        if os.path.isfile(self.profile.profileimg.url):
            os.remove(self.profile.profileimg.url)

        # Call super class method
        super().tearDown()

    def setUp(self):
        print('Setting up test environment for SettingsTestCase')
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpass",
        )
        self.profile = Profile.objects.create(
            user=self.user, id_user=self.user.id, user_id=1
        )

    def test_settings_page_authenticated_user(self):
        print('Testing test_settings_page_authenticated_user')
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(reverse("settings"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "settings.html")
        self.assertEqual(response.context["user_profile"], self.profile)

    def test_settings_update_authenticated_user(self):
        print('Testing test_settings_update_authenticated_user')
        self.client.login(username="testuser", password="testpass")
        with open("media/blank-profile-picture.jpg", "rb") as image:
            response = self.client.post(
                reverse("settings"),
                {"image": image, "bio": "New bio", "location": "New location"},
            )
        self.assertEqual(response.status_code, 302)
        updated_profile = Profile.objects.get(user=self.user)
        self.assertEqual(updated_profile.bio, "New bio")
        self.assertEqual(updated_profile.location, "New location")
        self.assertIsNotNone(updated_profile.profileimg)


# Tests for the profile view (profile page), follow/unfollow and search
class ViewsTestCase(TestCase):
    def setUp(self):
        print('Setting up test environment for ViewsTestCase')
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", email="testuser@example.com", password="testpass"
        )
        self.user_profile = Profile.objects.create(
            user=self.user, id_user=self.user.id, user_id=1
        )

        self.post = Post.objects.create(
            user=self.user.username,
            caption="Test caption",
            image="test.jpg",
            no_of_likes=0,
        )

        self.followers_count = FollowersCount.objects.create(
            follower=self.user.username,
            user="otheruser",
        )

    def test_profile(self):
        print('Testing test_profile')
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(reverse("profile", args=[self.user.username]))
        self.assertTemplateUsed(response, "profile.html")
        self.assertEqual(response.context["user_profile"], self.user_profile)
        self.assertEqual(response.context["user_object"], self.user)
        self.assertEqual(response.context["user_posts_length"], 1)
        self.assertFalse(
            response.context["follow_status"]
        )  # User should not be following themselves
        self.assertEqual(response.context["user_following"], 1)
        self.assertEqual(response.context["visitor_profile"], self.user_profile)

    def test_follow_unfollow(self):
        print('Testing test_follow_unfollow')
        self.client.login(username="testuser", password="testpass")
        response = self.client.post(
            reverse("follow"), {"follower": self.user.username, "user": "anotheruser"}
        )
        self.assertEqual(
            response.status_code, 302
        )  # Redirect after successful POST request
        response = self.client.post(reverse("unfollow", args=["anotheruser"]))
        self.assertEqual(
            response.status_code, 302
        )  # Redirect after successful POST request
        self.assertFalse(
            FollowersCount.objects.filter(
                follower=self.user.username, user="anotheruser"
            ).exists()
        )

    def test_search(self):
        print('Testing test_search')
        self.client.login(username="testuser", password="testpass")
        response = self.client.post(reverse("search"), {"username": ""})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "search.html")


# Tests for the chat functionality, including the chat and the room views
class ChatTestCase(TestCase):
    def setUp(self):
        print('Setting up test environment for ChatTestCase')
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.user_profile = Profile.objects.create(
            user=self.user, id_user=self.user.id, user_id=1
        )

    def test_chat(self):
        print('Testing test_chat')
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(reverse("chat"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "chat/index.html")
        self.assertEqual(
            str(response.context["visitor_profile"]), str(self.user_profile)
        )

    def test_room(self):
        print('Testing test_room')
        self.client.login(username="testuser", password="testpassword")
        room_name = "test_room"
        response = self.client.get(reverse("room", args=[room_name]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "chat/room.html")
        self.assertEqual(response.context["room_name"], room_name)
        self.assertEqual(response.context["user"], self.user.username)
        self.assertEqual(
            str(response.context["visitor_profile"]), str(self.user_profile)
        )
