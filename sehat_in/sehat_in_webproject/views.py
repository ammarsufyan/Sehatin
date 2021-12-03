from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User, auth
from django.contrib import messages
from .models import *
from django.core.exceptions import PermissionDenied
from django.http import Http404, JsonResponse
import json
import re
from django.core import serializers
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from itertools import chain

# Views of each URL
# Assigning the function to each url
# ----------------------------------------------------------------
# Error
def error_404_view(request, exception):
    """Custom 404 Error View"""
    return render(request, 'error/404.html')

def error_403_view(request, exception):
    """Custom 403 Error View"""
    return render(request, 'error/403.html')

# ----------------------------------------------------------------
# Home
def index(request):
    """Index page (Home)"""
    # Get 3 latest articles
    latest_articles = Artikel.objects.all().order_by('-created_at')[:3]

    # Get 3 latest forum
    latest_forum = Forum.objects.all().order_by('-created_at')[:3]

    # if user is authenticated
    if request.user.is_authenticated:
        # Get user's notification
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    else:
        notifications = None

    return render(request, 'index.html', {'latest_articles': latest_articles, 'latest_forum': latest_forum, 'notifications': notifications})

# ----------------------------------------------------------------
# Auth
def register(request):
    """Request, if no request open page like usual. Request made using html form.
    
    If user alread logged in: Redirect home
    Onsucess: Redirect to login
    Onfail: Return error message
    """
    # Check if user is logged in
    if request.user.is_authenticated:
        return redirect('/')

    # Check if there is a post request / If a user registered
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirmation = request.POST.get('password_confirmation')
        
        # Empty Validation -> in case the user play with inspect element
        if len(first_name) == 0 or len(last_name) == 0 or len(username) == 0 or len(email) == 0 or len(password) == 0 or len(password_confirmation) == 0:
            messages.info(request, 'Please fill out all fields!')
            return redirect('/auth/register')

        # Check length
        if len(username) < 5 or len(username) > 50:
            messages.info(request, 'Username must be between 5 and 50 characters!')
            return redirect('/auth/register')
        
        regex = "[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,4}$"
        if not re.search(regex, email) or len(email) < 3:
            messages.info(request, 'Invalid email address!')
            return redirect('/auth/register')

        lowercase = re.compile('[a-z]')
        uppercase = re.compile('[A-Z]')
        if not lowercase.search(password) or not uppercase.search(password) or len(password) < 8 or len(password) > 50:
            messages.info(request, 'Password must be between 8 and 50 characters and contain at least one lowercase and one uppercase letter!')
            return redirect('/auth/register')

        # Prevent special characters on username
        regex = "[^a-zA-Z0-9_]"
        if re.search(regex, username):
            messages.info(request, 'Username must not contain special characters!')
            return redirect('/auth/register')

        if password == password_confirmation:
            # Invalid username
            if username.lower() == "deleted":
                messages.info(request, 'Invalid Username!')
                return render(request, 'auth/register.html', {'email': str(email), 'username': str(username), 'first_name': str(first_name), 'last_name': str(last_name)})

            # if user contain admin
            if 'admin' in username.lower():
                messages.info(request, 'Invalid Username!')
                return render(request, 'auth/register.html', {'email': str(email), 'username': str(username), 'first_name': str(first_name), 'last_name': str(last_name)})

            # Check if username already exists 
            elif User.objects.filter(username__iexact=username).exists():
                messages.info(request, f'Username "{username}" Already Taken! Please use a different username!')
                return render(request, 'auth/register.html', {'email': str(email), 'username': str(username), 'first_name': str(first_name), 'last_name': str(last_name)})

            # Check if email already exists case insensitive
            elif User.objects.filter(email__iexact=email).exists():
                messages.info(request, f'The email "{email}" Already Registered!')
                return render(request, 'auth/register.html', {'email': str(email), 'username': str(username), 'first_name': str(first_name), 'last_name': str(last_name)})
            
            # If everything is fine, create a new user
            else:
                user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username, email=email, password=password)
                user.save()

                # Create a new user profile
                user_profile = UserProfile(user=user)
                user_profile.save()

                messages.info(request, 'You have been registered successfully, you can now log in to your account')
                return redirect('/auth/login')
        else: # If password and password confirmation are not the same
            messages.info(request, 'Password and Confirmation do not match!')
            return redirect('/auth/register')
    else: # If there is no post request
        return render(request, 'auth/register.html')

def login(request):
    """Login, if no request open page like usual. Request made using html form
    
    If user alread logged in: Redirect home
    Onsucess: Redirect to home
    Onfail: Return error message
    """
    # Check if user is logged in
    if request.user.is_authenticated:
        return redirect('/')

    # Check if there is a post request / If a user logged in
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if username == "deleted":
            messages.info(request, 'Invalid Credentials!')
            return redirect('/auth/login')

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
    """Logout"""
    # Check if user is logged in
    if request.user.is_authenticated:
        auth.logout(request)

    return redirect('/')

# ----------------------------------------------------------------
# Forum
def forum(request):
    """See all post"""
    tags = Tag.objects.filter(type="Forum")

    # if user is authenticated
    if request.user.is_authenticated:
        # Get user's notification
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    else:
        notifications = None

    searching = False
    q = None
    # Check if there is a search
    if request.GET.get('q'):
        query = request.GET.get('q')
        paginator = Paginator(Forum.objects.filter(title__icontains=query).order_by('-created_at'), 25)
        page = request.GET.get('page')
        posts = paginator.get_page(page)
        searching = True
        q = query

        # Check if no result found
        if paginator.count == 0:
            messages.info(request, 'No result found')
            return redirect('/forum')
    else:
        paginator = Paginator(Forum.objects.all().order_by('-created_at'), 25)
        page = request.GET.get('page')
        posts = paginator.get_page(page)

    return render(request, 'forum/index.html', {'posts': posts, 'tags': tags, 'searching': searching, 'notifications': notifications, 'q': q})

def forum_Tag(request, tagName):
    """See post by tag"""
    tag = Tag.objects.get(name=tagName.replace('-', ' '))
    if tag is not None and tag.type == 'Forum':
        # if user is authenticated
        if request.user.is_authenticated:
            # Get user's notification
            notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
        else:
            notifications = None

        paginator = Paginator(Forum.objects.filter(tag=tag).order_by('-created_at'), 25)
        page = request.GET.get('page')
        posts = paginator.get_page(page)
        return render(request, 'forum/tag.html', {'posts': posts, 'tag': tag, 'notifications': notifications})
    else:
        raise Http404

def forum_Content(request, id):
    """Redirect to forum content"""
    if id is not None:
        try:
            post = Forum.objects.get(id=id)
        except:
            raise Http404

        # Redirect to vanity url
        return redirect('/forum/' + str(post.id) + '/' + post.title.replace(' ', '-'))
    else:
        # return 404
        raise Http404

def forum_Url(request, id, title):
    """Generate URL for post with vanity url of title"""
    # Title in the link is just for vanity url
    if id is not None and title is not None:
        post = Forum.objects.get(id=id)
        
        # if user is authenticated
        if request.user.is_authenticated:
            # Get user's notification
            notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
        else:
            notifications = None

        # To ensure the vanity url is always exactly the title
        if title.replace('-', ' ') != post.title.replace('?', ''):
            return redirect('/forum/' + str(post.id) + '/' + post.title.replace(' ', '-').replace('?', ''))
        
        if post is not None:
            comments = Comment.objects.filter(comment_Forum=post).order_by('created_at') # oldest to newest
            likes = Like.objects.filter(post=post)

            return render(request, 'forum/view.html', {'post': post, 'comments': comments, 'likes': likes, 'notifications': notifications})
        else:
            raise Http404
    else:
        # return 404
        raise Http404

