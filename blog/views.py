import more_itertools
from django.db.models import Count
from django.shortcuts import render
from blog.models import Comment, Post, Tag

SELECTION_LIMIT = 5
RELATED_POSTS_LIMIT = 20

def serialize_post(post):
    return {
        "title": post.title,
        "teaser_text": post.text[:200],
        "author": post.author.username,
        "comments_amount": post.total_comments,
        "image_url": post.image.url if post.image else None,
        "published_at": post.published_at,
        "slug": post.slug,
        "tags": post.total_tags,
        'first_tag_title': post.total_tags['title'],
    }


def serialize_tag(tag):
    return {
        'title': tag.title,
        'posts_with_tag': tag.total_posts,
    }


def index(request):

    popular_posts = Post.objects.popular()[:SELECTION_LIMIT] \
        .prefetch_related('author') \
        .fetch_with_comments_count() \
        .fetch_posts_count_for_tags()

    fresh_posts = Post.objects.fresh()[:SELECTION_LIMIT] \
        .prefetch_related('author') \
        .fetch_with_comments_count() \
        .fetch_posts_count_for_tags()

    popular_tags = Tag.objects.popular()[:SELECTION_LIMIT]

    context = {
        'most_popular_posts': [
            serialize_post(post) for post in popular_posts
        ],
        'page_posts': [
            serialize_post(post) for post in fresh_posts
        ],
        'popular_tags': [
            serialize_tag(tag) for tag in popular_tags
        ],
    }
    return render(request, 'index.html', context)


def post_detail(request, slug):
    posts = Post.objects.filter(slug=slug) \
        .annotate(total_likes=Count('likes', distinct=True)) \
        .prefetch_related('author') \
        .fetch_posts_count_for_tags()
    post = more_itertools.first(posts)
    serialized_comments = Comment.objects.fetch_comments_on_post(post)

    serialized_post = {
        "title": post.title,
        "text": post.text,
        "author": post.author.username,
        "comments": serialized_comments,
        'likes_amount': post.total_likes,
        "image_url": post.image.url if post.image else None,
        "published_at": post.published_at,
        "slug": post.slug,
        "tags": post.total_tags,
    }

    popular_posts = Post.objects.popular()[:SELECTION_LIMIT] \
        .prefetch_related('author') \
        .fetch_with_comments_count() \
        .fetch_posts_count_for_tags()

    popular_tags = Tag.objects.popular()[:SELECTION_LIMIT]

    context = {
        'post': serialized_post,
        'popular_tags': [
            serialize_tag(tag) for tag in popular_tags
        ],
        'most_popular_posts': [
            serialize_post(post) for post in popular_posts
        ],
    }
    return render(request, 'post-details.html', context)


def tag_filter(request, tag_title):
    tag = Tag.objects.get(title=tag_title)

    popular_posts = Post.objects.popular()[:SELECTION_LIMIT] \
        .prefetch_related('author') \
        .fetch_with_comments_count() \
        .fetch_posts_count_for_tags()

    related_posts = tag.posts.all()[:RELATED_POSTS_LIMIT] \
        .prefetch_related('author') \
        .fetch_with_comments_count() \
        .fetch_posts_count_for_tags()

    popular_tags = Tag.objects.popular()[:SELECTION_LIMIT]

    context = {
        "tag": tag.title,
        'popular_tags': [
            serialize_tag(tag) for tag in popular_tags
        ],
        "posts": [
            serialize_post(post) for post in related_posts
        ],
        'most_popular_posts': [
            serialize_post(post) for post in popular_posts
        ],
    }
    return render(request, 'posts-list.html', context)


def contacts(request):
    return render(request, 'contacts.html', {})
