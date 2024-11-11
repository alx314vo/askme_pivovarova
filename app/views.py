import copy
from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage, PageNotAnInteger, InvalidPage
from random import choice, randint

# Create your views here.

tags = ["meow", "cprog", "ubuntu", "cats", "bmstu", "vk", "wow"]

QUESTIONS = []
for i in range(1, 100):
    QUESTIONS.append({
        'title': 'title ' + str(i),
        'id': i,
        'text': 'text' + str(i),
        'tags': [choice(tags), choice(tags)],
        'likes': randint(-100, 100)
    })


def paginate(objects_list, request, per_page=5):
    page_num = request.GET.get('page')

    p = Paginator(objects_list, per_page)
    try:
        question_page = p.page(page_num)
    except (EmptyPage, PageNotAnInteger, InvalidPage) as e:
        question_page = p.page(1)

    return question_page


def home(request):
    return render(request, 'home.html', context={'questions': paginate(QUESTIONS, request)}
                  )


def hot(request):
    hot_questions = copy.deepcopy(QUESTIONS)
    hot_questions.reverse()
    return render(request, 'hot.html', context={'questions': paginate(hot_questions, request)}
                  )


def answer(request, id):
    try:
        question = QUESTIONS[id - 1]
    except IndexError:
        raise Http404("Question not found.")
    return render(request, "answer.html", context={'question': question, 'id': id})


def ask(request):
    return render(request, 'ask.html')


def login(request):
    return render(request, 'login.html')


def reg(request):
    return render(request, 'reg.html')


def tag(request, tag_name):
    tag_questions = list(
        filter(lambda question: tag_name in question['tags'], QUESTIONS))
    if not tag_questions:
        raise Http404("Tag not found")

    return render(request, "tag.html", context={'questions': paginate(tag_questions, request), 'tag': tag_name})