def forum_Create(request):
    """Create post, if no request open page like usual. Request are made using jquery ajax
    
    Onsucess: Redirect to the post
    Onfail: Return error message
    """
    if request.user.is_authenticated:
        if request.method == 'POST': # If a request is made
            user = request.user
            title = request.POST.get('title')
            content = request.POST.get('content')
            tag_get = request.POST.get('tag')
            
            # Check if tag is found
            if tag_get is None:
                messages.info(request, 'Invalid tag options!')
                return HttpResponse('error')

            # Check tittle length
            if len(title) < 5:
                messages.info(request, 'Title is too short, Min title length is 5 characters')
                return HttpResponse('error')

            if len(title) > 200:
                messages.info(request, 'Title is too long, Max title length is 200 characters')
                return HttpResponse('error')

            # Check content length
            if len(content) < 25:
                messages.info(request, 'Content must be at least 25 characters!')
                return HttpResponse('limit')

            # Max 40k
            if len(content) > 40000:
                messages.info(request, 'Invalid content length! Max allowed are 40k including formatting')
                return HttpResponse('limit')

            # Check if tag is found
            tag = Tag.objects.get(name=tag_get)

            if tag is None:
                messages.info(request, 'Invalid tag options! No tag found!')
                return HttpResponse('error')

            post = Forum(title=title, content=content, user=user, tag=tag)
            post.save()

            # Return the post id
            getPost = Forum.objects.get(title=title, content=content, user=user)
            return HttpResponse(getPost.id)
        else: # user enter normally
            # if user is authenticated
            notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
            tags = Tag.objects.filter(type="Forum")
            return render(request, 'forum/create.html', {'tags': tags, 'notifications': notifications})
    else: # user is not logged in
        messages.info(request, 'Need to login first!')
        return redirect('/auth/login')

def forum_Edit(request, id, title):
    """Edit post, if no request open page like usual. Request are made using jquery ajax
    
    Onsucess: Redirect to the post
    Onfail: Return error message
    """
    # Check if user is logged in and it's the post owner
    if request.user != Forum.objects.get(id=id).user:
        raise PermissionDenied()

    if request.user.is_authenticated:
        if request.method == 'POST': # If an update is made
            # Can't change title
            content = request.POST.get('content') # content change
            tag_name = request.POST.get('tag') # if user change the tag, it will be changed

            if len(content) < 25:
                messages.info(request, 'Content must be at least 25 characters!')
                return HttpResponse('limit')

            # Max 40k
            if len(content) > 40000:
                messages.info(request, 'Invalid content length! Max allowed are 40k including formatting')
                return HttpResponse('limit')

            # Get the post and tag object
            post = Forum.objects.get(id=id)
            tag = Tag.objects.get(name=tag_name)

            # Change the stuff
            post.content = content
            post.tag = tag

            # Save
            post.save()

            # Redirect to the post
            return HttpResponse('success')
        else: # If user enter the edit page
            post = Forum.objects.get(id=id)
            tag = Tag.objects.filter(type="Forum")
            notifications = Notification.objects.filter(user=request.user).order_by('-created_at')

            if title.replace('-', ' ') != post.title: # Ensure the title is exactly the same
                return redirect('/forum/' + str(post.id) + '/' + post.title.replace(' ', '-') + '/edit')

            return render(request, 'forum/edit.html', {'post': post, 'tags': tag, 'notifications': notifications})
    else: # Double check, this shouldn't actually happen
        messages.info(request, 'Need to login first!')
        return HttpResponse('error')

def forum_Delete(request, id, title):
    """Delete a post. Only post request allowed, if no request throw 404. Request are made using jquery ajax
    
    onsuccess: Go to post home
    onfail: Alert fail using jquery
    """
    # Check if user is logged in and it's the post owner
    if request.method == 'POST': # If a request is made
        mode = request.POST.get('mode')
        user = request.user
        post = Forum.objects.get(id=id)

        if not user.is_superuser:
            if user != post.user:
                messages.info(request, 'Need to login first!')
                dataJson = {'status': 'error', 'message': 'Need to login first!'}
                return HttpResponse(json.dumps(dataJson))

        # If delete mode admin send notification to the user
        if mode == 'admin' and user.is_superuser:
            if post.user != None: # Check if post user's account still exist
                # Check if the deleted comment's user is admin, if admin then dont send notification
                if not post.user.is_superuser:
                    # Get reason for deletion by admin
                    reason = request.POST.get('reason')
                    # Send notification to user
                    notification = Notification(user=post.user, notification_Content='Your post has been deleted by admin (' + user.username + '). Reason: ' + reason)
                    notification.save()

        # Delete the post
        post.delete()

        # Return success
        dataJson = {'status': 'success', 'message': 'The post has been deleted successfully!'}
        return HttpResponse(json.dumps(dataJson))
    else: # If no request, throw 404
        raise Http404

def forum_Like(request, id, title):
    """Like post, if no request throw 404. Request are made using jquery ajax
    
    onsuccess: Use jquery to update the likes
    onfail: Alert fail using jquery
    """
    if request.method == 'POST':
        if request.user.is_authenticated:
            post = Forum.objects.get(id=id)
            user = request.user
            like = Like.objects.filter(user=user, post=post)
            if like.count() == 0: # If user hasn't liked this post
                like = Like(user=user, post=post)
                like.save()

                # Get amount of posts like
                likes = Like.objects.filter(post=post)
                jsonData = {'likes': likes.count()}

                # Increase the post likes
                post.likes += 1
                post.save()

                return HttpResponse(json.dumps(jsonData))
            else: # If user has liked this post
                like.delete()

                # Get amount of posts like
                likes = Like.objects.filter(post=post)
                jsonData = {'likes': likes.count()}

                # Decrease the post likes
                post.likes -= 1
                post.save()

                return HttpResponse(json.dumps(jsonData))
        else: # If user is not logged in
            jsonData = {'likes': 0}
            return HttpResponse(json.dumps(jsonData))
    else: # If no request, throw 404
        raise Http404

def forum_Report(request, id, title):
    if request.method == 'POST':
        if request.user.is_authenticated:
            # Report
            user = request.user
            post = Forum.objects.get(id=id)
            reason = request.POST.get('reason')

            # Validate reason
            if len(reason) < 4:
                messages.info(request, 'Invalid Reason Length! Min input are 4 characters')
                jsonData = {'status': 'limit', 'message': 'Reason inputted is too short (Min input are 4 characters)! '}
                return HttpResponse(json.dumps(jsonData))

            if len(reason) > 200:
                messages.info(request, 'Invalid Reason Length! Max input are 200 characters!')
                jsonData = {'status': 'limit', 'message': 'Reason inputted is too long (Max input are 200 characters)!'}
                return HttpResponse(json.dumps(jsonData))

            # Check if user has already reported this post
            report = Report.objects.filter(user=user, post=post)
            if report.count() == 0:
                report = Report(user=user, reportedUser=post.user, post=post, reason=reason, reportType='post')
                report.save()
                jsonData = {'status': 'success', 'message': 'Post has been reported successfully!'}
                return HttpResponse(json.dumps(jsonData))
            else:
                messages.info(request, 'You have already reported this post!')
                jsonData = {'status': 'error', 'message': 'You have already reported this post!'}
                return HttpResponse(json.dumps(jsonData))
        else:
            messages.info(request, 'Need to login first!')
            jsonData = {'status': 'error', 'message': 'Need to login first!'}
            return HttpResponse(json.dumps(jsonData))
    else:
        raise Http404

# ----------------------------------------------------------------
# Comment
def forum_Comment(request, id, title):
    """Comment on a post, if no request throw 404. Request are made using jquery ajax
    
    Onsucess: Refresh page / re-Load the page
    Onfail: Alert using jquery
    """
    if request.method == 'POST': # If a comment is made
        if request.user.is_authenticated:
            # Comment
            user = request.user
            post = Forum.objects.get(id=id)
            commentGet = request.POST.get('comment')

            # If comment empty
            if commentGet == None:
                messages.info(request, 'Invalid comment length!')
                return HttpResponse('error')

            # If comment too long or too short
            if len(commentGet) > 10000 or len(commentGet) < 20:
                messages.info(request, 'Invalid comment length!')
                return HttpResponse('limit')

            # Save comment first
            comment = Comment(user=user, comment_Forum=post, content=commentGet)
            comment.save()

            # Increase the post comments
            post.comments += 1
            post.save()

            # send notification to post owner
            if post.user != user:
                if post.user != None: # Check if post user's account still exist
                    notification = Notification(user=post.user, post_Forum=post, comment=comment, notification_Content=user.username + ' posted a comment on your post')
                    notification.save()

            # Send notification to mentioned users @
            mentioned = re.findall(r'@\w+', commentGet)
            # Remove dupe
            mentionedNoDupe = list(dict.fromkeys(mentioned))
            # Loop
            for mentionedUser in mentionedNoDupe:
                mentionedUser = mentionedUser[1:] # Remove @
                if mentionedUser != user.username:
                    try:
                        # Get the mentioned user object
                        mentionedUserObject = User.objects.get(username=mentionedUser)

                        # Get the comment object
                        mentionedComment = Comment.objects.get(user=user, comment_Forum=post, content=commentGet)
                    
                        notification = Notification(user=mentionedUserObject, comment=mentionedComment, post_Forum=post, notification_Content=user.username + ' mentioned you in a comment')
                        notification.save()
                    except:
                        continue

            return HttpResponse('success')
        else: # If user is not logged in
            messages.info(request, 'Need to login first!')
            return HttpResponse('error')
    else: # If no request, throw 404
        raise Http404

