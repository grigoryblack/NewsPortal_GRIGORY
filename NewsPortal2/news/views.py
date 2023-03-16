from django.shortcuts import render, redirect
from django.views.generic import CreateView, DetailView, DeleteView, ListView, UpdateView
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.core.cache import cache

from .models import Author, Category, Comment, Post, User
from .filters import PostFilter
from .forms import CommentForm, PostForm


class PostCreateView(PermissionRequiredMixin, CreateView):

    model = Post
    template_name = 'post_create.html'
    form_class = PostForm
    success_url = '/'
    permission_required = ('news.add_post',)

    def form_valid(self, form):
        current_user = self.request.user
        form.instance.author = Author.objects.get(author_user=current_user)
        return super(PostCreateView, self).form_valid(form)


class PostsListView(ListView):

    model = Post
    template_name = 'post_list.html'
    context_object_name = 'posts'
    ordering = ['-id']
    paginate_by = 10

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = PostFilter(self.request.GET, queryset=self.get_queryset())
        return context


class PostDetailView(DetailView):

    model = Post
    template_name = 'post_detail.html'
    context_object_name = 'post'
    queryset = Post.objects.all()


    def get_object(self, *args, **kwargs,):
        obj = cache.get(f'post-{self.kwargs["pk"]}', None)
        if not obj:
            obj = super().get_object(queryset=self.queryset)
            cache.set(f'post-{self.kwargs["pk"]}', obj)
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        id = self.kwargs.get('pk')
        post = Post.objects.get(pk=id)
        current_user = self.request.user
        # добавление формы комментариев
        context['comment_form'] = CommentForm()
        # комментировать могут только зарегистрированные пользователи
        context['registered_user'] = True if current_user in User.objects.all() else False
        # удалять и редактировать можно только собственные посты
        context['own_post'] = True if current_user == post.author.author_user else False
        return context

    def post(self, request, pk):

        post = self.get_object(pk=pk)
        form = CommentForm(request.POST)

        if form.is_valid():
            obj = form.save(commit=False)
            obj.post = post
            obj.author = self.request.user
            obj.save()
            return redirect('post_detail', post.pk)


class PostUpdateView(PermissionRequiredMixin, UpdateView):

    model = Post
    template_name = 'post_create.html'
    fields = ('author', 'type', 'title', 'content', 'category')
    success_url = '/'
    permission_required = ('news.change_post',)


class PostDeleteView(PermissionRequiredMixin, DeleteView):

    model = Post
    template_name = 'post_delete.html'
    success_url = '/'
    permission_required = ('news.delete_post',)


class CategoryList(ListView):

    model = Category
    template_name = 'category_list.html'
    context_object_name = 'categories'


class CategoryDetail(LoginRequiredMixin, DetailView):
    "
    model = Category
    template_name = 'category_detail.html'
    context_object_name = 'category'


def add_subscriber(request, **kwargs):

    pk = kwargs.get('pk')
    category = Category.objects.get(pk=pk)
    curr_usr = request.user
    category.subscribers.add(curr_usr)
    return redirect('/categories/')


def remove_subscriber(request, **kwargs):

    pk = kwargs.get('pk')
    category = Category.objects.get(pk=pk)
    curr_usr = request.user
    category.subscribers.remove(curr_usr)
    return redirect('/categories/')
