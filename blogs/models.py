from django.db import models
from django.contrib.auth.models import AbstractUser, User

# from datetime import datetime
from django.utils.timezone import now


class UserProfile(AbstractUser):
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    avatar = models.ImageField(
        default="/profile_pics/default_avatar.png", upload_to="profile_pics"
    )


class Category(models.Model):
    category = models.CharField(max_length=255, db_index=True)

    def __str__(self):
        return self.category


class Blog(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    title = models.CharField(max_length=255)
    content = models.TextField()
    date = models.DateTimeField(blank=True, default=now)

    def __str__(self):
        return self.title


class Comment(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    comment = models.TextField()
    date = models.DateTimeField(blank=True, default=now)

    def __str__(self):
        return f"For blog '{self.blog}' comment: '{self.comment}' "


class Visit(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    visit = models.DateTimeField(blank=True, default=now)


class SavedBlog(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)

    def __str__(self):
        return self.blog


class Draft(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    category = models.ForeignKey(
        Category, blank=True, null=True, on_delete=models.PROTECT
    )
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True)