def forum_Comment_Like(request, id, title, comment_id):
    """Like a comment, if no request throw 404. Request are made using jquery ajax
    
    onsuccess: Use jquery to update the likes
    onfail: Alert fail using jquery
    """
    if request.method == 'POST':
        if request.user.is_authenticated:
            comment = Comment.objects.get(id=comment_id)
            user = request.user
            post = Forum.objects.get(id=id)
            like = Like.objects.filter(user=user, comment=comment)

            if like.count() == 0: # If user hasn't liked this comment
                like = Like(user=user, comment=comment, post=post)
                like.save()

                # Get amount of comments like
                likes = Like.objects.filter(comment=comment)
                jsonData = {'likes': likes.count()}

                # Increase the comment likes
                comment.likes += 1
                comment.save()

                return HttpResponse(json.dumps(jsonData))
            else: # If user has liked this comment
                like.delete()

                # Get amount of comments like
                likes = Like.objects.filter(comment=comment)
                jsonData = {'likes': likes.count()}

                # Decrease the comment likes
                comment.likes -= 1
                comment.save()

                return HttpResponse(json.dumps(jsonData))
        else: # If user is not logged in
            jsonData = {'likes': 0, 'names': 'error'}
            return HttpResponse(json.dumps(jsonData))
    else: # If no request, throw 404
        raise Http404

def forum_Comment_Edit(request, id, title, comment_id):
    """Edit a comment, if no request throw 404. Request are made using jquery ajax
    
    onsuccess: Use jquery to update the comment
    onfail: Alert fail using jquery
    """
    # Check if a post request is made
    if request.method == 'POST':
        if request.user.is_authenticated:
            comment = Comment.objects.get(id=comment_id)
            user = request.user
            commentGet = request.POST.get('comment')

            # Check length of comment
            if len(commentGet) > 10000 or len(commentGet) < 20:
                messages.info(request, 'Invalid comment length!')
                return HttpResponse('limit')

            # If comment empty
            if commentGet == None:
                messages.info(request, 'Invalid comment length!')
                return HttpResponse('error')

            # Edit comment
            comment.content = commentGet
            comment.save()

            return HttpResponse('success')
        else: # If user is not logged in
            messages.info(request, 'Need to login first!')
            return HttpResponse('error')
    else: # If no request, throw 404
        raise Http404

def forum_Comment_Delete(request, id, title, comment_id):
    """Delete a comment, if no request throw 404. Request are made using jquery ajax
    
    onsuccess: Use jquery to update the comment
    onfail: Alert fail using jquery
    """
    # Check if a post request is made
    if request.method == 'POST':
        if request.user.is_authenticated:
            post = Forum.objects.get(id=id)
            comment = Comment.objects.get(id=comment_id)
            user = request.user
            mode = request.POST.get('mode')

            # Verify if the user is the comment owner
            if not user.is_superuser:
                if user != comment.user:
                    raise PermissionDenied()

            # If delete mode admin send notification to the user
            if mode == 'admin' and user.is_superuser:
                if comment.user != None: # Check if post user's account still exist
                    # Check if the deleted comment's user is admin, if admin then dont send notification
                    if not comment.user.is_superuser:
                        # Get reason for deletion by admin
                        reason = request.POST.get('reason')
                        # Send notification to user
                        notification = Notification(user=comment.user, notification_Content='Your comment has been deleted by admin (' + user.username + '). Reason: ' + reason)
                        notification.save()

            # Delete comment
            comment.delete()

            # Decrease the post comments
            post.comments -= 1
            post.save()

            # Get current comment count
            comments = Comment.objects.filter(comment_Forum=comment.comment_Forum)
            dataJson = {'status': 'success', 'message': comments.count()}
            return HttpResponse(json.dumps(dataJson))
        else: # If user is not logged in
            messages.info(request, 'Need to login first!')
            dataJson = {'status': 'error', 'message': 'Need to login first!'}
            return HttpResponse(json.dumps(dataJson))
    else: # If no request, throw 404
        raise Http404

def forum_Comment_Report(request, id, title, comment_id):
    """Report a comment, if no request throw 404. Request are made using jquery ajax
    
    onsuccess: Tell report success using jquery
    onfail: Alert fail using jquery
    """
    # Check if a post request is made
    if request.method == 'POST':
        if request.user.is_authenticated:
            comment = Comment.objects.get(id=comment_id)
            user = request.user
            reason = request.POST.get('reason')

            # Validate reason
            if len(reason) < 4:
                messages.info(request, 'Invalid Reason Length! Min input are 4 characters')
                jsonData = {'status': 'limit', 'message': 'Reason inputted is too short (Min input are 4 characters)! '}
                return HttpResponse(json.dumps(jsonData))

            if len(reason) > 200:
                messages.info(request, 'Invalid Reason Length! Max input are 200 characters!')
                jsonData = {'status': 'limit', 'message': 'Reason inputted is too long (Max input are 200 characters)!'}
                return HttpResponse(json.dumps(jsonData))

            # Check if user has already reported this comment
            report = Report.objects.filter(user=user, comment=comment)
            # If have not reported this comment
            if report.count() == 0:                
                # Report comment
                report = Report(user=user, reportedUser=comment.user, comment=comment, reason=reason, reportType='comment')
                report.save()

                # Get amount of reports
                reports = Report.objects.filter(comment=comment)
                dataJson = {'status': 'success', 'message': reports.count()}
                return HttpResponse(json.dumps(dataJson))
            else: # If user has already reported this comment
                dataJson = {'status': 'error', 'message': 'You have already reported this comment!'}
                return HttpResponse(json.dumps(dataJson))
        else: # If user is not logged in
            messages.info(request, 'Need to login first!')
            dataJson = {'status': 'error', 'message': 'Need to login first!'}
            return HttpResponse(json.dumps(dataJson))
    else: # If no request, throw 404
        raise Http404

# ----------------------------------------------------------------
# Profile
def profile(request, username):
    """See a user's profile"""
    try:
        # get the user profile
        user = User.objects.get(username=username)

        user_profile = UserProfile.objects.get(user=user)
        
        # get the user posts
        posts = Forum.objects.filter(user=user)

        # get the user comments
        comments = Comment.objects.filter(user=user)

        # if user is authenticated
        if request.user.is_authenticated:
            # Get user's notification
            notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
        else:
            notifications = None

        return render(request, 'profile/index.html', {'theUser': user, 'user_profile': user_profile, 'posts': posts, 'comments': comments, 'notifications': notifications})
    except:
        raise Http404

def profile_Posts(request, username):
    """Get all posts of a user"""
    try:
        user = User.objects.get(username=username)

        # get the user posts 25 per page
        paginator = Paginator(Forum.objects.filter(user=user).order_by('-created_at'), 25)
        page = request.GET.get('page')
        posts = paginator.get_page(page)

        # if user is authenticated
        if request.user.is_authenticated:
            # Get user's notification
            notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
        else:
            notifications = None

        return render(request, 'profile/posts.html', {'theUser': user, 'posts': posts, 'notifications': notifications})
    except:
        raise Http404

def profile_Konsultasi(request, username):
    """Get all posts of a user"""
    try:
        # get the user profile
        user = User.objects.get(username=username)

        # get the user posts 25 per page
        paginator = Paginator(Konsultasi.objects.filter(user=user).order_by('-created_at'), 25)
        page = request.GET.get('page')
        posts = paginator.get_page(page)

        # if user is authenticated
        if request.user.is_authenticated:
            # Get user's notification
            notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
        else:
            notifications = None

        return render(request, 'profile/konsultasi.html', {'theUser': user, 'post_konsul': posts, 'notifications': notifications})
    except:
        raise Http404
    

def profile_Comments(request, username):
    """Get all comments of a user"""
    try:
        # get the user profile
        user = User.objects.get(username=username)

        # get the user comments 25 per page
        paginator = Paginator(Comment.objects.filter(user=user).order_by('-created_at'), 25)
        page = request.GET.get('page')
        comments = paginator.get_page(page)

        # if user is authenticated
        if request.user.is_authenticated:
            # Get user's notification
            notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
        else:
            notifications = None

        return render(request, 'profile/comments.html', {'theUser': user, 'comments': comments, 'notifications': notifications})
    except:
        raise Http404

