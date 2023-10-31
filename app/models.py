from djongo import models
from . manager import UserManager
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from . data_validation_fun import *

# Create your models here.
# from django.db import models

class custom_usermodel(AbstractUser):

    validate = Data_validation()
    email = models.CharField(null=False, unique=True, max_length=50)
    profile_picture = models.ImageField(upload_to='images/', default='default-img/unknown.jpg', validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg']), validate.img_validation])
    phone_number = models.BigIntegerField(unique=True, null=False)
    is_blocked = models.BooleanField(default=False, null=False)
    country = models.CharField(null=False, max_length=50)


    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username',"phone_number"]


    def __str__(self) -> str:
        return self.username
    
class OTP(models.Model):
    author = models.ForeignKey(custom_usermodel, on_delete=models.CASCADE, related_name="reverse_user")
    OTP_digit = models.BigIntegerField(null=False, unique=True)    
    created_time = models.DateTimeField(auto_now_add = True)
    expiry_time = models.DateTimeField(null=False)
    is_verified = models.BooleanField(default=False)
    request_times = models.IntegerField(default=3)
    
    class Meta:

        ordering = ["-created_time"]

    def __str__(self) -> str:
        return f"obj - {self.author.username} - {self.id}"  
    

class Users_Task(models.Model):

    user_id = models.ForeignKey(custom_usermodel, on_delete=models.CASCADE, related_name="task")
    task_title = models.CharField(max_length=120, unique=True)
    task_description = models.TextField(max_length=300, unique=True)
    start_date = models.DateField(null=False)
    end_date = models.DateField(null=False)
    status = models.CharField(choices=(("pending", "Pending"), ("ongoing","Ongoing"), ("completed", "completed")), default='Not Started', max_length=20)
    updated_on = models.DateTimeField(auto_now_add = True)

