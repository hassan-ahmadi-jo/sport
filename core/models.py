from django.db import models
from django.db import transaction
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill

# Create your models here.
class SiteSettings(models.Model):
    name = models.CharField(max_length=70, verbose_name='عنوان سایت')
    tagline = models.TextField(verbose_name='توضیح خلاصه')

    logo = ProcessedImageField(
        upload_to='settings/logos/',
        processors=[ResizeToFill(300, 100)],
        format='WEBP',
        options={'quality': 90},
        verbose_name="لوگو سایت (عرض سه برابر ارتفاع)"
    )

    favicon = ProcessedImageField(
        upload_to='settings/favicons/',
        processors=[ResizeToFill(32, 32)],
        format='PNG',
        options={'quality': 90},
        null=True,
        blank=True,
        verbose_name="فاوآیکون"
    )

    email = models.EmailField(blank=True, null=True, verbose_name='ایمیل پشتیبانی')
    instagram = models.URLField(blank=True, null=True, verbose_name='لینک اینستاگرام')
    telegram = models.URLField(blank=True, null=True, verbose_name='لینک تلگرام')
    whatsapp = models.URLField(blank=True, null=True, verbose_name='لینک واتساپ')

    contact_website_designer = models.URLField(blank=True, null=True, verbose_name='لینک طراح (رزومه/لینکدین)')

    is_active = models.BooleanField(default=False, verbose_name='این تنظیمات فعال است؟')

    def clean(self):
        super().clean()
        if self.is_active:
            with transaction.atomic():
                active_settings = SiteSettings.objects.filter(is_active=True).select_for_update()
                if active_settings.exists():
                    active_settings.exclude(id=self.id).update(is_active=False)

    @classmethod
    def get_settings(cls):
        return cls.objects.filter(is_active=True).first() or cls.objects.first()

    def save(self, *args, **kwargs):
            self.full_clean()
            return super().save(*args, **kwargs)

    class Meta:
            verbose_name = 'پیکربندی سایت'
            verbose_name_plural = 'پیکربندی‌های سایت'

    def __str__(self):
         return self.name