# INi buat apaan ya??? kaga kepake gw lupa dulu mau bakal apa, tp di keep aja dulu mungkin
# def profile_Liked_Commented_Posts(request, username):
#     """Get all liked and commented posts of a user"""
#     try:
#         # get the user profile
#         user = User.objects.get(username=username)

#         # Get user liked or commented posts
#         liked_posts = Like.objects.filter(user=user).order_by('-created_at')
#         commented_posts = Comment.objects.filter(user=user).order_by('-created_at')
#         combined_Liked_Commented_Posts = list(chain(liked_posts, commented_posts))

#         # 
#         paginator = Paginator(combined_Liked_Commented_Posts, 25)
#         page = request.GET.get('page')
#         liked_Commented_Posts = paginator.get_page(page)

#         return render(request, 'profile/liked-commented-posts.html', {'theUser': user, 'liked_Commented_Posts': liked_Commented_Posts, 'test': combined_Liked_Commented_Posts})


#         # Combine them both into one object
        
#         # return render(request, 'profile/liked_commented_posts.html', {'theUser': user, 'liked_posts': liked_posts, 'commented_posts': commented_posts})
#     except:
#         raise Http404

def profile_Settings(request, username):
    """User profile settings
    if a posts request is made, it means that the user is trying to update his profile
    """
    if request.user.is_authenticated:
        if username == request.user.username: # If user is logged in and username is the same
            if request.method == 'POST': # If request is made using post
                user = User.objects.get(username=request.user.username)
                user.first_name = request.POST.get('firstName')
                user.last_name = request.POST.get('lastName')

                # No changing email
                # user.email = request.POST.get('email')

                # # Check email
                # regex = "[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,4}$"
                # if not re.search(regex, user.email) or len(user.email) < 3:
                #     messages.info(request, 'Invalid email address!')
                #     return redirect('/auth/register')

                # User profile
                user_Profile = UserProfile.objects.get(user=user)
                user_Profile.bio = request.POST.get('bio')
                user_Profile.location = request.POST.get('location')
                # user_Profile.img_url = request.POST.get('img')

                # Check bio limit 500 characters
                if len(user_Profile.bio) > 500:
                    messages.info(request, 'Bio to long! Max length is 500 characters')
                    return redirect('/profile/' + user.username + '/settings')

                # Check location limit 250 characters
                if len(user_Profile.location) > 250:
                    messages.info(request, 'Location too long! Max length is 250 characters')
                    return redirect('/profile/' + user.username + '/settings')  

                # Check image url ???
                # if user_Profile.img_url != '':
                #     if not user_Profile.img_url.startswith('https'):
                #         messages.info(request, 'Invalid image url! Image must be secured with https')
                #         return redirect('/profile/' + user.username + '/settings')

                # Save
                user.save()
                user_Profile.save()

                messages.info(request, 'Profile updated successfully!')
                return redirect('/profile/' + user.username + '/settings')
            else: # If Open normally
                notifications = Notification.objects.filter(user=request.user).order_by('-created_at')

                return render(request, 'profile/settings.html', {'UserProfile': UserProfile.objects.get(user=request.user), 'notifications': notifications})
        else: # If not the user
            raise PermissionDenied()
    else: # If user is not logged in
        messages.info(request, 'You have to be logged in first!')
        return render(request, 'auth/login')

def profile_Notification(request, username):
    """User profile notification"""
    if request.user.is_authenticated:
        if username == request.user.username:
            notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
            return render(request, 'profile/notification.html', {'notifications': notifications})
        else:
            raise PermissionDenied()
    else:
        messages.info(request, 'You have to be logged in first!')
        return render(request, 'auth/login')

def profile_Notification_Read(request, username, notification_id):
    """User profile notification read
    
    onsuccess: Mark comment as read
    onfail: Alert fail
    """
    if request.method == 'POST':
        if username == request.user.username:
            # Get the notification
            notification = Notification.objects.get(id=notification_id)

            # Mark as read
            notification.read = True
            notification.save()

            return HttpResponse(json.dumps({'status': 'success'}))
        else:
            raise PermissionDenied()
    else:
        raise Http404

def profile_Notification_Readall(request, username):
    """User profile notification read all
    
    onsuccess: Mark all comment as read
    onfail: Alert fail
    """
    if request.method == 'POST':
        if username == request.user.username:
            # Mark all notifications as read
            Notification.objects.filter(user=request.user).update(read=True)

            return HttpResponse(json.dumps({'status': 'success'}))
        else:
            raise PermissionDenied()
    else:
        raise Http404

def profile_history(request, username):
    """User History"""
    if username == request.user.username:
        # Check if there is a post request to delete a history
        if request.method == 'POST':
            # Get the history
            history = History.objects.get(id=request.POST.get('history_id'))

            # Delete the history
            history.delete()

            return HttpResponse(json.dumps({'status': 'success'}))
        else:
            user = User.objects.get(username=username)
            history = History.objects.filter(user=user).order_by('-created_at')
            notifications = Notification.objects.filter(user=request.user).order_by('-created_at')

            return render(request, 'profile/history.html', {'theUser': user, 'history': history, 'notifications': notifications})
    else:
        raise PermissionDenied()

# ----------------------------------------------------------------
# Report
def report(request):
    """Open reports view, admin only"""
    if request.user.is_superuser:
        # Get reqeuest split reports to 25 per page
        paginator = Paginator(Report.objects.all().order_by('-created_at'), 25)
        page = request.GET.get('page')
        reports = paginator.get_page(page)
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')

        return render(request, 'report.html', {'reportsPaged': reports, 'notifications': notifications})
    else:
        raise PermissionDenied()

def report_Resolve(request, id):
    """Resolve report, admin only"""
    if request.method == 'POST':
        if request.user.is_superuser:
            # Get report
            report = Report.objects.get(id=id)

            # Check if already resolved or not, if not resolved make resolved, if resolved make unresolved
            if report.isResolved == False:
                report.isResolved = True
                report.save()
                dataJson = {'status': 'success', 'isResolved': True}
                return HttpResponse(json.dumps(dataJson))
            else:
                report.isResolved = False
                report.save()
                dataJson = {'status': 'success', 'isResolved': False}
                return HttpResponse(json.dumps(dataJson))
        else:
            raise PermissionDenied()
    else:
        raise Http404

# ----------------------------------------------------------------
# Konsul
def konsultasi(request):
    """Open konsultasi view"""
    # if user is authenticated
    if request.user.is_authenticated:
        # Get user's notification
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    else:
        notifications = None
    tags = Tag.objects.filter(type="Konsultasi")
    searching = False
    q = None
    # Check if there is a search
    if request.GET.get('q'):
        query = request.GET.get('q')
        paginator = Paginator(Konsultasi.objects.filter(title__icontains=query).order_by('-created_at'), 25)
        page = request.GET.get('page')
        konsultasi = paginator.get_page(page)
        searching = True
        q = query

        # Check if no result found
        if paginator.count == 0:
            messages.info(request, 'No result found')
            return redirect('/konsultasi')
    else:
        paginator = Paginator(Konsultasi.objects.all().order_by('-created_at'), 25)
        page = request.GET.get('page')
        konsultasi = paginator.get_page(page)

    return render(request, 'konsultasi/index.html', {'post_konsul': konsultasi, 'tags': tags, 'searching': searching, 'notifications': notifications, 'q': q})

def konsultasi_Create(request):
    """Create post, if no request open page like usual. Request are made using jquery ajax
    
    Onsucess: Redirect to the post
    Onfail: Return error message
    """
    if request.user.is_authenticated:
        if request.method == 'POST': # If a request is made
            user = request.user
            title = request.POST.get('title')
            content = request.POST.get('content')
            tag_get = request.POST.get('tag')
            
            # Check if tag is found
            if tag_get is None:
                messages.info(request, 'Invalid tag options!')
                return HttpResponse('error')

            # Check tittle length
            if len(title) < 5:
                messages.info(request, 'Title is too short, Min title length is 5 characters')
                return HttpResponse('error')

            if len(title) > 200:
                messages.info(request, 'Title is too long, Max title length is 200 characters')
                return HttpResponse('error')

            # Check content length
            if len(content) < 25:
                messages.info(request, 'Content must be at least 25 characters!')
                return HttpResponse('limit')

            # Max 40k
            if len(content) > 40000:
                messages.info(request, 'Invalid content length! Max allowed are 40k including formatting')
                return HttpResponse('limit')

            # Check if tag is found
            tag = Tag.objects.get(name=tag_get)

            if tag is None:
                messages.info(request, 'Invalid tag options! No tag found!')
                return HttpResponse('error')

            post = Konsultasi(title=title, content=content, user=user, tag=tag)
            post.save()

            # Return the post id
            getPost = Konsultasi.objects.get(title=title, content=content, user=user)
            return HttpResponse(getPost.id)
        else: # user enter normally
            tags = Tag.objects.filter(type="Konsultasi")
            notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
            return render(request, 'konsultasi/create.html', {'tags': tags, 'notifications': notifications})
    else: # user is not logged in
        messages.info(request, 'Need to login first!')
        return redirect('/auth/login')

