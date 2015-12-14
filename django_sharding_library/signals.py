from django.apps import apps

def create_save_shard_handler(shard_app_label):
    def save_shard_handler(sender, instance, **kwargs):
        """
        Saves the shard to the model in the field `shard`.
        e.g. usage:
        @receiver(models.signals.pre_save, sender=User)
        def shard_handler(sender, instance, **kwargs):
            save_shard_handler(sender, instance, **kwargs)
        """
        bucketer = apps.get_app_config(shard_app_label).get_bucketer(sender.django_sharding__shard_group)
        shard_fields = filter(lambda field: getattr(field, 'django_sharding__stores_shard', False), sender._meta.fields)
        if not any(shard_fields):
            shard_field_name = getattr(sender, 'django_sharding__shard_field', None)
            shard_fields = filter(lambda field: field.name == shard_field_name, sender._meta.fields)
    
        if not any(shard_fields):
            return
    
        if len(shard_fields) > 1:
            raise Exception('The model {} has multuple fields for shard storage: {}'.format(sender, shard_fields))
        shard_field = shard_fields[0]
        if not getattr(instance, shard_field.name, None):
            setattr(instance, shard_field.name, bucketer.pick_shard(instance))
    return save_shard_handler
