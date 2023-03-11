from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from django.contrib.auth.models import User
from coreApp.models import Post, Profile, LikePost, FollowersCount
from coreApp.serializers import PostSerializer, ProfileSerializer


## Tests for API views

class TestAllPostsListAPI(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', email='testuser@example.com', password='testpass'
        )
        self.staff_user = User.objects.create_user(
            username='teststaff', email='teststaff@example.com', password='testpass', is_staff=True
        )
        self.post = Post.objects.create(
            user=self.user.username,
            caption='Test post',
            image=None,
            no_of_likes=0,
        )

    def test_all_posts_list_api_for_staff_user(self):
        self.client.force_login(self.staff_user)
        response = self.client.get(reverse('all_posts_list_api'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_all_posts_list_api_for_non_staff_user(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('all_posts_list_api'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class UserPostsAPITest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        self.post = Post.objects.create(
            user=self.user,
            caption='Test post'
        )

    def test_user_posts_api_for_owner(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('user_posts_api', kwargs={'user': 'testuser'}))
        posts = Post.objects.filter(user=self.user)
        serializer = PostSerializer(posts, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_posts_api_for_staff_user(self):
        self.user.is_staff = True
        self.user.save()
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('user_posts_api', kwargs={'user': 'testuser'}))
        posts = Post.objects.filter(user=self.user)
        serializer = PostSerializer(posts, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_posts_api_for_non_owner_non_staff_user(self):
        User.objects.create_user(
            username='nonowneruser',
            password='testpass'
        )
        self.client.login(username='nonowneruser', password='testpass')
        response = self.client.get(reverse('user_posts_api', kwargs={'user': 'testuser'}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class TestPostDetailAPI(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.post = Post.objects.create(
            user=self.user,
            caption='Test post',
            image=None,
            no_of_likes=0
        )

    def test_post_detail_api_for_post_owner(self):
        self.client.login(username='testuser', password='testpass')
        url = reverse('post_detail_api', args=[self.post.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = {"post": PostSerializer(self.post).data}
        self.assertEqual(response.json(), expected_data)

    def test_post_detail_api_for_admin(self):
        admin_user = User.objects.create_superuser(
            username='adminuser',
            email='admin@test.com',
            password='adminpass'
        )
        self.client.login(username='adminuser', password='adminpass')
        url = reverse('post_detail_api', args=[self.post.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = {"post": PostSerializer(self.post).data}
        self.assertEqual(response.json(), expected_data)

    def test_post_detail_api_for_non_post_owner_non_admin(self):
        non_admin_user = User.objects.create_user(username='nonadminuser', password='nonadminpass')
        self.client.login(username='nonadminuser', password='nonadminpass')
        url = reverse('post_detail_api', args=[self.post.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class TestProfileDetailAPI(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.profile = Profile.objects.create(
            user=self.user,
            bio='Test bio',
            location='Test location',
             id_user=1,
        )

    def test_profile_detail_api_for_profile_owner(self):
        self.client.login(username='testuser', password='testpass')
        url = reverse('profile_detail_api', args=[self.user.username])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = {"profile": ProfileSerializer(self.profile).data}
        self.assertEqual(response.json(), expected_data)

    def test_profile_detail_api_for_admin(self):
        admin_user = User.objects.create_superuser(
            username='adminuser',
            email='admin@test.com',
            password='adminpass',
        )
        self.client.login(username='adminuser', password='adminpass')
        url = reverse('profile_detail_api', args=[self.user.username])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = {"profile": ProfileSerializer(self.profile).data}
        self.assertEqual(response.json(), expected_data)

class TestAllProfilesListAPI(APITestCase):
    def setUp(self):
        self.url = reverse("all_profiles_list_api")
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass"
        )
        self.profile = Profile.objects.create(
            user=self.user,
            bio="Test bio",
            location="Test location",
            id_user=1,
        )
        admin_user = User.objects.create_superuser(
            username='adminuser',
            email='admin@test.com',
            password='adminpass'
        )

    def test_all_profiles_list_api_for_staff_user(self):
        # log in as staff user
        self.client.login(username="adminuser", password="adminpass")

        # make request to API endpoint
        response = self.client.get(self.url)

        # verify response
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_all_profiles_list_api_for_non_staff_user(self):
        # log in as non-staff user
        self.client.login(username="testuser", password="testpass")

        # make request to API endpoint
        response = self.client.get(self.url)

        # verify response
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class AuthenticationViewsTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.signup_url = reverse('signup')
        self.signin_url = reverse('signin')
        self.signout_url = reverse('signout')
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpass'
        )

    def test_signup_view(self):
        # Test GET request to signup view
        response = self.client.get(self.signup_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'signup.html')

        # Test valid POST request to signup view
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass',
            'password2': 'newpass'
        }
        response = self.client.post(self.signup_url, data)
        self.assertRedirects(response, reverse('settings'))

        # Test POST request with invalid password confirmation (should redirect to signup again
        data['password2'] = 'notmatching'
        response = self.client.post(self.signup_url, data)
        self.assertRedirects(response, self.signup_url)

        # Test POST request with existing username (should redirect to signup again)
        data['username'] = 'testuser'
        response = self.client.post(self.signup_url, data)
        self.assertRedirects(response, self.signup_url)

        # Test POST request with existing email (should redirect to signup again
        data['username'] = 'newuser'
        data['email'] = 'testuser@example.com'
        response = self.client.post(self.signup_url, data)
        self.assertRedirects(response, self.signup_url)

    def test_signin_view(self):
        # Test GET request to signin view
        response = self.client.get(self.signin_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'signin.html')

        # Test POST request with valid credentials
        data = {
            'username': 'testuser',
            'password': 'testpass'
        }

        # Test POST request with invalid credentials
        data['password'] = 'invalid'
        response = self.client.post(self.signin_url, data)
        self.assertRedirects(response, self.signin_url)

    def test_signout_view(self):
        # Log in user before testing signout
        self.client.login(username='testuser', password='testpass')

        # Test GET request to signout view
        response = self.client.get(self.signout_url)
        self.assertRedirects(response, self.signin_url)

class TestIndexView(TestCase):

    def setUp(self):
        self.username = "testuser"
        self.email = "testuser@test.com"
        self.password = "testpass123"

        self.user = User.objects.create_user(username=self.username, email=self.email, password=self.password)
        self.profile = Profile.objects.create(user=self.user, id_user=self.user.id)

        self.url = reverse("index")
        self.feed = []

    def test_index_view_unauthenticated(self):
        response = self.client.get(self.url)
        # It should redirect to the login page
        self.assertEqual(response.status_code, 302)

    def test_index_view_authenticated(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(self.url)
        # It shouldn't redirect, should show the index page
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")

    def test_index_view_feed(self):
        self.client.login(username=self.username, password=self.password)
        for i in range(5):
            Post.objects.create(user=self.user.username, caption=f"Test post {i+1}")
        response = self.client.get(self.url)
        # Regardless of the number of posts, the feed should show no user's posts
        self.assertEqual(len(response.context["posts"]), 0)
        for post in response.context["posts"]:
            self.assertEqual(post.user, self.username)


class SettingsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", email="testuser@example.com", password="testpass",
        )
        self.profile = Profile.objects.create(user=self.user, id_user=self.user.id,  user_id=1)

    def test_settings_page_authenticated_user(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(reverse("settings"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "settings.html")
        self.assertEqual(response.context["user_profile"], self.profile)

    def test_settings_update_authenticated_user(self):
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

class ViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', email='testuser@example.com', password='testpass'
        )
        self.user_profile = Profile.objects.create(user=self.user, id_user=self.user.id,  user_id=1)

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
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(reverse("profile", args=[self.user.username]))
        print('######################################')
        print(response)
        self.assertTemplateUsed(response, "profile.html")
        self.assertEqual(response.context["user_profile"], self.user_profile)
        self.assertEqual(response.context["user_object"], self.user)
        self.assertEqual(response.context["user_posts_length"], 1)
        self.assertFalse(response.context["follow_status"]) # User should not be following themselves
        self.assertEqual(response.context["user_following"], 1)
        self.assertEqual(response.context["visitor_profile"], self.user_profile)

    def test_follow_unfollow(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.post(reverse("follow"), {"follower": self.user.username, "user": "anotheruser"})
        self.assertEqual(response.status_code, 302) # Redirect after successful POST request
        response = self.client.post(reverse("unfollow", args=["anotheruser"]))
        self.assertEqual(response.status_code, 302) # Redirect after successful POST request
        self.assertFalse(FollowersCount.objects.filter(follower=self.user.username, user="anotheruser").exists())

    def test_search(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.post(reverse("search"), {"username": ""})
        self.assertEqual(response.status_code, 200 )
        self.assertTemplateUsed(response, "search.html")   
        