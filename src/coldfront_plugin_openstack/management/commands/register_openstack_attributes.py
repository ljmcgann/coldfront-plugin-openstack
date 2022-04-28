from django.core.management.base import BaseCommand

from coldfront.core.allocation import models as allocation_models
from coldfront.core.resource import models as resource_models

from coldfront_plugin_openstack import attributes


class Command(BaseCommand):
    help = 'Add default OpenStack allocation related choices'

    def register_allocation_attributes(self):
        def register(attribute_name, attribute_type):
            allocation_models.AllocationAttributeType.objects.get_or_create(
                name=attribute_name,
                attribute_type=allocation_models.AttributeType.objects.get(
                    name=attribute_type),
                has_usage=False,
                is_private=False,
                is_changeable='Quota' in attribute_name
            )

        for allocation_attribute in attributes.ALLOCATION_ATTRIBUTES:
            register(allocation_attribute, 'Text')

        for allocation_quota_attribute in attributes.ALLOCATION_QUOTA_ATTRIBUTES:
            register(allocation_quota_attribute, 'Int')

    def register_resource_attributes(self):
        for resource_attribute_type in attributes.RESOURCE_ATTRIBUTES:
            resource_models.ResourceAttributeType.objects.get_or_create(
                name=resource_attribute_type,
                attribute_type=resource_models.AttributeType.objects.get(
                    name='Text')
            )

    def register_resource_type(self):
        resource_models.ResourceType.objects.get_or_create(
            name='OpenStack', description='OpenStack Cloud'
        )
        resource_models.ResourceType.objects.get_or_create(
            name='OpenShift', description='OpenShift Cloud'
        )

    def handle(self, *args, **options):
        self.register_resource_type()
        self.register_resource_attributes()
        self.register_allocation_attributes()
