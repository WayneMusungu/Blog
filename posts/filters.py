import django_filters
from posts.models import Post

class PostFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(field_name='categories__name', lookup_expr='icontains')

    class Meta:
        model = Post
        fields = ['category']
