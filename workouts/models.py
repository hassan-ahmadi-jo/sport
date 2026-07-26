from django.db import models
from django.db.models import Max
from products.models import SubscriptionProduct
from sports.utils.slug import unique_slug_generator

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