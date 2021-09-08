from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User, auth
from django.contrib import messages
from .models import *


# Create your views here.
# Assigning the function to each url
def index(request):
    return render(request, 'index.html')

def test(request):
    return render(request, 'test.html')

def a(request):
    return render(request, 'a.html')

def register(request):
    # Check if there is a post request / If a user registered
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirmation = request.POST.get('password_confirmation')
        
        # Empty Validation -> in case the user play with inspect element
        # nanti gantiin sesuai minimalnya brp atau gimana bebas
        if len(first_name) == 0 or len(last_name) == 0 or len(username) == 0 or len(email) == 0 or len(password) == 0 or len(password_confirmation) == 0:
            messages.info(request, 'Please fill out all fields!')
            return redirect('/auth/register')

        if password == password_confirmation:
            # Check if username already exists
            if User.objects.filter(username=username).exists():
                messages.info(request, 'Username Already Taken!')
                return redirect('/auth/register')

            # Check if email already exists
            elif User.objects.filter(email=email).exists():
                messages.info(request, 'Email Already Registered!')
                return redirect('/auth/register')
            
            # If everything is fine, create a new user
            else:
                user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username, email=email, password=password)
                user.save()
                messages.info(request, 'You have been registered successfully')
                return redirect('/auth/login')
        else:
            messages.info(request, 'Password and Confirmation do not match!')
            return redirect('/auth/register')
    else:
        return render(request, 'auth/register.html')

def login(request):
    # Check if there is a post request / If a user logged in
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Invalid Credentials!')
            return redirect('/auth/login')
    else:
        return render(request, 'auth/login.html')

def logout(request):
    auth.logout(request)
    return redirect('/')

def post_Url(request, id, title):
    # Title in the link is just for vanity url
    if id is not None and title is not None:
        post = Post.objects.get(id=id)
        if post is not None:
            comment = Comment.objects.filter(post=post)
            likes = Like.objects.filter(post=post)
            return render(request, 'post.html', {'post': post, 'comment': comment, 'likes': likes})
        else:
            return HttpResponse('404')
    else:
        # return 404
        return HttpResponse('404')

def post_Content(request, id):
    if id is not None:
        post = Post.objects.get(id=id)
        if post is not None:
            # Redirect to vanity url
            return redirect('/post/' + str(post.id) + '/' + post.title.replace(' ', '_'))
        else:
            print("you are inside id")
            return HttpResponse('404')
    else:
        # return 404
        print("you are inside else")
        return HttpResponse('404')

def post(request):
    posts = Post.objects.all()
    print(posts)

    return render(request, 'post.html', {'posts': posts})

def post_Create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        user = request.user
        post = Post(title=title, content=content, user=user)
        post.save()
        return redirect('/post')
    else:
        return render(request, 'post/post_create.html')

def post_Edit(request):
    if request.method == 'POST':
        # Can't change title
        content = request.POST.get('content')
        content = request.POST.get('id')
        post = Post.objects.get(id=id)
        post.content = content
        post.save()
        return redirect('/post')
    else:
        return render(request, 'post/post_edit.html')

def post_Report(request):
    if request.method == 'POST':
        # Report
        user = request.user
        post = Post.objects.get(id=id)
        reason = request.POST.get('reason')
        report = Report(user=user, post=post, reason=reason)
        report.save()
        return redirect('/post')
    else:
        return render(request, 'post/post_report.html')