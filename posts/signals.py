from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django_elasticsearch_dsl.registries import registry
from posts.models import Post
import logging

# Set up a logger
logger = logging.getLogger(__name__)

@receiver(post_save, sender=Post)
def update_document(sender, instance, **kwargs):
    """
    Update the Elasticsearch document for the updated Post instance.
    """
    try:
        registry.update(instance)
    except Exception as e:
        # Log the error with relevant details
        logger.error(f"Failed to update Elasticsearch document for Post ID {instance.id}: {e}")

@receiver(post_delete, sender=Post)
def delete_document(sender, instance, **kwargs):
    """
    Delete the Elasticsearch document for the deleted Post instance.
    """
    try:
        registry.delete(instance)
    except Exception as e:
        # Log the error with relevant details
        logger.error(f"Failed to delete Elasticsearch document for Article ID {instance.id}: {e}")