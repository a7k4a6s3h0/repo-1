from datetime import date, timezone
import django.utils
import rest_framework
from . models import *
from . data_validation_fun import Data_validation

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = custom_usermodel
        fields = ('id', 'username', 'email', 'profile_picture', 'phone_number')

class user_registration(serializers.ModelSerializer):
    
    re_enter_password = serializers.CharField(write_only=True)
    
    class Meta:
        model = custom_usermodel
        fields = ('username', 'email', 'password', 're_enter_password', 'phone_number', 'profile_picture')
        write_only_fields = ('re_enter_password',)
        extra_kwargs = {'password': {'write_only': True}}

    def get_profile_picture_url(self, obj):
       
        request = self.context.get('request')
        
        if obj.profile_picture:
            
            return request.build_absolute_uri(obj.profile_picture.url)
        else:
            
            return None
  
    
    def create(self, validated_data):
        
        """
        Ensure that the email, password and phone number are in a valid format before saving to database
        """  

        validation_obj = Data_validation()
        validation_obj.email_validation(validated_data.get('email'))
        validation_obj.password_validation(validated_data.get('password'))

        password = validated_data.pop('password', None)
        # Remove the 're_enter_password' field from the validated_data dictionary
        password2 = validated_data.pop('re_enter_password', None)
        user_country = validation_obj.phone_number_validation(validated_data.get('phone_number'))
        instance = self.Meta.model(**validated_data)

        if password is not None:
            if password != password2:
                raise serializers.ValidationError({"error":"Both password is not matching"})
            instance.set_password(password)
            instance.country = user_country
            instance.is_active = False

        instance.save()
        return instance
    
class login_serilalizer(serializers.Serializer):

    email = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    def validate(self, attrs):
        """
        Ensure that the email and password are in a valid format
        """

        validation_obj = Data_validation()

        if 'email' in attrs:
            validation_obj.email_validation(attrs['email'])
        if 'password' in attrs:
           validation_obj.password_validation(attrs['password'])

        return attrs 


class OTPValidationSerializer(serializers.Serializer):
    
    OTP_digit = serializers.IntegerField(required=True)

    def validate_OTP_digit(self, value):
        
        if len(str(value)) != 4:
            raise serializers.ValidationError("OTP must be a 4-digit number.")
        
        if not str(value).isdigit():
            raise serializers.ValidationError("OTP must contain only numeric digits.")
        
        
        return value

class CreateTaskSerializer(serializers.ModelSerializer):

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("ongoing", "Ongoing"),
        ("completed", "Completed")
    )

    class Meta:
        model = Users_Task
        fields = ('task_title', 'task_description', 'start_date', 'end_date', 'status')


    def validate(self, data):

        start_date = data.get('start_date')
        end_date = data.get('end_date')

        if start_date >= end_date:
            raise serializers.ValidationError("Start date must be earlier than the end date.")

        now = date.today()
        if start_date < now:
            raise serializers.ValidationError("Start date should be in the future.")

        status_choices = [choice[0] for choice in self.STATUS_CHOICES]

        if data['status'] not in status_choices:
            raise serializers.ValidationError(f"'{data['status']}' is not a valid choice. Choices are: {', '.join(status_choices)}")
        
        return data
    
    def create(self, validated_data):
        request = self.context.get('request')
        user = custom_usermodel.objects.get(id=request.user.id)
        task_instance = Users_Task.objects.create(user_id=user, **validated_data)
        return task_instance
    
   
class EditTaskSerializer(serializers.ModelSerializer):

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("ongoing", "Ongoing"),
        ("completed", "Completed")
    )

    task_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Users_Task
        fields = ('task_id', 'task_title', 'task_description', 'start_date', 'end_date', 'status')
        write_only_fields = ('task_id',)

    def validate(self, data):

        start_date = data.get('start_date')
        end_date = data.get('end_date')

        if start_date >= end_date:
            raise serializers.ValidationError("Start date must be earlier than the end date.")

        now = date.today()
        if start_date < now:
            raise serializers.ValidationError("Start date should be in the future.")

        status_choices = [choice[0] for choice in self.STATUS_CHOICES]

        if data['status'] not in status_choices:
            raise serializers.ValidationError(f"'{data['status']}' is not a valid choice. Choices are: {', '.join(status_choices)}")
        
        return data     
    

    def update(self, instance, validated_data):

        instance.task_title = validated_data.get('task_title', instance.task_title)
        instance.task_description = validated_data.get('task_description', instance.task_description)
        instance.start_date = validated_data.get('start_date', instance.start_date)
        instance.end_date = validated_data.get('end_date', instance.end_date)
        instance.status = validated_data.get('status', instance.status)
        instance.save()

        return instance

class ListAllTaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = Users_Task
        exclude = ('user_id',)


    def to_representation(self, instance):
        representation = super().to_representation(instance)  

        if instance.end_date <= date.today() and instance.status != "completed":  

            representation["is_expired"] = True
            representation['message'] = f"Time is Over, But Your Task is still {instance.status}"

        return representation    


class DeleteTaskSerializer(serializers.Serializer):

    task_id = serializers.IntegerField(required=True)