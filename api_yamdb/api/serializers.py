from django.conf import settings
from django.shortcuts import get_object_or_404

from rest_framework import serializers
from reviews.models import Category, Comment, Genre, Review, Title, User
from .mixins import ValidateUsernameMixin


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug')
        model = Category


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        many=True, queryset=Genre.objects.all(), slug_field='slug',
    )
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(), slug_field='slug'
    )

    class Meta:
        fields = (
            'id', 'name', 'year', 'description', 'genre', 'category')
        model = Title


class TitleInfoSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True)
    category = CategorySerializer()
    rating = serializers.IntegerField()

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        )
        read_only_fields = fields


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True,
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')

    def validate(self, data):
        if self.context['request'].method != 'POST':
            return data
        title_id = self.context['view'].kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        author = self.context['request'].user
        if Review.objects.filter(
                author=author, title=title.id).exists():
            raise serializers.ValidationError(
                'На одно произведение можно оставить один отзыв.'
            )
        return data

    def validate_score(self, value):
        if settings.MIN_SCORE <= value <= settings.MAX_SCORE:
            return value
        raise serializers.ValidationError(
            f'Оценка должна быть от {settings.MIN_SCORE} '
            f'до {settings.MAX_SCORE}')


class SignupSerializer(ValidateUsernameMixin,
                       serializers.Serializer):
    username = serializers.CharField(
        max_length=settings.USERNAME_LENGTH,
        required=True,
    )
    email = serializers.EmailField(
        max_length=settings.EMAIL_LENGTH,
        required=True,
    )


class TokenSerializer(ValidateUsernameMixin,
                      serializers.Serializer):
    username = serializers.CharField(
        max_length=settings.USERNAME_LENGTH,
        required=True
    )
    confirmation_code = serializers.CharField(
        max_length=settings.CONFIRMATION_CODE_LENGTH,
        required=True
    )


class UserSerializer(ValidateUsernameMixin,
                     serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'username', 'email',
            'first_name', 'last_name',
            'bio', 'role'
        )


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
