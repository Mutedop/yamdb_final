from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from .models import Category, Comment, Genre, Review, Title, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name',
                  'username', 'bio', 'email',
                  'role', 'confirmation_code']
        read_only_field = ('email', )


class ObtainingConfirmationCodeSerializer(serializers.ModelSerializer):
    """
    Sending confirmation code to the transmitted email.
    """
    class Meta:
        model = User
        fields = ('email', )


class TokenSerializer(serializers.Serializer):
    """
    Receiving a JWT token in exchange for email and confirmation code.
    """
    email = serializers.EmailField(required=True)
    confirmation_code = serializers.CharField(required=True)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ('id', )
        model = Category


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ('id', )
        model = Genre


class TitleWriteSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        many=True,
        slug_field='slug',
        queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )

    class Meta:
        fields = '__all__'
        model = Title


class TitleReadSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(read_only=True, many=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.IntegerField(read_only=True, required=False)

    class Meta:
        fields = '__all__'
        model = Title


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True)
    review = serializers.SlugRelatedField(
        slug_field='id', read_only=True)

    class Meta:
        fields = '__all__'
        model = Comment


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='username'
    )
    title = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='id'
    )

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date', 'title')
        model = Review

    def validate(self, data):
        title = get_object_or_404(
            Title,
            pk=self.context['view'].kwargs.get('title_id')
        )
        author = self.context['request'].user
        if (Review.objects.filter(title=title, author=author).exists()
                and self.context['request'].method == 'POST'):
            raise serializers.ValidationError(
                'Нельзя публиковать больше одного отзыва на Title'
            )
        return data
