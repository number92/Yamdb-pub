import csv
from django.core.management.base import BaseCommand
from django.shortcuts import get_object_or_404

from reviews.models import Category, Genre, Title, Comment, Review, User


class Command(BaseCommand):
    """Загрузка данных в БД"""

    def handle(self, *args, **options):
        try:
            category_load()
            genre_load()
            titles_load()
            genre_title()
            user_load()
            reviews_load()
            comment_load()

        except Exception as er:
            print(er)


def category_load():
    with open('static/data/category.csv',
              encoding='utf-8', mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            Category.objects.get_or_create(id=row['id'],
                                           name=row['name'],
                                           slug=row['slug']
                                           )


def genre_load():
    with open('static/data/genre.csv',
              encoding='utf-8', mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            Genre.objects.get_or_create(id=row['id'],
                                        name=row['name'],
                                        slug=row['slug']
                                        )


def titles_load():
    with open('static/data/titles.csv',
              encoding='utf-8', mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            category = Category.objects.get(pk=row['category'])
            Title.objects.get_or_create(id=row['id'],
                                        name=row['name'],
                                        year=row['year'],
                                        category=category
                                        )


def genre_title():
    with open('static/data/genre_title.csv',
              encoding='utf-8', mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            title_obj = get_object_or_404(Title, id=row['title_id'])
            genre_obj = get_object_or_404(Genre, id=row['genre_id'])
            title_obj.genre.add(genre_obj)
            title_obj.save()


def user_load():
    with open('static/data/users.csv',
              encoding='utf-8', mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            User.objects.create(id=row['id'],
                                username=row['username'],
                                email=row['email'],
                                role=row['role'],
                                bio=row['bio'],
                                first_name=row['first_name'],
                                last_name=row['last_name']
                                )


def reviews_load():
    with open('static/data/review.csv',
              encoding='utf-8', mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            author = User.objects.get(id=row['author'])
            Review.objects.create(id=row['id'],
                                  title_id=row['title_id'],
                                  text=row['text'],
                                  author=author,
                                  score=row['score'],
                                  pub_date=row['pub_date']
                                  )


def comment_load():
    with open('static/data/comments.csv',
              encoding='utf-8', mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            Comment.objects.create(id=row['id'],
                                   text=row['text'],
                                   pub_date=row['pub_date'],
                                   author_id=row['author'],
                                   review_id=row['review_id']
                                   )
