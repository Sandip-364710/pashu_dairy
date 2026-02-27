from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.utils import timezone
from datetime import timedelta


class CustomUserManager(BaseUserManager):
    def create_user(self, mobile, name, village, password=None, **extra_fields):
        if not mobile:
            raise ValueError('મોબાઇલ નંબર આવશ્યક છે')
        
        user = self.model(
            mobile=mobile,
            name=name,
            village=village,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user


class CustomUser(AbstractUser):
    # આ લાઇન ઉમેરો જેથી username ફિલ્ડ નીકળી જાય
    username = None 
    
    mobile = models.CharField(max_length=10, unique=True, verbose_name='મોબાઇલ નંબર')
    village = models.CharField(max_length=100, verbose_name='ગામ')
    name = models.CharField(max_length=100, verbose_name='નામ')
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'mobile'  # હવે લોગિન માટે મોબાઇલ નંબર વપરાશે
    REQUIRED_FIELDS = ['name', 'village']
    
    class Meta:
        verbose_name = 'વપરાશકર્તા'
        verbose_name_plural = 'વપરાશકર્તાઓ'
    
    def __str__(self):
        return f"{self.name} ({self.mobile})"


class Animal(models.Model):
    ANIMAL_TYPES = [
        ('cow', 'ગાય'),
        ('buffalo', 'ભેંસ'),
    ]
    
    BREED_CHOICES = [
        # Cow breeds
        ('gir', 'ગીર'),
        ('sahiwal', 'સાહિવાલ'),
        ('holstein', 'હોલ્સ્ટેન'),
        ('jersey', 'જર્સી'),
        ('kankrej', 'કાંકરેજ'),
        # Buffalo breeds
        ('murrah', 'મુરાહ'),
        ('jafarabadi', 'જાફરાબાદી'),
        ('mehsani', 'મહેસાણી'),
        ('banni', 'બન્ની'),
    ]
    
    CHECKUP_STATUS_CHOICES = [
        ('pending', 'બાકી'),
        ('positive', 'સકારાત્મક'),
        ('negative', 'નકારાત્મક'),
    ]
    
    tag_no = models.CharField(max_length=20, unique=True, verbose_name='ટેગ નંબર')
    animal_type = models.CharField(max_length=10, choices=ANIMAL_TYPES, verbose_name='પ્રાણી પ્રકાર')
    breed = models.CharField(max_length=20, choices=BREED_CHOICES, verbose_name='જાત')
    insemination_date = models.DateField(verbose_name='બીજદાનની તારીખ')
    checkup_status = models.CharField(max_length=10, choices=CHECKUP_STATUS_CHOICES, default='pending', verbose_name='તપાસ સ્થિતિ')
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='માલિક')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'પ્રાણી'
        verbose_name_plural = 'પ્રાણીઓ'
    
    def __str__(self):
        return f"{self.get_animal_type_display()} - {self.tag_no}"
    
    @property
    def checkup_date(self):
        """Calculate check-up date (insemination + 75 days)"""
        return self.insemination_date + timedelta(days=90)
    
    @property
    def expected_delivery_date(self):
        """Calculate expected delivery date"""
        if self.checkup_status == 'positive':
            days = 280 if self.animal_type == 'cow' else 310
            return self.insemination_date + timedelta(days=days)
        return None
    
    @property
    def days_since_insemination(self):
        """Days since insemination"""
        return (timezone.now().date() - self.insemination_date).days
    
    @property
    def needs_checkup_alert(self):
        """Check if 75 days alert needed"""
        return self.checkup_status == 'pending' and self.days_since_insemination >= 90


class MilkRecord(models.Model):
    # સવાર અને સાંજ માટેના ઓપ્શન્સ
    SESSION_CHOICES = [
        ('morning', 'સવાર'),
        ('evening', 'સાંજ'),
    ]

    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, verbose_name='પ્રાણી')
    date = models.DateField(verbose_name='તારીખ')
    
    # નવું ફિલ્ડ: સવાર કે સાંજ
    session = models.CharField(
        max_length=10, 
        choices=SESSION_CHOICES, 
        default='morning', 
        verbose_name='સમય (સવાર/સાંજ)'
    )
    
    liters = models.DecimalField(max_digits=6, decimal_places=2, verbose_name='લીટર')
    price_per_liter = models.DecimalField(max_digits=6, decimal_places=2, verbose_name='દર પ્રતિ લીટર')
    total_amount = models.DecimalField(max_digits=8, decimal_places=2, editable=False, verbose_name='કુલ રકમ')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'દૂધ રેકોર્ડ'
        verbose_name_plural = 'દૂધ રેકોર્ડ્સ'
        ordering = ['-date', '-created_at'] # નવી એન્ટ્રી પહેલા દેખાશે
    
    def __str__(self):
        return f"{self.animal.tag_no} - {self.date} ({self.get_session_display()})"
    
    def save(self, *args, **kwargs):
        self.total_amount = self.liters * self.price_per_liter
        super().save(*args, **kwargs)
