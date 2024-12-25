from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import IntegrityError
from app.models import UserProfile, Tag, Question, QuestionTag, QuestionLike, Comment, CommentLike
import random

def create_tags(num_users):
    tags = []
    existing_tags = set(Tag.objects.values_list('tag', flat=True))
    
    for i in range(num_users):
        tag_name = f'tag{i}'
        
        if tag_name not in existing_tags:
            tag = Tag.objects.create(tag=tag_name)
            tags.append(tag)
            
            if len(tags) % 10 == 0:
                print(f"Создано {len(tags)} тегов")
    
    return tags

def create_user_profile(user, nickname):
    existing_profile, created = UserProfile.objects.get_or_create(
        user=user,
        nickname=nickname
    )
    
    if created:
        print(f"Создан новый профиль для пользователя {user.username}: {nickname}")
        return existing_profile
    else:
        print(f"Профиль для пользователя {user.username} с никнеймом {nickname} уже существует")
        return None

def create_user_profiles(num_users):
    profiles = []
    existing_nicknames = set(UserProfile.objects.values_list('nickname', flat=True))
    
    for i in range(num_users):
        username = f'user{i}'
        user, created = User.objects.get_or_create(username=username)
        
        if created:
            nickname = f'user__{i}'
            if nickname not in existing_nicknames:
                profile = create_user_profile(user, nickname)
                if profile:
                    profiles.append(profile)
            
            if len(profiles) % 100 == 0:
                print(f"Обработано {len(profiles)} профилей пользователей")
    
    return profiles

def create_questions(ratio):
    tags = Tag.objects.all()
    
    questions = []
    for i in range(ratio):
        author = UserProfile.objects.get(nickname=f'user_{i}')
        title = f'Вопрос {i}'
        text = f'Это вопрос номер {i} для пользователя {author.user.username}'
        
        question = Question.objects.create(
            user=author,
            title=title,
            text=text
        )
        
        # Выбираем случайные теги для вопроса
        selected_tags = random.sample(list(tags), min(ratio, len(tags)))
        for tag in selected_tags:
            QuestionTag.objects.create(question=question, tag=tag)
        
        questions.append(question)
    
    print(f"Создано {ratio} вопросов")
    
    # Создаем комментарии для каждого вопроса
    create_question_comments(questions)

def create_question_comments(questions):
    for question in questions:
        for _ in range(10):
            author = random.choice(UserProfile.objects.all())
            text = f'Комментарий к вопросу {question.id}'
            Comment.objects.create(user=author, question=question, text=text)

def create_answers(ratio):
    tags = Tag.objects.all()
    
    for i in range(ratio):
        author = UserProfile.objects.get(nickname=f'user_{i}')
        question = Question.objects.order_by('-id')[i]
        text = f'Ответ на вопрос {question.id}'
        
        Comment.objects.create(question=question, user=author, text=text)
        
        # Обновляем теги для ответа
        tags_for_answer = random.sample(list(tags), min(5, len(tags)))
        for tag in tags_for_answer:
            # Удаляем существующие связи вопроса с тегом
            QuestionTag.objects.filter(question=question).filter(tag=tag).delete()
            
            # Создаем новую связь между вопросом и тегом
            QuestionTag.objects.create(question=question, tag=tag)
    
    print(f"Создано {ratio} ответов")

def create_comments(ratio):
    for i in range(ratio):
        author = UserProfile.objects.get(nickname=f'user_{i}')
        parent = Question.objects.order_by('-id')[i]
        text = f'Комментарий к вопросу {parent.id}'
        
        Comment.objects.create(user=author, question=parent, text=text)

def create_likes(ratio):
    posts = Question.objects.all()
    comments = Comment.objects.all()
    
    post_likes = []
    comment_likes = []

    for i in range(ratio * 200):  
        user = random.choice(UserProfile.objects.all())
        
        while True:
            post = random.choice(posts)
            like_value = random.choice([1, -1])
            
            try:
                QuestionLike.objects.get(user=user, question=post, value=like_value)
                break
            except QuestionLike.DoesNotExist:
                post_like = QuestionLike(user=user, question=post, value=like_value)
                post_likes.append(post_like)
                
                break

        while True:
            comment = random.choice(comments)
            like_value = random.choice([1, -1])
            
            try:
                CommentLike.objects.get(user=user, comment=comment, value=like_value)
                break
            except CommentLike.DoesNotExist:
                comment_like = CommentLike(user=user, comment=comment, value=like_value)
                comment_likes.append(comment_like)
                
                break

        if len(post_likes) >= 1000:  
            try:
                QuestionLike.objects.bulk_create(post_likes)
            except IntegrityError:
                print(f"Произошла ошибка при создании лайков для вопросов: {str(i)}")
            
            post_likes.clear()

        if len(comment_likes) >= 1000:  
            try:
                CommentLike.objects.bulk_create(comment_likes)
            except IntegrityError:
                print(f"Произошла ошибка при создании лайков для комментариев: {str(i)}")
            
            comment_likes.clear()

    # Создаем оставшиеся лайки
    try:
        QuestionLike.objects.bulk_create(post_likes)
    except IntegrityError:
        print(f"Произошла ошибка при создании оставшихся лайков для вопросов: {str(i)}")

    try:
        CommentLike.objects.bulk_create(comment_likes)
    except IntegrityError:
        print(f"Произошла ошибка при создании оставшихся лайков для комментариев: {str(i)}")

    print(f"Завершено создание {len(post_likes) + len(comment_likes)} оценок")

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int)

    def handle(self, *args, **options):
        ratio = options['ratio']
        
        # Создаем пользователей
        users_to_create = []
        existing_users = set(User.objects.values_list('username', flat=True))

        for i in range(ratio):
            username = f'user{i}'
            
            if username not in existing_users:
                user = User.objects.create(username=username)
                users_to_create.append(user)
                
                print(f"Создан новый пользователь: {username}")
            else:
                print(f"Пользователь {username} уже существует")

        # Создаем профили пользователей
        UserProfile.objects.bulk_create([
            UserProfile(user=user, nickname=f'user_{i}')
            for i, user in enumerate(users_to_create)
        ])
        
        create_tags(ratio)
        
        # Создаем вопросы
        create_questions(ratio)
