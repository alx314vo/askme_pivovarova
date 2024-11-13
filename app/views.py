import copy
from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage, PageNotAnInteger, InvalidPage
from random import choice, randint
from app.models import Question, Comment

# Create your views here.

def paginate(objects_list, request, per_page=5):
    page_num = request.GET.get('page')

    p = Paginator(objects_list, per_page)
    try:
        question_page = p.page(page_num)
    except (EmptyPage, PageNotAnInteger, InvalidPage) as e:
        question_page = p.page(1)

    return question_page


def home(request):
    QUESTIONS = Question.objects.get_new()
    return render(request, 'home.html', context={'questions': paginate(QUESTIONS, request)}
                  )


def hot(request):
    hot_questions = Question.objects.get_hot()
    hot_questions.reverse()
    return render(request, 'hot.html', context={'questions': paginate(hot_questions, request)}
                  )


def answer(request, id):
    try:
        question = Question.objects.get_by_id(id)
    except IndexError:
        raise Http404("Question not found.")
    comments = Comment.objects.get_comments_by_question(question)
    #print(comments)
    return render(request, "answer.html", context={'question': question, 'id': id, 'comments': paginate(comments, request)})


def ask(request):
    return render(request, 'ask.html')


def login(request):
    return render(request, 'login.html')


def reg(request):
    return render(request, 'reg.html')

def settings(request):
    return render(request, 'settings.html')

def tag(request, tag_name):
    tag_questions = Question.objects.get_by_tag(tag_name)
    if not tag_questions:
        raise Http404("Tag not found")

    return render(request, "tag.html", context={'questions': paginate(tag_questions, request), 'tag': tag_name})
