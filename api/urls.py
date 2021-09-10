from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (CategoryViewSet, CommentViewSet, GenreViewSet,
                    ObtainingConfirmationCodeView, ReviewViewSet, TitleViewSet,
                    TokenView, UserViewSet)

v1_router = DefaultRouter()
v1_router.register(
    'categories',
    CategoryViewSet,
    basename='categories-list'
)
v1_router.register(
    'genres',
    GenreViewSet,
    basename='genres-list'
)
v1_router.register(
    'titles',
    TitleViewSet,
    basename='titles-list'
)
v1_router.register(
    'users',
    UserViewSet
)
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='review-list'
)
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comment-list'
)

urlpatterns = [
    path('v1/',
         include(v1_router.urls)),
    path('v1/auth/email/',
         ObtainingConfirmationCodeView.as_view(),
         name='conformation_code'),
    path('v1/auth/token/',
         TokenView.as_view(),
         name='token'),
    path('v1/token/refresh/',
         TokenRefreshView.as_view(),
         name='token_refresh'),
]
