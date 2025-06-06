from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render,get_object_or_404,redirect
from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin
from django.contrib.auth.models import User
from django.http import HttpResponse
from .models import Post
from django.views.generic import ListView ,DetailView ,CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required


def home(request):
    context= {
        'posts':Post.objects.all()
    }
    return render(request,'blog/home.html',context)

class PostListView(ListView):
    model = Post
    template_name = 'blog/home.html' #<app>/<model>_<viewtype>.html
    context_object_name ='posts'
    paginate_by = 5
    ordering =['-date_posted']

    def get_queryset(self):
        query = self.request.GET.get('q')  # Get search query from URL
        if query:
            return Post.objects.filter(title__icontains=query).order_by('-date_posted')
        return Post.objects.all().order_by('-date_posted')

class UserPostListView(ListView):
    model = Post
    template_name = 'blog/user_posts.html' #<app>/<model>_<viewtype>.html
    context_object_name ='posts'
    paginate_by = 5
    
    
    def get_queryset(self):
        user = get_object_or_404(User,username=self.kwargs.get('username'))
        return Post.objects.filter(author = user).order_by('-date_posted')

    

class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    
class PostCreateView(LoginRequiredMixin,CreateView):
    model = Post
    fields = ['title','content','image']
    template_name = 'blog/post_form.html'

    def form_valid(self ,form):
        form.instance.author = self.request.user 
        return super().form_valid(form)
    
class PostUpdateView(LoginRequiredMixin,UserPassesTestMixin,UpdateView):
    model = Post
    fields = ['title','content','image']
    template_name = 'blog/post_form.html'

    def form_valid(self ,form):
        form.instance.author = self.request.user 
        return super().form_valid(form)
    
    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False
    
class PostDeleteView(LoginRequiredMixin,UserPassesTestMixin,DeleteView):
    model = Post
    success_url = '/'
    template_name = 'blog/post_confirm_delete.html'


    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False
    

@login_required
def like_post(request, post_id):
    # Get the post object by id
    post = get_object_or_404(Post, id=post_id)

    # Toggle the like status
    if request.user in post.likes.all():
        post.likes.remove(request.user)  # If user already liked, remove like
    else:
        post.likes.add(request.user)  # If user has not liked, add like

    # Redirect back to the post detail page
    return redirect('post-detail', pk=post.id)


def about(request):
    return render(request,'blog/about.html',{'title':'About'})