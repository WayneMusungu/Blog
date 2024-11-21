from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry

from posts.models import Post


@registry.register_document
class PostDocument(Document):
    title = fields.TextField(
        attr='title',
        fields={
            'raw': fields.TextField(),
            'suggest': fields.CompletionField(),
        }
    )
    categories = fields.ObjectField(
        attr='categories',
        properties={
            'id': fields.IntegerField(),
            'category': fields.TextField(
                attr='name',
                fields={
                    'raw': fields.KeywordField(),
                }
            )
        }
    )

    class Index:
        name = 'posts'

    class Django:
        model = Post