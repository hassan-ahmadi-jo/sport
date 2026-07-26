from django.utils.text import slugify

def unique_slug_generator(instance, slug_field='slug', title_field='title', new_slug=None):
    if new_slug:
        slug = new_slug
    else:
        title = getattr(instance, title_field)
        slug = slugify(title, allow_unicode=True)

    Klass = instance.__class__
    qs = Klass.objects.all()

    if instance.pk:
        qs = qs.exclude(pk=instance.pk)

    if not qs.filter(**{slug_field: slug}).exists():
        return slug

    counter = 2
    while True:
        candidate = f'{slug}-{counter}'
        if not qs.filter(**{slug_field: candidate}).exists():
            return candidate
        counter += 1