def konsultasi_Tag(request, tagName):
    """Open konsultasi tag view"""
    tag = Tag.objects.get(name=tagName.replace('-', ' '))
    if tag is not None and tag.type == "Konsultasi":
        paginator = Paginator(Konsultasi.objects.filter(tag=tag).order_by('-created_at'), 25)
        page = request.GET.get('page')
        posts = paginator.get_page(page)
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
        return render(request, 'konsultasi/tag.html', {'post_konsul': posts, 'tag': tag, 'notifications': notifications})
    else:
        raise Http404

def konsultasi_Delete(request, id, title):
    """Delete konsultasi"""
        # Check if user is logged in and it's the post owner
    if request.method == 'POST': # If a request is made
        mode = request.POST.get('mode')
        user = request.user
        konsultasi = Konsultasi.objects.get(id=id)

        if not user.is_superuser:
            if user != konsultasi.user:
                messages.info(request, 'Need to login first!')
                dataJson = {'status': 'error', 'message': 'Need to login first!'}
                return HttpResponse(json.dumps(dataJson))

        # If delete mode admin send notification to the user
        if mode == 'admin' and user.is_superuser:
            if konsultasi.user != None: # Check if post user's account still exist
                # Check if the deleted comment's user is admin, if admin then dont send notification
                if not konsultasi.user.is_superuser:
                    reason = request.POST.get('reason')

                    # Kirim notif ke user
                    user = konsultasi.konsultasi_User
                    message = "Konsultasi anda dengan judul '" + konsultasi.konsultasi_Title + "' telah dihapus oleh admin. Alasan: " + reason
                    notification = Notification(user=user, notification_content=message)
                    notification.save()

        # Delete the post
        konsultasi.delete()

        # Return success
        dataJson = {'status': 'success', 'message': 'Konsultasi berhasil dihapus!'}
        return HttpResponse(json.dumps(dataJson))
    else:
        raise Http404

def konsultasi_Url(request, id, title):
    """Open konsultasi detail view"""
    # Title in the link is just for vanity url
    if id is not None and title is not None:
        konsultasi = Konsultasi.objects.get(id=id)
        # if user is authenticated
        if request.user.is_authenticated:
            # Get user's notification
            notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
        else:
            notifications = None
        # To ensure the vanity url is always exactly the title
        if title.replace('-', ' ') != konsultasi.title.replace('?', ''):
            return redirect('/konsultasi/' + str(konsultasi.id) + '/' + konsultasi.title.replace(' ', '-').replace('?', ''))
        
        if konsultasi is not None:
            comments = Comment.objects.filter(comment_Konsultasi=konsultasi).order_by('created_at') # oldest to newest

            return render(request, 'konsultasi/view.html', {'post': konsultasi, 'comments': comments, 'notifications': notifications})
        else:
            raise Http404
    else:
        # return 404
        raise Http404

def konsultasi_Content(request, id):
    """Open konsultasi detail view"""
    if id is not None:
        try:
            konsultasi = Konsultasi.objects.get(id=id)
        except:
            raise Http404

        return redirect('/konsultasi/' + str(konsultasi.id) + '/' + konsultasi.title.replace(' ', '-'))
    else:
        # return 404
        raise Http404

def konsultasi_Comment(request, id, title):
    """Create konsultasi comment"""
    if request.method == 'POST': # If a comment is made
        if request.user.is_authenticated:
            print('a')
            # Comment
            user = request.user
            post = Konsultasi.objects.get(id=id)
            print(post)
            commentGet = request.POST.get('comment')

            # If comment empty
            if commentGet == None:
                messages.info(request, 'Invalid comment length!')
                return HttpResponse('error')

            # If comment too long or too short
            if len(commentGet) > 10000 or len(commentGet) < 20:
                messages.info(request, 'Invalid comment length!')
                return HttpResponse('limit')

            # Save comment first
            comment = Comment(user=user, comment_Konsultasi=post, content=commentGet)
            comment.save()

            # Increase the post comments
            post.comments += 1
            post.save()

            # send notification to post owner
            if post.user != user:
                if post.user != None: # Check if post user's account still exist
                    notification = Notification(user=post.user, post_Konsultasi=post, comment=comment, notification_Content=user.username + ' posted a comment on your post')
                    notification.save()

            # Send notification to mentioned users @
            mentioned = re.findall(r'@\w+', commentGet)
            # Remove dupe
            mentionedNoDupe = list(dict.fromkeys(mentioned))
            # Loop
            for mentionedUser in mentionedNoDupe:
                mentionedUser = mentionedUser[1:] # Remove @
                if mentionedUser != user.username:
                    try:
                        # Get the mentioned user object
                        mentionedUserObject = User.objects.get(username=mentionedUser)

                        # Get the comment object
                        mentionedComment = Comment.objects.get(user=user, comment_Konsultasi=post, content=commentGet)
                    
                        notification = Notification(user=mentionedUserObject, comment=mentionedComment, post_Konsultasi=post, notification_Content=user.username + ' mentioned you in a comment')
                        notification.save()
                    except:
                        continue

            return HttpResponse('success')
        else: # If user is not logged in
            messages.info(request, 'Need to login first!')
            return HttpResponse('error')
    else: # If no request, throw 404
        raise Http404

def konsultasi_Comment_Delete(request, id, title, comment_id):
    """Delete konsultasi comment"""
        # Check if a post request is made
    if request.method == 'POST':
        if request.user.is_authenticated:
            post = Konsultasi.objects.get(id=id)
            comment = Comment.objects.get(id=comment_id)
            user = request.user
            mode = request.POST.get('mode')

            # Verify if the user is the comment owner
            if not user.is_superuser:
                if user != comment.user:
                    raise PermissionDenied()

            # If delete mode admin send notification to the user
            if mode == 'admin' and user.is_superuser:
                if comment.user != None: # Check if post user's account still exist
                    # Check if the deleted comment's user is admin, if admin then dont send notification
                    if not comment.user.is_superuser:
                        # Get reason for deletion by admin
                        reason = request.POST.get('reason')
                        # Send notification to user
                        notification = Notification(user=comment.user, notification_Content='Your comment has been deleted by admin (' + user.username + '). Reason: ' + reason)
                        notification.save()

            # Delete comment
            comment.delete()

            # Decrease the post comments
            post.comments -= 1
            post.save()

            # Get current comment count
            comments = Comment.objects.filter(comment_Konsultasi=comment.comment_Konsultasi)
            dataJson = {'status': 'success', 'message': comments.count()}
            return HttpResponse(json.dumps(dataJson))
        else: # If user is not logged in
            messages.info(request, 'Need to login first!')
            dataJson = {'status': 'error', 'message': 'Need to login first!'}
            return HttpResponse(json.dumps(dataJson))
    else: # If no request, throw 404
        raise Http404

def konsultasi_Comment_Edit(request, id, title, comment_id):
    """Edit konsultasi comment"""
    # Check if a post request is made
    if request.method == 'POST':
        if request.user.is_authenticated:
            comment = Comment.objects.get(id=comment_id)
            user = request.user
            commentGet = request.POST.get('comment')

            # Check length of comment
            if len(commentGet) > 10000 or len(commentGet) < 20:
                messages.info(request, 'Invalid comment length!')
                return HttpResponse('limit')

            # If comment empty
            if commentGet == None:
                messages.info(request, 'Invalid comment length!')
                return HttpResponse('error')

            # Edit comment
            comment.content = commentGet
            comment.save()

            return HttpResponse('success')
        else: # If user is not logged in
            messages.info(request, 'Need to login first!')
            return HttpResponse('error')
    else: # If no request, throw 404
        raise Http404

# ----------------------------------------------------------------
# Tests menu
def tests(request):
    """Tests menu"""
    # if user is authenticated
    if request.user.is_authenticated:
        # Get user's notification
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    else:
        notifications = None
    return render(request, 'tests/index.html', {'notifications': notifications})

