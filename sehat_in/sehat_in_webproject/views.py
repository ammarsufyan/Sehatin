from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User, auth
from django.contrib import messages
from .models import *
from django.core.exceptions import PermissionDenied
from django.http import Http404
import json

# Create your views here.
# Assigning the function to each url
def error_404_view(request, exception):
    return render(request, 'error/404.html')

def error_403_view(request, exception):
    return render(request, 'error/403.html')

def index(request):
    return render(request, 'index.html')

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
                messages.info(request, f'Username "{username}" Already Taken! Please use a different username!')
                return render(request, 'auth/register.html', {'email': str(email), 'username': str(username), 'first_name': str(first_name), 'last_name': str(last_name)})

            # Check if email already exists
            elif User.objects.filter(email=email).exists():
                messages.info(request, f'The email "{email}" Already Registered!')
                return render(request, 'auth/register.html', {'email': str(email), 'username': str(username), 'first_name': str(first_name), 'last_name': str(last_name)})
            
            # If everything is fine, create a new user
            else:
                user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username, email=email, password=password)
                user.save()
                messages.info(request, 'You have been registered successfully, you can now log in to your account')
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
        # To ensure the vanity url is always exactly the title
        if title.replace('-', ' ') != post.title:
            return redirect('/post/' + str(post.id) + '/' + post.title.replace(' ', '-'))
        
        if post is not None:
            comments = Comment.objects.filter(post=post)
            likes = Like.objects.filter(post=post)
            return render(request, 'post/postview.html', {'post': post, 'comments': comments, 'likes': likes})
        else:
            raise Http404
    else:
        # return 404
        raise Http404

def post_Content(request, id):
    if id is not None:
        post = Post.objects.get(id=id)
        if post is not None:
            # Redirect to vanity url
            return redirect('/post/' + str(post.id) + '/' + post.title.replace(' ', '-'))
        else:
            raise Http404
    else:
        # return 404
        raise Http404

def post(request):
    posts = Post.objects.all()
    tags = Tag.objects.all()
    return render(request, 'post/index.html', {'posts': posts.order_by('-created_at'), 'tags': tags})

def post_Tag(request, tagName):
    tag = Tag.objects.get(name=tagName)
    if tag is not None:
        posts = Post.objects.filter(tag=tag)
        return render(request, 'post/tag.html', {'posts': posts.order_by('-created_at'), 'tag': tag})
    else:
        raise Http404

def post_Create(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            title = request.POST.get('title')
            content = request.POST.get('content')
            user = request.user
            tag_get = request.POST.get('tag')
            tag = Tag.objects.get(name=tag_get)
            post = Post(title=title, content=content, user=user, tag=tag)
            post.save()

            getPost = Post.objects.get(title=title, content=content, user=user)
            return redirect('/post/' + str(getPost.id) + '/' + getPost.title.replace(' ', '-'))
        else:
            tags = Tag.objects.all()
            return render(request, 'post/create.html', {'tags': tags})
    else:
        messages.info(request, 'Need to login first!')
        return redirect('/auth/login')

def post_Edit(request, id, title):
    # Check if user is logged in and it's the post owner
    if request.user != Post.objects.get(id=id).user:
        raise PermissionDenied()

    if request.user.is_authenticated:
        if request.method == 'POST':
            # Can't change title
            content = request.POST.get('content') # content change
            tag_name = request.POST.get('tag') # if user change the tag, it will be changed

            # Get the post and tag object
            post = Post.objects.get(id=id)
            tag = Tag.objects.get(name=tag_name)

            # Change the stuff
            post.content = content
            post.tag = tag

            # Save
            post.save()

            # Redirect to the post
            return redirect('/post/' + str(post.id) + '/' + post.title.replace(' ', '-'))
        else:
            post = Post.objects.get(id=id)
            tag = Tag.objects.all()

            if title.replace('-', ' ') != post.title:
                return redirect('/post/' + str(post.id) + '/' + post.title.replace(' ', '-') + '/edit')

            return render(request, 'post/edit.html', {'post': post, 'tags': tag})
    else:
        messages.info(request, 'Need to login first!')
        return redirect('/auth/login')

def post_Like(request, id, title):
    if request.method == 'POST':
        if request.user.is_authenticated:
            post = Post.objects.get(id=id)
            user = request.user
            like = Like.objects.filter(user=user, post=post)
            if like.count() == 0:
                like = Like(user=user, post=post)
                like.save()

                # Get amount of posts like
                likes = Like.objects.filter(post=post)
                names = []
                for like in likes:
                    names.append(like.user.username)
                jsonData = {'likes': likes.count(), 'names': names}

                return HttpResponse(json.dumps(jsonData))
            else:
                like.delete()

                # Get amount of posts like
                likes = Like.objects.filter(post=post)
                names = []
                for like in likes:
                    names.append(like.user.username)
                jsonData = {'likes': likes.count(), 'names': names}

                return HttpResponse(json.dumps(jsonData))
        else:
            return redirect('/post/' + str(id) + '/' + title.replace(' ', '-'))
    else:
        raise Http404

def post_Report(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            # Report
            user = request.user
            post = Post.objects.get(id=id)
            reason = request.POST.get('reason')
            report = Report(user=user, post=post, reason=reason)
            report.save()
            return redirect('/post')
        else:
            return render(request, 'post/report.html')
    else:
        messages.info(request, 'Need to login first!')
        return redirect('/auth/login')