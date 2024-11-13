from django.db import models

# Create your models here.

from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    nickname = models.CharField(max_length=255, unique=True)
    profile_image = models.ImageField(upload_to='uploads/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nickname

class Tag(models.Model):
    tag = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.tag
    
    
class QuestionManager(models.Manager):
    def get_new(self):
        return self.order_by('-created_at')
        
    def get_by_tag(self, tag_name):
        return self.filter(questiontag__tag__tag=tag_name)
    
    def get_by_id(self, id):
        return self.get(id=id)
    
    def get_hot(self):
        return self.order_by('-question_likes')


class Question(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    title = models.CharField(max_length=255)
    tags = models.ManyToManyField(Tag, through='QuestionTag', related_name='questions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = QuestionManager()

    def __str__(self):
        return self.title  # Исправлено на title
    
class QuestionTag(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('question', 'tag')
        
    def __str__(self):
        return f"{self.question.title} tagged with {self.tag.tag}"

class QuestionLike(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='question_likes')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='question_likes')  # Изменено на question_likes
    created_at = models.DateTimeField(auto_now_add=True)
    value = models.IntegerField(choices=[(1, 'Like'), (-1, 'Dislike')], default=1)

    class Meta:
        unique_together = ('user', 'question')
        indexes = [
            models.Index(fields=['user', 'question']),
        ]
    def __str__(self):
        return f"{self.user.nickname} liked {self.question.title}"  # Исправлено на title

class CommentManager(models.Manager):
    def get_comments_by_question(self, question):
        return self.filter(question=question).order_by('-created_at')

class Comment(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CommentManager()

    def __str__(self):
        return f"Comment by {self.user.nickname} on {self.question.title}"  # Исправлено на title

class CommentLike(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='comment_likes')
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='comment_likes')  # Изменено на comment_likes
    created_at = models.DateTimeField(auto_now_add=True)
    value = models.IntegerField(choices=[(1, 'Like'), (-1, 'Dislike')], default=1)

    class Meta:
        unique_together = ('user', 'comment')
        
    def __str__(self):
        return f"{self.user.username} liked a comment on {self.comment.question.title}"  # Исправлено на title

