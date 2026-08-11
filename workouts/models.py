from django.db import models
from django.db.models import Max
from products.models import SubscriptionProduct
from sports.utils.slug import unique_slug_generator
from django.utils import timezone
from django.core.exceptions import ValidationError

# Create your models here.

def get_next_course_number():
    max_number = WorkoutCourse.objects.aggregate(Max('number'))['number__max']
    if max_number is None:
        return 1
    return max_number + 1

class WorkoutCourse(models.Model):
    title = models.CharField(max_length=200, verbose_name='عنوان دوره')
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True, verbose_name='عنوان در آدرس')
    description = models.TextField(blank=True, null=True, verbose_name='توضیحات کوتاه')
    subscription_product = models.ForeignKey(SubscriptionProduct, on_delete=models.PROTECT, related_name='courses', verbose_name='محصول اشتراکی مرجع')

    number = models.IntegerField(unique=True, default=get_next_course_number, verbose_name='شماره دوره')
    start_date = models.DateField(verbose_name='تاریخ شروع تمرینات')
    duration_days = models.PositiveIntegerField(default=7, verbose_name='تعداد روزهای دوره')

    @property
    def next_update_days(self):
        days_passed = (timezone.localdate() - self.start_date).days
        return self.duration_days - (days_passed % self.duration_days)
    
    class Meta:
        verbose_name = "دوره تمرینی"
        verbose_name_plural = "دوره‌های تمرینی"
        ordering = ['number']
    
    def __str__(self):
        return f"دوره {self.number}: {self.title}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug_generator(self)
        return super().save(*args, **kwargs)


class DailyWorkout(models.Model):
    title = models.CharField(max_length=200, verbose_name='عنوان تمرین روز')
    description = models.TextField(blank=True, null=True, verbose_name='توضیحات کوتاه')
    content = models.TextField(verbose_name='محتوای تمرین (مارک‌داون)', help_text='می‌توانید از کدهای مارک‌داون و لینک ویدیوها در این بخش استفاده کنید.')
    plan = models.ForeignKey(WorkoutCourse, on_delete=models.CASCADE, related_name='daily_workouts', verbose_name='دوره مربوطه')
    day_number = models.PositiveIntegerField(verbose_name='شماره روز (روز ۱، روز ۲)')

    class Meta:
        verbose_name = 'تمرین روزانه'
        verbose_name_plural = 'تمرین‌های روزانه'
        unique_together = ['plan', 'day_number']
        ordering = ['plan__number', 'day_number']

    def __str__(self):
        return f"{self.plan.number}) {self.plan.title} - روز {self.day_number}: {self.title}"

class ActiveWorkoutCourseConfig(models.Model):
    subscription_product = models.OneToOneField(SubscriptionProduct, on_delete=models.PROTECT, related_name='active_course_config', verbose_name='محصول اشتراکی مرجع')
    current_course = models.OneToOneField(WorkoutCourse, blank=True, null=True, on_delete=models.PROTECT, related_name='active_for_products', verbose_name='دوره تمرینی فعال')

    def clean(self):
        super().clean()
        if self.current_course and self.current_course.subscription_product_id != self.subscription_product_id:
            raise ValidationError({
                'current_course': 'دوره انتخاب‌شده باید متعلق به همین محصول اشتراکی باشد.'
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = 'پیکربندی دوره محصول'
        verbose_name_plural = 'پیکربندی دوره محصولات'

    def __str__(self):
        if self.current_course:
            return f'{self.subscription_product.title} - {self.current_course.title}'
        return self.subscription_product.title