# ------------------------------
# Test Loneliness
def test_Loneliness(request):
    """Tes Skala Kesepian"""
    # if user is authenticated
    if request.user.is_authenticated:
        # Get user's notification
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    else:
        notifications = None
    return render(request, 'tests/health/loneliness/index.html', {'notifications': notifications})

def test_Loneliness_Question(request):
    """Halaman pertanyaan Tes Skala Kesepian"""
    # if user is authenticated
    if request.user.is_authenticated:
        # Get user's notification
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    else:
        notifications = None
    return render(request, 'tests/health/loneliness/question.html', {'notifications': notifications})

def test_Loneliness_Result(request):
    """Halaman hasil Tes Skala Kesepian"""
    # Check if there is post request
    if request.method == 'POST':
        # Get score
        score_Kesepian = int(request.POST.get('score_kesepian'))
        score_Sosial = int(request.POST.get('score_sosial'))
        user = request.user

        # Kesepian
        kesepian = 0
        # 1 = tidak kesepian
        # 2 = kesepian
        # 3 = sangat kesepian

        if 12 <= score_Kesepian <= 24:
            kesepian = 1
        elif 25 <= score_Kesepian <= 36:
            kesepian = 2
        elif 37 <= score_Kesepian <= 48:
            kesepian = 3
        
        # Sosial
        sosial = 0
        # 1 = penuh dukungan sosial
        # 2 = kurang dukungan sosial
        # 3 = sangat kurang dukungan sosial

        if 13 <= score_Sosial <= 25:
            sosial = 1
        elif 26 <= score_Sosial <= 37:
            sosial = 2
        elif 38 <= score_Sosial <= 52:
            sosial = 3
        
        # Result
        # 1 2 == 1 3
        # 2 1 == 3 1
        # 2 2 == 2 3
        # 3 2 == 3 3 
        if (kesepian == 1 and sosial == 1): # 1 1 
            resultKey = 1
            resultType = "Tidak mengalami kesepian dan Penuh dukungan sosial"
        elif (kesepian == 1 and sosial == 2): # 1 2
            resultKey = 2
            resultType = "Tidak mengalami kesepian. Namun, Kurang dukungan sosial"
        elif (kesepian == 1 and sosial == 3): # 1 3
            resultKey = 2
            resultType = "Tidak mengalami kesepian. Namun, Sangat kurang dukungan sosial"
        elif (kesepian == 2 and sosial == 1): # 2 1
            resultKey = 3
            resultType = "Penuh dukungan sosial. Namun, Kesepian"
        elif (kesepian == 2 and sosial == 2): # 2 2
            resultKey = 4
            resultType = "Kesepian dan Kurang dukungan sosial"
        elif (kesepian == 2 and sosial == 3): # 2 3
            resultKey = 4
            resultType = "Kesepian dan Sangat kurang dukungan sosial"
        elif (kesepian == 3 and sosial == 1): # 3 1
            resultKey = 3
            resultType = "Penuh dukungan sosial. Nammun, Sangat kesepian"
        elif (kesepian == 3 and sosial == 2): # 3 2
            resultKey = 5
            resultType = "Sangat kesepian dan Kurang dukungan sosial"
        elif (kesepian == 3 and sosial == 3): # 3 3
            resultKey = 5
            resultType = "Sangat kesepian dan Sangat kurang dukungan sosial"
        else:
            resultKey = 0
            resultType = "Error!"

        result_data = {
            0: "Error, harap coba lagi! Jika masih error harap hubungi admin",
            # Tidak kesepian, penuh dukungan sosial
            1: "Berdasarkan jawaban Kamu, dapat disimpulkan bahwa untuk saat ini Kamu tidak mengalami kesepian dan juga mendapat dukungan sosial yang penuh. Untuk itu, tetap pertahankan ya! Masih banyak lingkungan pertemanan yang belum Kamu explore dan juga masih banyak lagi dukungan sosial yang akan Kamu dapatkan kedepannya. Semangat!",
            # Tidak kesepian, kurang dukungan sosial atau sangat kurang dukungan sosial
            2: "Berdasarkan jawaban Kamu, dapat disimpulkan bahwa untuk saat ini Kamu tidak mengalami kesepian namun (kurang/sangat kurang) akan dukungan sosial. Untuk itu, cobalah untuk percaya kepada teman-teman mu sehingga temanmu juga akan begitu, yang nantinya kalian akan bisa bersama-sama saling memberi dukungan. Sehingga, dengan adanya dukungan sosial yang penuh, bisa menjadikan kamu tidak akan pernah merasa kesepian dikarenakan kasih sayang dan perhatian yang Kamu dapatkan dari mereka. Jadi, teruslah semangat ya!",
            # Kesepian atau sangat kesepian, penuh dukungan sosial
            3: "Berdasarkan jawaban Kamu, dapat disimpulkan bahwa untuk saat ini Kamu mengalami (kesepian/sangat kesepian) namun penuh akan dukungan sosial. Untuk itu, cobalah renungkan apa yang menjadi penyebab utama kesepian mu saat ini. Dengan begitu, kamu akan tahu sendiri bagaimana cara mengatasi kesepian yang kamu hadapi dengan cara dan versi mu sendiri. Sehingga diharapkan, dengan adanya dukungan sosial yang penuh, bisa menjadikan kamu tidak merasa kesepian lagi karena masih banyak orang yang sayang dan perhatian kepadamu, tapi mungkin Kamu belum menyadari hal itu. Jadi, tetap semangat ya!",
            # kesepian dan kurang dukungan sosial
            4: "Berdasarkan jawaban Kamu, dapat disimpulkan bahwa untuk saat ini Kamu sedang mengalami kesepian dan juga kurang akan dukungan sosial. Untuk itu, cobalah membuka diri untuk beradaptasi dan berinteraksi pada lingkungan pertemanan mu dan juga coba untuk percaya kepada teman-teman mu sehingga temanmu juga akan begitu, yang nantinya kalian akan bisa bersama-sama saling memberi dukungan. Jadi, apapun keadaanmu sekarang jangan sampai membuat mu putus asa akan kehidupan ya. Masih ada waktu untuk mu memperbaiki keadaan. Semangat!",
            # sangat kesepian dan sangat kurang dukungan sosial
            5: "Berdasarkan jawaban Kamu, dapat disimpulkan bahwa untuk saat ini Kamu sangat kesepian dan juga sangat kurang akan dukungan sosial. Untuk itu, cobalah untuk membuka diri, beradaptasi, dan berinteraksi pada lingkungan pertemanan mu dan juga coba untuk percaya kepada teman-teman mu sehingga temanmu juga akan begitu, yang nantinya kalian akan bisa bersama-sama saling memberi dukungan. Jadi, apapun keadaanmu sekarang jangan sampai membuat mu putus asa akan kehidupan ya. Masih ada waktu untuk mu memperbaiki keadaan. Kami tahu ini bukanlah hal yang mudah, tapi Kami juga yakin Kamu pasti bisa. Semangat!"
        }
        # Save to history if user is logged in
        if request.user.is_authenticated:
            # Save to history
            history = History(user=user, quiz_type='Tes Skala Kesepian', res_type=resultType, res_data=result_data[resultKey])
            history.save()
        
            notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
        else:
            notifications = None
        # Nanti bisa di return banyak, style json -> title, hasil text, apa2 lah
        return render(request, 'tests/result.html', {'res_type': resultType, 'res_data': result_data[resultKey], 'notifications': notifications, 'quiz_type': 'Test Skala Kesepian'})
    else:
        messages.info(request, 'Silahkan test terlebih dahulu!')        
        return redirect('/tests')

# ------------------------------
# Test Depression
def test_Depression(request):
    """Test Depression"""
    # if user is authenticated
    if request.user.is_authenticated:
        # Get user's notification
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    else:
        notifications = None
    return render(request, 'tests/health/depression/index.html', {'notifications': notifications})

def test_Depression_Question(request):
    """Halaman pertanyaan Test Depression"""
    # if user is authenticated
    if request.user.is_authenticated:
        # Get user's notification
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    else:
        notifications = None
    return render(request, 'tests/health/depression/question.html', {'notifications': notifications})

