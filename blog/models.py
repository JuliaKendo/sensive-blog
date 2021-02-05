import more_itertools
from django.db import models
from django.urls import reverse
from django.db.models import Count, Prefetch
from django.contrib.auth.models import User


class PostQuerySet(models.QuerySet):

    def popular(self):
        popular_posts = self.annotate(
            total_likes=Count('likes', distinct=True)
        ).order_by('-total_likes')
        return popular_posts

    def fresh(self):
        fresh_posts = self.order_by('-published_at')
        return fresh_posts

    def fetch_with_comments_count(self):
        posts_with_comments = Post.objects.filter(
            id__in=self
        ).annotate(
            total_comments=Count('related_comments')
        )
        post_ids_and_comments = dict(
            posts_with_comments.values_list('id', 'total_comments')
        )
        for post in self:
            post.total_comments = post_ids_and_comments[post.id]
        return self

    def fetch_posts_count_for_tags(self):
        posts_count_for_tags = Post.objects.filter(
            id__in=self
        ).prefetch_related(
            Prefetch(
                'tags',
                queryset=Tag.objects.annotate(posts_with_tag=Count('posts'))
            )
        )
        for post in self:
            current_post = filter(
                lambda x, y=post: x.id == y.id,
                posts_count_for_tags
            )
            post_count_for_tags = more_itertools.first(current_post)
            for tag in post_count_for_tags.tags.all():
                post.total_tags = {
                    'title': tag.title,
                    'posts_with_tag': tag.posts_with_tag
                }
        return self



class Post(models.Model):
    title = models.CharField("Заголовок", max_length=200)
    text = models.TextField("Текст")
    slug = models.SlugField("Название в виде url", max_length=200)
    image = models.ImageField("Картинка")
    published_at = models.DateTimeField("Дата и время публикации")

    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name="Автор", limit_choices_to={'is_staff': True}
    )
    likes = models.ManyToManyField(
        User, related_name="liked_posts",
        verbose_name="Кто лайкнул", blank=True
    )
    tags = models.ManyToManyField(
        "Tag", related_name="posts", verbose_name="Теги"
    )

    objects = PostQuerySet.as_manager()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post_detail', args={'slug': self.slug})

    class Meta:
        ordering = ['-published_at']
        verbose_name = 'пост'
        verbose_name_plural = 'посты'


class TagQuerySet(models.QuerySet):

    def popular(self):
        popular_tags = self.annotate(
            total_posts=Count('posts', distinct=True)
        ).order_by('-total_posts')
        return popular_tags


class Tag(models.Model):
    title = models.CharField("Тег", max_length=20, unique=True)

    objects = TagQuerySet.as_manager()

    def __str__(self):
        return self.title

    def clean(self):
        self.title = self.title.lower()

    def get_absolute_url(self):
        return reverse('tag_filter', args={'tag_title': self.slug})

    class Meta:
        ordering = ["title"]
        verbose_name = 'тег'
        verbose_name_plural = 'теги'


class CommentQuerySet(models.QuerySet):

    def fetch_comments_on_post(self, post):
        comments_by_post = self.select_related().filter(post=post)
        serialized_comments = []
        for comment in comments_by_post:
            serialized_comments.append({
                'text': comment.text,
                'published_at': comment.published_at,
                'author': comment.author.username,
            })
        return serialized_comments


class Comment(models.Model):
    post = models.ForeignKey(
        "Post", on_delete=models.CASCADE,
        verbose_name="Пост, к которому написан",
        related_name='related_comments'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Автор"
    )

    text = models.TextField("Текст комментария")
    published_at = models.DateTimeField("Дата и время публикации")

    objects = CommentQuerySet.as_manager()

    def __str__(self):
        return f"{self.author.username} under {self.post.title}"

    class Meta:
        ordering = ['published_at']
        verbose_name = 'комментарий'
        verbose_name_plural = 'комментарии'
