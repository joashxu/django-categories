from django.core.urlresolvers import reverse
from django.db import models
from django.utils.encoding import force_unicode
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from django.utils.translation import ugettext_lazy as _

from .settings import RELATION_MODELS, RELATIONS

from .base import CategoryBase


class Category(CategoryBase):
    order = models.IntegerField(default=0)
    alternate_title = models.CharField(
        blank=True,
        default="",
        max_length=100,
        help_text="An alternative title to use on pages with this category.")
    alternate_url = models.CharField(
        blank=True,
        max_length=200,
        help_text="An alternative URL to use instead of the one derived from "
                  "the category hierarchy.")
    description = models.TextField(blank=True, null=True)
    meta_keywords = models.CharField(
        blank=True,
        default="",
        max_length=255,
        help_text="Comma-separated keywords for search engines.")
    meta_extra = models.TextField(
        blank=True,
        default="",
        help_text="(Advanced) Any additional HTML to be placed verbatim "
                  "in the &lt;head&gt;")

    @property
    def short_title(self):
        return self.name

    def get_absolute_url(self):
        """Return a path"""
        if self.alternate_url:
            return self.alternate_url
        prefix = reverse('categories_tree_list')
        ancestors = list(self.get_ancestors()) + [self, ]
        return prefix + '/'.join([force_unicode(i.slug) for i in ancestors]) + '/'

    if RELATION_MODELS:
        def get_related_content_type(self, content_type):
            """
            Get all related items of the specified content type
            """
            return self.categoryrelation_set.filter(
                content_type__name=content_type)

        def get_relation_type(self, relation_type):
            """
            Get all relations of the specified relation type
            """
            return self.categoryrelation_set.filter(relation_type=relation_type)

    class Meta(CategoryBase.Meta):
        verbose_name = _('category')
        verbose_name_plural = _('categories')

    class MPTTMeta:
        order_insertion_by = ('order', 'name')


if RELATIONS:
    CATEGORY_RELATION_LIMITS = reduce(lambda x, y: x | y, RELATIONS)
else:
    CATEGORY_RELATION_LIMITS = []


class CategoryRelationManager(models.Manager):
    def get_content_type(self, content_type):
        """
        Get all the items of the given content type related to this item.
        """
        qs = self.get_queryset()
        return qs.filter(content_type__name=content_type)

    def get_relation_type(self, relation_type):
        """
        Get all the items of the given relationship type related to this item.
        """
        qs = self.get_queryset()
        return qs.filter(relation_type=relation_type)


class CategoryRelation(models.Model):
    """Related category item"""
    category = models.ForeignKey(Category, verbose_name=_('category'))
    content_type = models.ForeignKey(
        ContentType, limit_choices_to=CATEGORY_RELATION_LIMITS, verbose_name=_('content type'))
    object_id = models.PositiveIntegerField(verbose_name=_('object id'))
    content_object = GenericForeignKey('content_type', 'object_id')
    relation_type = models.CharField(verbose_name=_('relation type'),
                                     max_length="200",
                                     blank=True,
                                     null=True,
                                     help_text=_("A generic text field to tag a relation, like 'leadphoto'."))

    objects = CategoryRelationManager()

    def __unicode__(self):
        return u"CategoryRelation"