def test_Depression_Result(request):
    """Halaman hasil Test Depression"""
    # Check if there is post request
    if request.method == 'POST':
        # Get score
        score = int(request.POST.get('score'))
        user = request.user

        if 20 <= score <= 49:
            resultKey = 1
            resultType = "Tidak mengalami depresi"
        elif 50 <= score <= 59:
            resultKey = 2
            resultType = "Mengalami sedikit depresi"
        elif 60 <= score <= 69:
            resultKey = 3
            resultType = "Mengalami tingkat depresi yang cukup tinggi"
        elif 70 <= score <= 80:
            resultKey = 4
            resultType = "Mengalami tingkat depresi yang tinggi"
        else:             
            resultKey = 0
            resultType = "Error!"

        result_data = {
            0: "Error, harap coba lagi! Jika masih error harap hubungi admin",
            # Tidak mengalami depresi
            1: "Berdasarkan jawaban kamu, dapat disimpulkan bahwa untuk saat ini kamu tidak mengalami depresi. Hal yang bagus! Untuk itu, tetap pertahankan ya! Masih banyak kesenangan yang bisa kamu lakukan dan bisa datang ke kamu. Jangan berpikir rendah tentang dirimu, ya. Semangat!",
            # Mengalami sedikit depresi
            2: "Berdasarkan jawaban kamu, dapat disimpulkan bahwa untuk saat ini kamu mengalami sedikit depresi. Untuk itu, cobalah kembali melakukan hal yang kamu suka dan jangan menyalahkan dirimu akan setiap hal buruk yang terjadi. Apapun keadaanmu sekarang, jangan sampai membuatmu putus asa akan kehidupan, ya. Masih ada waktu untukmu kembali menjadi individu yang memiliki harapan. Semangat!",
            # Mengalami depresi yang cukup tinggi
            3: "Berdasarkan jawaban kamu, dapat disimpulkan bahwa untuk saat ini kamu mengalami tingkat depresi yang cukup tinggi. Untuk itu, cobalah membuka hidup baru dengan menjauhkan hal-hal yang membuatmu merasa sedih dan terganggu, dan lanjutkan hidupmu yang ceria dan penuh tawa. Jauhkan pula dirimu dari lingkungan yang tidak sehat bagimu. Kelilingi dirimu dengan orang-orang baik yang akan mendukungmu dengan pilihan terbaik. Kami yakin bahwa kamu bisa melewati fase ini. Semangat!",
            # Mengalami depresi yang tinggi
            4: "Berdasarkan jawaban kamu, dapat disimpulkan bahwa untuk saat ini kamu mengalami tingkat depresi yang tinggi. Untuk itu, cobalah renungkan apa yang menjadi penyebab utama yang memicu rasa depresimu saat ini. Dengan begitu, kamu akan mengetahui bagaimana cara mengatasi depresi yang kamu hadapi dengan cara dan versimu sendiri. Sehingga diharapkan, dengan adanya perubahan cara hidup, bisa menjadikan kamu tidak merasa depresi lagi karena masih banyak bagian dari dunia ini yang akan merasa bahagia dengan kehadiranmu. Mungkin untuk saat ini, kamu belum bisa merasakan bahwa kamu berguna bagi banyak orang. Kami yakin bahwa kamu bisa melewati fase ini. Senyumlah dan tetap semangat!",
        }

        # Save to history if user is logged in
        if request.user.is_authenticated:
            # Save to history
            history = History(user=user, quiz_type='Test Depresi', res_type=resultType, res_data=result_data[resultKey])
            history.save()
        
            notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
        else:
            notifications = None
        # Nanti bisa di return banyak, style json -> title, hasil text, apa2 lah
        return render(request, 'tests/result.html', {'res_type': resultType, 'res_data': result_data[resultKey], 'notifications': notifications, 'quiz_type': 'Test Depresi'})
    else:
        messages.info(request, 'Silahkan test terlebih dahulu!')        
        return redirect('/tests')

# ------------------------------
# Test Kesadaran
def test_Mindfulness(request):
    """Test Kesadaran"""
    # if user is authenticated
    if request.user.is_authenticated:
        # Get user's notification
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    else:
        notifications = None
    return render(request, 'tests/health/mindfulness/index.html', {'notifications': notifications})

def test_Mindfulness_Question(request):
    """Halaman pertanyaan Test Kesadaran"""
    # if user is authenticated
    if request.user.is_authenticated:
        # Get user's notification
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    else:
        notifications = None
    return render(request, 'tests/health/mindfulness/question.html', {'notifications': notifications})

def test_Mindfulness_Result(request):
    """Halaman hasil Test Kesadaran"""
    # Check if there is post request
    if request.method == 'POST':
        # Get score
        score = int(request.POST.get('score'))
        user = request.user

        if 15 <= score <= 39:
            resultKey = 1
            resultType = "Kamu Sangat Peka"
        elif 40 <= score <= 49:
            resultKey = 2
            resultType = "Kamu Cukup Peka"
        elif 50 <= score <= 59:
            resultKey = 3
            resultType = "Kamu Sangat Kurang Peka"
        elif score == 60:
            resultKey = 4
            resultType = "Kamu Tidak Peka"
        else:             
            resultKey = 0
            resultType = "Error!"

        result_data = {
            0: "Error, harap coba lagi! Jika masih error harap hubungi admin",
            # Kamu Sangat Peka
            1: "Berdasarkan jawaban kamu, dapat disimpulkan bahwa kamu adalah orang yang sangat peka dan memiliki kesadaran penuh terhadap emosi dirimu dan kegiatan yang kamu lakukan. Hal yang bagus! Untuk itu, tetap pertahankan ya! Banggalah terhadap dirimu sendiri dan berikan senyum terbaikmu. Semangat!",
            # Kamu Kurang Peka
            2: "Berdasarkan jawaban kamu, dapat disimpulkan bahwa untuk saat ini kamu adalah orang yang cukup peka dan kurang memiliki kesadaran terhadap emosi dirimu dan kegiatan yang kamu lakukan. Untuk itu, cobalah kembali renungkan apa yang perlu pemicu utamanya, dan mintalah bantuan kepada orang terdekatmu. Berbicaralah dan kembali terbuka atas keluh kesahmu. Apapun keadaanmu sekarang, kamu adalah orang yang hebat. Tetap semangat!",
            # Mengalami depresi yang cukup tinggi
            3: "Berdasarkan jawaban kamu, dapat disimpulkan bahwa untuk saat ini kamu adalah orang yang kurang peka dan sangat kurang memiliki kesadaran terhadap emosi dirimu dan kegiatan yang kamu lakukan. Untuk itu, cobalah kembali menjadi orang yang terbuka dan meminta bantuan kepada orang terdekatmu, maupun orang yang menurutmu dapat dipercaya dan paham dengan hal yang kamu rasakan. Jauhkan dirimu dari yang kamu anggap buruk. Secara perlahan, kami yakin bahwa kamu bisa melewati fase ini. Tetap senyum dan berikan yang terbaik, ya! Kamu adalah orang yang hebat, semangat!",
            # Mengalami depresi yang tinggi
            4: "Berdasarkan jawaban kamu, dapat disimpulkan bahwa untuk saat ini kamu adalah orang yang tidak peka dan tidak memiliki kesadaran terhadap emosi dirimu dan kegiatan yang kamu lakukan. Untuk itu, cobalah kembali menjadi orang yang terbuka secara perlahan. Renungkan dengan dirimu sendiri, pasti kamu akan mendapatkan jalan keluar yang terbaik versimu. Mintalah bantuan orang terdekat maupun orang yang menurutmu dapat dipercaya dan paham dengan hal yang kamu rasakan. Kamu tidak perlu berjuang sendiri, banyak sekali orang yang dapat membantumu dan peduli dengan kehadiranmu. Kami yakin bahwa kamu bisa melewati fase ini. Tetap senyum dan berikan yang terbaik, ya! Kamu adalah orang yang hebat, semangat!",
        }

        # Save to history if user is logged in
        if request.user.is_authenticated:
            # Save to history
            history = History(user=user, quiz_type='Test Kesadaran', res_type=resultType, res_data=result_data[resultKey])
            history.save()
        
            notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
        else:
            notifications = None
        # Nanti bisa di return banyak, style json -> title, hasil text, apa2 lah
        return render(request, 'tests/result.html', {'res_type': resultType, 'res_data': result_data[resultKey], 'notifications': notifications, 'quiz_type': 'Test Kesadaran'})
    else:
        messages.info(request, 'Silahkan test terlebih dahulu!')        
        return redirect('/tests')

def test_Result(request):
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    else:
        notifications = None

    # If a post request is sent
    if request.method == 'POST':
        res_type = request.POST.get('res_type')
        res_data = request.POST.get('res_data')
        quiz_type = request.POST.get('quiz_type')
        return render(request, 'tests/result.html', {'res_type': res_type, 'res_data': res_data, 'notifications': notifications, 'quiz_type': quiz_type})
    else:
        messages.info(request, 'Silahkan test terlebih dahulu!')        
        return redirect('/tests')

