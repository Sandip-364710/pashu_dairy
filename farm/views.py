from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Count, Q
from django.views.generic import TemplateView, CreateView, ListView, UpdateView, FormView
from django.views import View
from django.urls import reverse
from datetime import date, timedelta
from .models import CustomUser, Animal, MilkRecord
from .forms import CustomUserCreationForm, CustomUserLoginForm, AnimalForm, AnimalTypeSelectionForm, CheckupStatusForm, MilkRecordForm


class RegisterView(FormView):
    template_name = 'farm/register.html'
    form_class = CustomUserCreationForm
    success_url = '/'
    
    def form_valid(self, form):
        user = form.save()
        mobile = form.cleaned_data.get('mobile')
        password = form.cleaned_data.get('password1')
        user = authenticate(mobile=mobile, password=password)
        if user:
            login(self.request, user)
            messages.success(self.request, 'નોંધણી સફળ રહી!')
        return super().form_valid(form)


class LoginView(FormView):
    template_name = 'farm/login.html'
    form_class = CustomUserLoginForm
    success_url = '/dashboard/'
    
    def form_valid(self, form):
        mobile = form.cleaned_data['mobile']
        password = form.cleaned_data['password']
        user = authenticate(self.request, username=mobile, password=password)
        if user:
            login(self.request, user)
            messages.success(self.request, 'લોગિન સફળ રહ્યું!')
            return super().form_valid(form)
        else:
            messages.error(self.request, 'મોબાઇલ નંબર અથવા પાસવર્ડ ખોટો છે')
            return self.form_invalid(form)


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('login')


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'farm/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get user's animals
        animals = Animal.objects.filter(owner=user)
        
        # Calculate dashboard stats
        total_animals = animals.count()
        total_cows = animals.filter(animal_type='cow').count()
        total_buffaloes = animals.filter(animal_type='buffalo').count()
        
        # Today's milk records
        today_milk_records = MilkRecord.objects.filter(
            animal__owner=user,
            date=date.today()
        )
        today_total_liters = today_milk_records.aggregate(Sum('liters'))['liters__sum'] or 0
        today_total_amount = today_milk_records.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        
        # Check-up alerts (75 days completed)
        checkup_alerts = animals.filter(
            checkup_status='pending',
            insemination_date__lte=date.today() - timedelta(days=90)
        )
        
        # Upcoming deliveries (positive checkup status)
        upcoming_deliveries = animals.filter(
            checkup_status='positive'
        )
        
        # Recent milk records
        recent_milk_records = MilkRecord.objects.filter(
            animal__owner=user
        ).order_by('-date')[:5]
        
        context.update({
            'total_animals': total_animals,
            'total_cows': total_cows,
            'total_buffaloes': total_buffaloes,
            'today_total_liters': today_total_liters,
            'today_total_amount': today_total_amount,
            'checkup_alerts': checkup_alerts,
            'upcoming_deliveries': upcoming_deliveries,
            'recent_milk_records': recent_milk_records,
        })
        
        return context


class AddAnimalView(LoginRequiredMixin, View):
    template_name = 'farm/add_animal.html'
    
    def get_success_url(self):
        return reverse('dashboard')
    
    def get(self, request):
        animal_type = request.GET.get('animal_type')
        
        if animal_type:
            # Step 2: Show full form with filtered breeds
            form = AnimalForm(animal_type=animal_type)
            # Pre-select the animal type
            form.fields['animal_type'].initial = animal_type
            context = {
                'form': form,
                'step': 2,
                'selected_animal_type': animal_type,
                'animal_type_display': dict(Animal.ANIMAL_TYPES).get(animal_type, '')
            }
        else:
            # Step 1: Show animal type selection
            form = AnimalTypeSelectionForm()
            context = {
                'form': form,
                'step': 1,
            }
        
        return render(request, self.template_name, context)
    
    def post(self, request):
        animal_type = request.POST.get('animal_type')
        
        if 'select_animal_type' in request.POST:
            # Handle Step 1 submission
            form = AnimalTypeSelectionForm(request.POST)
            if form.is_valid():
                animal_type = form.cleaned_data['animal_type']
                # Redirect to step 2 with selected animal type
                return redirect(f"{reverse('add_animal')}?animal_type={animal_type}")
            else:
                context = {
                    'form': form,
                    'step': 1,
                }
                return render(request, self.template_name, context)
        
        elif 'add_animal' in request.POST:
            # Handle Step 2 submission
            form = AnimalForm(request.POST, animal_type=animal_type)
            if form.is_valid():
                animal = form.save(commit=False)
                animal.owner = request.user
                animal.save()
                messages.success(request, 'પ્રાણી સફળતાપૂર્વક ઉમેરાયું!')
                return redirect(self.get_success_url())
            else:
                context = {
                    'form': form,
                    'step': 2,
                    'selected_animal_type': animal_type,
                    'animal_type_display': dict(Animal.ANIMAL_TYPES).get(animal_type, '')
                }
                return render(request, self.template_name, context)
        
        # Fallback to step 1
        form = AnimalTypeSelectionForm()
        context = {
            'form': form,
            'step': 1,
        }
        return render(request, self.template_name, context)


class AnimalListView(LoginRequiredMixin, ListView):
    model = Animal
    template_name = 'farm/animal_list.html'
    context_object_name = 'animals'
    
    def get_queryset(self):
        return Animal.objects.filter(owner=self.request.user).order_by('-created_at')


class UpdateCheckupStatusView(LoginRequiredMixin, UpdateView):
    model = Animal
    form_class = CheckupStatusForm
    template_name = 'farm/update_checkup.html'
    success_url = '/dashboard/'
    
    def get_queryset(self):
        return Animal.objects.filter(owner=self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, 'તપાસ સ્થિતિ અપડેટ થઈ!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['animal'] = self.get_object()
        return context


class AddMilkRecordView(LoginRequiredMixin, CreateView):
    form_class = MilkRecordForm
    template_name = 'farm/add_milk_record.html'
    success_url = '/milk-records/'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        messages.success(self.request, 'દૂધ રેકોર્ડ સફળતાપૂર્વક ઉમેરાયો!')
        return super().form_valid(form)


class MilkRecordsView(LoginRequiredMixin, TemplateView):
    template_name = 'farm/milk_records.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        records = MilkRecord.objects.filter(
            animal__owner=self.request.user
        ).order_by('-date')
        
        # Calculate totals
        total_liters = records.aggregate(Sum('liters'))['liters__sum'] or 0
        total_amount = records.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        
        context.update({
            'records': records,
            'total_liters': total_liters,
            'total_amount': total_amount,
        })
        
        return context


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'farm/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context


@login_required
def guidance_view(request):
    return render(request, 'farm/guidance.html')
