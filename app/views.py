import copy 
from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger, InvalidPage
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from app.models import Question, Comment, Post, UserProfile, Tag
from app.forms import LoginForm, SignUpForm, QuestionForm, SettingsForm


def paginate(objects_list, request, per_page=5):
    page_num = request.GET.get('page')
    paginator = Paginator(objects_list, per_page)

    try:
        page_obj = paginator.page(page_num)
    except (EmptyPage, PageNotAnInteger, InvalidPage):
        page_obj = paginator.page(1)

    return page_obj



def home(request):
    newest_questions = Question.objects.get_new()
    return render(request, 'home.html', {'questions': paginate(newest_questions, request)})



def hot(request):
    popular_questions = Question.objects.get_hot()
    popular_questions.reverse()
    return render(request, 'hot.html', {'questions': paginate(popular_questions, request)})


def answer(request, id):
    try:
        question = Question.objects.get_by_id(id)
    except Question.DoesNotExist:
        raise Http404("Question not found.")

    comments = Comment.objects.get_comments_by_question(question)
    return render(request, "answer.html", {'question': question, 'id': id, 'comments': paginate(comments, request)})



@login_required(redirect_field_name='continue')
def ask(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            tags = [tag.strip() for tag in form.cleaned_data['tags'].split(',') if tag.strip()]
            if len(tags) > 5:
                return render(request, "ask.html", {'error': 'Too many tags', 'title': form.cleaned_data['title'], 'description': form.cleaned_data['description']})
            if not tags:
                return render(request, "ask.html", {'error': 'Question must have tags', 'title': form.cleaned_data['title'], 'description': form.cleaned_data['description']})


            post = Post.objects.create(user=request.user.profile, header=form.cleaned_data['title'], description=form.cleaned_data['description'])

            for tag_name in tags:
                tag, _ = Tag.objects.get_or_create(name=tag_name)
                post.tags.add(tag)

            return redirect('question', id=post.id) 

        return render(request, "ask.html", {'error': 'Invalid form data', 'title': form.cleaned_data.get('title', ""), 'description': form.cleaned_data.get('description', ""), 'tags': form.cleaned_data.get('tags', "")})

    return render(request, 'ask.html')





def login(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        next_url = request.GET.get('continue')
        if form.is_valid():
            user = auth.authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user:
                auth.login(request, user)
                return redirect(next_url or 'index')
            return render(request, "login.html", {'error': 'Invalid credentials', 'login': form.cleaned_data['username']})

        return render(request, "login.html", {'error': 'Invalid form data', 'login': form.cleaned_data.get('username', '')})

    return render(request, "login.html")





def reg(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():
            if User.objects.filter(username=form.cleaned_data['username']).exists() or User.objects.filter(email=form.cleaned_data['email']).exists():  # OR condition
                return render(request, "reg.html", context={'error': 'Username or email already in use', 'username': form.cleaned_data['username'], 'email': form.cleaned_data['email']})

            if form.cleaned_data['password'] != form.cleaned_data['password_confirm']:
                return render(request, "reg.html", context={'error': 'Passwords do not match', 'username': form.cleaned_data['username'], 'email': form.cleaned_data['email']})

            user = User.objects.create_user(username=form.cleaned_data['username'], email=form.cleaned_data['email'], password=form.cleaned_data['password'])
            UserProfile.objects.create(user=user, avatar=form.cleaned_data.get('picture', None))  # Use create directly
            return redirect('login')


        return render(request, "reg.html", context={'error': 'Bad request', 'data': form.cleaned_data})



    return render(request, "reg.html")


@login_required(redirect_field_name='continue')
def settings(request):
    if request.method == 'POST':
        form = SettingsForm(request.POST, request.FILES)
        if form.is_valid():
            user = request.user
            user_profile = user.profile


            if User.objects.filter(username=form.cleaned_data['username']).exclude(pk=user.pk).exists():
                return render(request, "settings.html", context={'error': 'Username already in use', 'username': form.cleaned_data['username'], 'email': form.cleaned_data['email']})


            if User.objects.filter(email=form.cleaned_data['email']).exclude(pk=user.pk).exists():
                return render(request, "settings.html", context={'error': 'Email already in use', 'username': form.cleaned_data['username'], 'email': form.cleaned_data['email']})


            user.username = form.cleaned_data['username']
            user.email = form.cleaned_data['email']
            user.save()

            user_profile.avatar = form.cleaned_data.get('picture', user_profile.avatar)
            user_profile.save()

            return redirect('settings')

        return render(request, "settings.html", context={'error': 'Bad request', 'username': form.cleaned_data.get('username', ''), 'email': form.cleaned_data.get('email', '')})


    return render(request, "settings.html")




@login_required(redirect_field_name='continue')
def logout(request):
    auth.logout(request)
    next_url = request.GET.get('continue')
    return redirect(next_url or 'index')


def tag(request, tag_name):
    tag_questions = Question.objects.get_by_tag(tag_name)
    if not tag_questions:
        raise Http404("Tag not found.")

    return render(request, "tag.html", context={'questions': paginate(tag_questions, request), 'tag': tag_name})