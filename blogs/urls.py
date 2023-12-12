from django.urls import path, include

from rest_framework_nested import routers

from .views import (
    login_view,
    logout_view,
    get_user_view,
    update_user_view,
    set_avatar_default,
    CategoryViewSet,
    BlogViewSet,
    CommentViewSet,
    VisitViewSet,
    SavedBlogViewSet,
    DraftViewSet,
)

router = routers.DefaultRouter(trailing_slash=True)
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"blogs", BlogViewSet, basename="blog")
router.register(r"visits", VisitViewSet, basename="visit")
router.register(r"savedblogs", SavedBlogViewSet, basename="savedblog")
router.register(r"drafts", DraftViewSet, basename="draft")

blog_router = routers.NestedDefaultRouter(router, r"blogs", lookup="blog")
blog_router.register(r"comments", CommentViewSet, basename="blog-comments")

urlpatterns = [
    path("login/", login_view, name="login-view"),
    path("logout/", logout_view, name="logout-view"),
    path("getuser/", get_user_view, name="get-user-view"),
    path("updateuser/", update_user_view, name="update-user-view"),
    path("deleteavatar/", set_avatar_default, name="delete-avatar"),
    path("", include(router.urls)),
    path("", include(blog_router.urls)),
]
