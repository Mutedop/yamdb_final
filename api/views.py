import uuid

from django.core.mail import send_mail
from django.db.models.aggregates import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from api_yamdb.settings import YAMDB_EMAIL

from .filters import TitleFilter
from .models import Category, Genre, Review, Title, User
from .permissions import IsAdmin, IsAdminOrReadOnly, IsAuthorOrStaffOrReadOnly
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ObtainingConfirmationCodeSerializer,
                          ReviewSerializer, TitleReadSerializer,
                          TitleWriteSerializer, TokenSerializer,
                          UserSerializer)


class BaseModelViewSet(mixins.ListModelMixin,
                       mixins.CreateModelMixin,
                       mixins.DestroyModelMixin,
                       viewsets.GenericViewSet):
    pass


class CategoryViewSet(BaseModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAdminOrReadOnly, )
    filter_backends = [SearchFilter]
    search_fields = ('name', )
    lookup_field = 'slug'


class GenreViewSet(BaseModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAdminOrReadOnly, )
    filter_backends = [SearchFilter]
    search_fields = ('name', )
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')
    ).order_by('name')
    pagination_class = PageNumberPagination
    permission_classes = (IsAdminOrReadOnly, )
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PATCH']:
            return TitleWriteSerializer
        return TitleReadSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = (IsAdmin, )
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination
    lookup_field = 'username'
    filter_backends = [SearchFilter]
    search_fields = ('username', )

    @action(detail=False, methods=['get', 'patch'],
            permission_classes=(IsAuthenticated, ),
            url_name='me', url_path='me')
    def me(self, request, *args, **kwargs):
        instance = self.request.user
        serializer = self.get_serializer(instance)
        if self.request.method == 'PATCH':
            serializer = self.get_serializer(
                instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(email=instance.email, role=instance.role)
        return Response(serializer.data, status=200)


class ObtainingConfirmationCodeView(APIView):
    """Processing a request to receive a code,
    sending it to the email specified by the user during registration.
    """
    permission_classes = (AllowAny, )

    def post(self, request):
        serializer = ObtainingConfirmationCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        confirmation_code = uuid.uuid4()
        User.objects.get_or_create(email=email,
                                   username=str(email),
                                   confirmation_code=confirmation_code,
                                   is_active=False)
        send_mail(
            'Confirmation Code',
            f'confirmation_code: {confirmation_code}',
            YAMDB_EMAIL,
            [email],
            fail_silently=False,
        )
        return Response(
            {'result': f'Confirmation Code отправлен на {email}'},
            status=200
        )


class TokenView(APIView):
    """
    Handling a request to get(method-post) or refresh the user's JWT token
    """
    permission_classes = (AllowAny, )

    def post(self, *args, **kwargs):
        serializer = TokenSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(User,
                                 email=serializer.validated_data['email'])
        user.save()
        refresh_token = RefreshToken.for_user(user)
        return Response({'token': str(refresh_token.access_token)})


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrStaffOrReadOnly)
    pagination_class = PageNumberPagination

    def get_queryset(self):
        review = get_object_or_404(Review, id=self.kwargs.get('review_id'))
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(Review, id=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review=review)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrStaffOrReadOnly)
    pagination_class = PageNumberPagination

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)
