from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, DetailView
from django.views import View
from . import models
from entitlements.models import SubscriptionEntitlement

# Create your views here.

class WorkoutCourseView(DetailView):
    template_name = 'workouts/workout_course.html'
    model = models.WorkoutCourse
    context_object_name = 'course'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        queryset = (super().get_queryset()
                    .select_related('subscription_product')
                    .filter(subscription_product__is_active=True, active_for_products__isnull=False))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        course = self.get_object()
        entitlement = SubscriptionEntitlement.objects.select_related('user', 'product').filter(user=user, product=course.subscription_product).first()
        context['entitlement'] = entitlement
        return context

class WorkoutDayDetailView(View):
    template_name = 'workouts/workout_day_detail.html'
    def get(self, request, slug,day_id):
        course = get_object_or_404(models.WorkoutCourse.objects.select_related('subscription_product'), slug=slug)
        context = {
            'current_day': get_object_or_404(course.daily_workouts.all(), id=day_id)
            }
        return render(request, self.template_name, context)