# ----------------------------------------------------------------
# Artikel
def artikel(request):
    """See all artikel"""
    tags = Tag.objects.filter(type="Artikel")
    # if user is authenticated
    if request.user.is_authenticated:
        # Get user's notification
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    else:
        notifications = None
    searching = False
    nextPage = False
    q = None
    # Check if there is a search
    if request.GET.get('q'):
        query = request.GET.get('q')
        paginator = Paginator(Artikel.objects.filter(title__icontains=query).order_by('-created_at'), 25)
        page = request.GET.get('page')
        posts_artikel = paginator.get_page(page)
        searching = True
        q = query

        # Check if no result found
        if paginator.count == 0:
            messages.info(request, 'No result found')
            return redirect('/artikel')
    else:
        paginator = Paginator(Artikel.objects.all().order_by('-created_at'), 25)
        page = request.GET.get('page')
        posts_artikel = paginator.get_page(page)
        if page:
            if int(page) > 1:
                nextPage = True

    # Get top 3 popular artikel sorted by views
    popular_artikel = Artikel.objects.all().order_by('-views')[:3]

    return render(request, 'artikel/index.html', {'posts': posts_artikel, 'tags': tags, 'popular_artikel': popular_artikel, 'searching': searching, 'nextPage': nextPage, 'notifications': notifications, 'q': q})

def artikel_tag(request, tagName):
    """See post by tag"""
    tag = Tag.objects.get(name=tagName.replace('-', ' '))
    # if user is authenticated
    if request.user.is_authenticated:
        # Get user's notification
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    else:
        notifications = None
    if tag is not None and tag.type == 'Artikel':
        paginator = Paginator(Artikel.objects.filter(tag=tag).order_by('-created_at'), 25)
        page = request.GET.get('page')
        posts = paginator.get_page(page)
        return render(request, 'artikel/tag.html', {'posts': posts, 'tag': tag, 'notifications': notifications})
    else:
        raise Http404

def artikel_content(request, id):
    """Redirect to artikel content"""
    if id is not None:
        try:
            post = Artikel.objects.get(id=id)
        except:
            raise Http404

        # Redirect to vanity url
        return redirect('/artikel/' + str(post.id) + '/' + post.title.replace(' ', '-'))
    else:
        # return 404
        raise Http404

def artikel_url(request, id, title):
    """Generate URL for post with vanity url of title"""
    # Title in the link is just for vanity url
    if id is not None and title is not None:
        post = Artikel.objects.get(id=id)
            # if user is authenticated
        if request.user.is_authenticated:
            # Get user's notification
            notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
        else:
            notifications = None
        # To ensure the vanity url is always exactly the title
        if title.replace('-', ' ') != post.title.replace('?', ''):
            return redirect('/artikel/' + str(post.id) + '/' + post.title.replace(' ', '-').replace('?', ''))
        
        if post is not None:
            # Increase the view of the post
            post.views += 1

            # Save the post
            post.save()
            
            return render(request, 'artikel/view.html', {'post': post, 'notifications': notifications})
        else:
            raise Http404
    else:
        # return 404
        raise Http404

def artikel_create(request):
    """Create post, if no request open page like usual. Request are made using jquery ajax
    
    Onsucess: Redirect to the post
    Onfail: Return error message
    """
    if request.user.is_authenticated:
        if request.method == 'POST': # If a request is made
            user = request.user
            title = request.POST.get('title')
            content = request.POST.get('content')
            tag_get = request.POST.get('tag')
            thumbnail_url = request.POST.get('thumbnail_url')
            
            # Check if tag is found
            if tag_get is None:
                messages.info(request, 'Invalid tag options!')
                return HttpResponse('error')

            # Check tittle length
            if len(title) < 5:
                messages.info(request, 'Title is too short, Min title length is 5 characters')
                return HttpResponse('error')

            if len(title) > 200:
                messages.info(request, 'Title is too long, Max title length is 200 characters')
                return HttpResponse('error')

            # Check content length
            if len(content) < 25:
                messages.info(request, 'Content must be at least 25 characters!')
                return HttpResponse('limit')

            # Max 40k
            if len(content) > 40000:
                messages.info(request, 'Invalid content length! Max allowed are 40k including formatting')
                return HttpResponse('limit')

            # Check if tag is found
            tag = Tag.objects.get(name=tag_get)

            if tag is None:
                messages.info(request, 'Invalid tag options! No tag found!')
                return HttpResponse('error')

            post = Artikel(title=title, content=content, user=user, tag=tag, thumbnail_url=thumbnail_url)
            post.save()

            # Return the post id
            getPost = Artikel.objects.get(title=title, content=content, user=user)
            return HttpResponse(getPost.id)
        else: # user enter normally
            tags = Tag.objects.filter(type="Artikel")
            notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
            return render(request, 'artikel/create.html', {'tags': tags, 'notifications': notifications})
    else: # user is not logged in
        messages.info(request, 'Need to login first!')
        return redirect('/auth/login')

def artikel_edit(request, id, title):
    """Edit post, if no request open page like usual. Request are made using jquery ajax
    
    Onsucess: Redirect to the post
    Onfail: Return error message
    """
    # Check if user is logged in and it's the post owner
    if request.user != Artikel.objects.get(id=id).user:
        raise PermissionDenied()

    if request.user.is_authenticated:
        if request.method == 'POST': # If an update is made
            # Can't change title
            content = request.POST.get('content') # content change
            tag_name = request.POST.get('tag') # if user change the tag, it will be changed
            thumbnail_url = request.POST.get('thumbnail_url')

            if len(content) < 25:
                messages.info(request, 'Content must be at least 25 characters!')
                return HttpResponse('limit')

            # Max 40k
            if len(content) > 40000:
                messages.info(request, 'Invalid content length! Max allowed are 40k including formatting')
                return HttpResponse('limit')

            # Get the post and tag object
            post = Artikel.objects.get(id=id)
            tag = Tag.objects.get(name=tag_name)

            # Change the stuff
            post.content = content
            post.tag = tag
            post.thumbnail_url = thumbnail_url

            # Save
            post.save()

            # Redirect to the post
            return HttpResponse('success')
        else: # If user enter the edit page
            post = Artikel.objects.get(id=id)
            tag = Tag.objects.filter(type="Artikel")

            if title.replace('-', ' ') != post.title: # Ensure the title is exactly the same
                return redirect('/artikel/' + str(post.id) + '/' + post.title.replace(' ', '-') + '/edit')

            notifications = Notification.objects.filter(user=request.user).order_by('-created_at')

            return render(request, 'artikel/edit.html', {'post': post, 'tags': tag, 'notifications': notifications})
    else: # Double check, this shouldn't actually happen
        messages.info(request, 'Need to login first!')
        return HttpResponse('error')

def artikel_delete(request, id, title):
    """Delete a post. Only post request allowed, if no request throw 404. Request are made using jquery ajax
    
    onsuccess: Go to post home
    onfail: Alert fail using jquery
    """
    # Check if user is logged in and it's the post owner
    if request.method == 'POST': # If a request is made
        mode = request.POST.get('mode')
        user = request.user
        post = Artikel.objects.get(id=id)

        if not user.is_superuser:
            if user != post.user:
                messages.info(request, 'Need to login first!')
                dataJson = {'status': 'error', 'message': 'Need to login first!'}
                return HttpResponse(json.dumps(dataJson))

        # If delete mode admin send notification to the user
        if mode == 'admin' and user.is_superuser:
            if post.user != None: # Check if post user's account still exist
                # Check if the deleted comment's user is admin, if admin then dont send notification
                if not post.user.is_superuser:
                    # Get reason for deletion by admin
                    reason = request.POST.get('reason')
                    # Send notification to user
                    notification = Notification(user=post.user, notification_Content='Your post has been deleted by admin (' + user.username + '). Reason: ' + reason)
                    notification.save()

        # Delete the post
        post.delete()

        # Return success
        dataJson = {'status': 'success', 'message': 'The post has been deleted successfully!'}
        return HttpResponse(json.dumps(dataJson))
    else: # If no request, throw 404
        raise Http404

#quick links privacy policy
def privacy_policy(request):
    if request.user.is_authenticated:
        # Get user's notification
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    else:
        notifications = None
    return render(request, 'privacy-policy.html', {'notifications': notifications})

#quick links faq
def faq(request):
    if request.user.is_authenticated:
        # Get user's notification
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    else:
        notifications = None
    return render(request, 'faq.html', {'notifications': notifications})