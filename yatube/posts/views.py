from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.views.generic.base import TemplateView
from django.shortcuts import redirect
from .models import Group, Post, User
from .forms import PostForm
from django.contrib.auth.decorators import login_required


def index(request):
    post_list = Post.objects.all().order_by('-pub_date')
    # Если порядок сортировки определен в классе Meta модели,
    # запрос будет выглядить так:
    # post_list = Post.objects.all()
    # Показывать по 10 записей на странице.
    paginator = Paginator(post_list, 10)

    # Из URL извлекаем номер запрошенной страницы - это значение параметра page
    page_number = request.GET.get('page')

    # Получаем набор записей для страницы с запрошенным номером
    page_obj = paginator.get_page(page_number)
    # Отдаем в словаре контекста
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()[:10]
    paginator = Paginator(group.posts.all(), 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'posts': posts,
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


class JustStaticPage(TemplateView):
    template_name = 'app_name/just_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Здесь можно произвести какие-то действия для создания контекста.
        # Для примера в словарь просто передаются две строки
        context['just_title'] = 'Очень простая страница'
        context['just_text'] = ('На создание этой страницы '
                                'у меня ушло пять минут! Ай да я.')
        return context


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author=author)
    page_number = request.GET.get('page')
    paginator = Paginator(post_list, 10)
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj,
               'author': author,
               }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = Post.objects.get(pk=post_id)
    context = {
        'post': post,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            author_field = form.save(commit=False)
            author_field.author = request.user
            form.save()
            return redirect('posts:profile', request.user)

        return render(request, 'posts/create_post.html', {'form': form})
    form = PostForm()
    return render(request, 'posts/create_post.html', {'form': form})


def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
        return redirect('posts:post_detail', post.pk,)
    is_edit = True
    form = PostForm(instance=post)
    context = {'form': form, 'is_edit': is_edit}
    return render(request, 'posts/create_post.html', context)
