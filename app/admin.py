from django.contrib import admin
from app.models import *

# Register your models here.
admin.site.register(Question)
admin.site.register(QuestionTag)
admin.site.register(QuestionLike)
admin.site.register(UserProfile)
admin.site.register(Tag)
admin.site.register(Comment)
admin.site.register(CommentLike)