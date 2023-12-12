from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login, logout

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework import filters

from django_filters.rest_framework import DjangoFilterBackend

# IMPORT MODELS
from .models import Category, Blog, Comment, UserProfile, Visit, SavedBlog, Draft

# IMPORT SERIALIZERS
from .serializers import (
    CategorySerializer,
    BlogSerializer,
    CommentSerializer,
    UserProfileSerializer,
    VisitSerializer,
    SavedBlogSerializer,
    DraftSerializer,
)

# CREATE CUSTOM PAGINATION CLASS
from rest_framework.pagination import PageNumberPagination


# class DefaultPagination(PageNumberPagination):
#     page_size = 6


# SESSION BASED AUTHENTICATION VIEWS - LOGIN AND LOGOUT USER
@api_view(["POST"])
def login_view(request):
    # EXTRACT USERNAME AND PASSWORD FROM THE REQUEST
    username = request.data["username"]
    password = request.data["password"]

    # IF USER DOESN'T PROVIDE HIS/HER USERNAME OR PASSWORD
    if not username:
        return Response(
            {"detail": "Please provide a username."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    if not password:
        return Response(
            {"detail": "Please provide your password."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    # AUTHENTICATE USER WITH GIVEN CREDENTIALS
    user = authenticate(username=username, password=password)

    # IF USER CANNOT BE AUTHENTICATED
    if not user:
        return Response(
            {"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED
        )

    login(request, user)
    return Response({"detail": "Successfully logged in."}, status=status.HTTP_200_OK)


@api_view(["GET"])
def logout_view(request):
    # IF UNAUTHENTICATED USERS REQUEST TO LOGOUT
    if not request.user.is_authenticated:
        return Response(
            {"detail": "Not authorized."}, status=status.HTTP_401_UNAUTHORIZED
        )

    logout(request)
    return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)


@api_view(["GET"])
def get_user_view(request):
    if not request.user.is_authenticated:
        return Response(
            {"detail": "Not authorized"}, status=status.HTTP_401_UNAUTHORIZED
        )

    user = get_object_or_404(UserProfile, id=request.user.id)
    serialized_user = UserProfileSerializer(user)

    return Response(serialized_user.data, status=status.HTTP_200_OK)


@api_view(["PUT", "PATCH"])
def update_user_view(request):
    if not request.user.is_authenticated:
        return Response(
            {"detail": "Not authorized"}, status=status.HTTP_401_UNAUTHORIZED
        )

    user = get_object_or_404(UserProfile, id=request.user.id)
    print(request.data.dict())
    serialized_user = UserProfileSerializer(user, request.data.dict(), partial=True)
    serialized_user.is_valid(raise_exception=True)
    serialized_user.update(user, request.data)

    return Response(serialized_user.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def set_avatar_default(request):
    if not request.user.is_authenticated:
        return Response(
            {"detail": "Not authorized"}, status=status.HTTP_401_UNAUTHORIZED
        )

    user = get_object_or_404(UserProfile, id=request.user.id)
    user.avatar = "../media/profile_pics/default_avatar.png"
    user.save()

    return Response(
        {"detail": "Profile picture set to default."}, status=status.HTTP_200_OK
    )


# SESSION BASED AUTHENTICATION VIEWS - LOGIN AND LOGOUT


# CATEGORY OPERATIONS VIEWS
class DefaultPagination(PageNumberPagination):
    page_size = 4
    page_query_param = "page"


class CategoryViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        category_list = Category.objects.all()
        serialized_list = CategorySerializer(category_list, many=True)
        return Response(serialized_list.data, status=status.HTTP_200_OK)

    def create(self, request):
        if request.user.is_staff:
            new_category = request.data
            serialized_category = CategorySerializer(data=new_category)
            serialized_category.is_valid(raise_exception=True)
            serialized_category.save()
            return Response(serialized_category.data, status=status.HTTP_201_CREATED)

        else:
            return Response(
                {"detail": "You do not have permission to do this action."},
                status=status.HTTP_403_FORBIDDEN,
            )

    def update(self, request, pk):
        if request.user.is_staff:
            category = get_object_or_404(Category, id=pk)
            serialized_category = CategorySerializer(category, request.data)
            serialized_category.is_valid(raise_exception=True)
            self.perform_update(serialized_category)
            return Response(serialized_category.data, status=status.HTTP_200_OK)

        else:
            return Response(
                {"detail": "You do not have permission to do this action."},
                status=status.HTTP_403_FORBIDDEN,
            )

    def destroy(self, request, pk):
        if request.user.is_staff:
            category = get_object_or_404(Category, id=pk)
            self.perform_destroy(category)
            return Response(
                {"detail": "Category successfully deleted."}, status=status.HTTP_200_OK
            )

        else:
            return Response(
                {"detail": "You do not have permission to do this action."},
                status=status.HTTP_403_FORBIDDEN,
            )


# CATEGORY OPERATIONS VIEWS


# VISIT OPERATIONS VIEWS
class VisitViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        queryset = Visit.objects.filter(user_id=request.user.id).order_by("-visit")[:5]
        serialized_visit = VisitSerializer(queryset, many=True)
        return Response(serialized_visit.data, status=status.HTTP_200_OK)

    def create(self, request, pk):
        queryset = Visit.objects.filter(user_id=request.user.id).order_by("-visit")[:5]
        for blog in queryset:
            if blog.blog_id == int(pk):
                return

        visit_data = {"user_id": request.user.id, "blog_id": pk}
        serialized_data = VisitSerializer(data=visit_data)
        serialized_data.is_valid(raise_exception=True)
        serialized_data.save()
        return Response(serialized_data.data, status=status.HTTP_201_CREATED)

    def delete(self, request):
        visits = Visit.objects.filter(user_id=request.user.id)
        self.perform_destroy(visits)
        return Response(
            {"detail": "Visits successfully deleted."}, status=status.HTTP_200_OK
        )


# VISIT OPERATIONS VIEWS


# BLOG OPERATIONS VIEWS
class BlogViewSet(ModelViewSet):
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultPagination

    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
    )

    filterset_fields = ("category__id",)

    search_fields = (
        "category__id",
        "user__username",
        "user__first_name",
        "user__last_name",
        "content",
        "title",
    )

    def get_queryset(self):
        if "by_user" in self.request.query_params:
            queryset = Blog.objects.filter(user__id=self.request.user.id)
            return queryset

        return super().get_queryset()

    def paginate_queryset(self, queryset):
        if "no_page" in self.request.query_params:
            return None

        return super().paginate_queryset(queryset)

    def retrieve(self, request, pk):
        VisitViewSet.create(self, request, pk)
        blog = get_object_or_404(Blog, id=pk)
        serialized_blog = BlogSerializer(blog)
        return Response(serialized_blog.data, status=status.HTTP_200_OK)

    def create(self, request):
        blog_data = {"user_id": request.user.id, **request.data}
        serialized_blog = BlogSerializer(data=blog_data)
        serialized_blog.is_valid(raise_exception=True)
        serialized_blog.save()
        return Response(serialized_blog.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk):
        blog = get_object_or_404(Blog, id=pk)
        if blog.user.id == request.user.id:
            serialized_blog = BlogSerializer(blog, request.data, partial=True)
            serialized_blog.is_valid(raise_exception=True)
            self.perform_update(serialized_blog)
            return Response(serialized_blog.data, status=status.HTTP_200_OK)
        else:
            return Response(
                {"detail": "You do not have permission to do this action."},
                status=status.HTTP_403_FORBIDDEN,
            )

    def destroy(self, request, pk):
        blog = get_object_or_404(Blog, id=pk)
        if blog.user.id == request.user.id:
            self.perform_destroy(blog)
            return Response(
                {"detail": "Blog successfully deleted."}, status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"detail": "You do not have permission to do this action."},
                status=status.HTTP_403_FORBIDDEN,
            )


# BLOG OPERATIONS VIEWS


# SAVED BLOG OPERATIONS VIEWS
class SavedBlogViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        savedblogs_list = SavedBlog.objects.filter(user_id=request.user.id)
        serialized_list = SavedBlogSerializer(savedblogs_list, many=True)
        return Response(serialized_list.data, status=status.HTTP_200_OK)

    def create(self, request):
        savedblogs_list = SavedBlog.objects.filter(user_id=request.user.id)
        for blog in savedblogs_list:
            if blog.blog_id == request.data["blog_id"]:
                return Response(
                    {"detail": "Blog already saved."}, status=status.HTTP_200_OK
                )

        data = {"user_id": request.user.id, **request.data}
        serialized_data = SavedBlogSerializer(data=data)
        serialized_data.is_valid(raise_exception=True)
        serialized_data.save()
        return Response(serialized_data.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk):
        savedblog = get_object_or_404(SavedBlog, id=pk)
        if request.user.id == savedblog.user.id:
            self.perform_destroy(savedblog)
            return Response(
                {"detail": "Blog deleted from saved blogs list."},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"detail": "You do not have permissions to do this action"},
                status=status.HTTP_403_FORBIDDEN,
            )


# SAVED BLOG OPERATIONS VIEWSx


# COMMENT OPERATIONS VIEWS
class CommentViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, blog_pk, pk):
        comment = get_object_or_404(Comment, id=pk)
        serialized_comment = CommentSerializer(comment)
        return Response(serialized_comment.data, status=status.HTTP_200_OK)

    def list(self, request, blog_pk):
        comments = Comment.objects.filter(blog_id=blog_pk)
        serialized_comments = CommentSerializer(comments, many=True)
        return Response(serialized_comments.data, status=status.HTTP_200_OK)

    def create(self, request, blog_pk):
        comment_data = {
            "user_id": request.user.id,
            "blog_id": blog_pk,
            **request.data,
        }
        serialized_comment = CommentSerializer(data=comment_data)
        serialized_comment.is_valid(raise_exception=True)
        serialized_comment.save()
        return Response(serialized_comment.data, status=status.HTTP_201_CREATED)

    def update(self, request, blog_pk, pk):
        comment = get_object_or_404(Comment, id=pk)
        if comment.user.id == request.user.id:
            serialized_comment = CommentSerializer(comment, request.data, partial=True)
            serialized_comment.is_valid(raise_exception=True)
            self.perform_update(serialized_comment)
            return Response(serialized_comment.data, status=status.HTTP_200_OK)
        else:
            return Response(
                {"detail": "You do not have permissions to do this action"},
                status=status.HTTP_403_FORBIDDEN,
            )

    def destroy(self, request, blog_pk, pk):
        comment = get_object_or_404(Comment, id=pk)
        if comment.user.id == request.user.id:
            self.perform_destroy(comment)
            comments = Comment.objects.filter(blog_id=blog_pk)
            serialized_comments = CommentSerializer(comments, many=True)
            return Response(serialized_comments.data, status=status.HTTP_200_OK)
        else:
            return Response(
                {"detail": "You do not have permissions to do this action"},
                status=status.HTTP_403_FORBIDDEN,
            )


# COMMENT OPERATIONS VIEWS


# DRAFT OPERATIONS VIEWS
class DraftViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        draft_list = Draft.objects.filter(user_id=request.user.id)
        serialized_drafts = DraftSerializer(draft_list, many=True)
        return Response(serialized_drafts.data, status=status.HTTP_200_OK)

    def create(self, request):
        draft_data = {"user_id": request.user.id, **request.data}
        serialized_data = DraftSerializer(data=draft_data)
        serialized_data.is_valid(raise_exception=True)
        serialized_data.save()
        return Response(serialized_data.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk):
        draft = get_object_or_404(Draft, id=pk)
        if draft.user.id == request.user.id:
            serialized_draft = DraftSerializer(draft, request.data, partial=True)
            serialized_draft.is_valid(raise_exception=True)
            self.perform_update(serialized_draft)
            return Response(serialized_draft.data, status=status.HTTP_200_OK)
        else:
            return Response(
                {"detail": "You do not have permission to do this action"},
                status=status.HTTP_403_FORBIDDEN,
            )

    def destroy(self, request, pk):
        draft = get_object_or_404(Draft, id=pk)
        if draft.user.id == request.user.id:
            self.perform_destroy(draft)
            drafts = Draft.objects.filter(user_id=request.user.id)
            serialized_drafts = DraftSerializer(drafts, many=True)
            return Response(serialized_drafts.data, status=status.HTTP_200_OK)
        else:
            return Response(
                {"detail": "You do not have permissions to do this action"},
                status=status.HTTP_403_FORBIDDEN,
            )


# DRAFT OPERATIONS VIEWS
