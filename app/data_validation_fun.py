from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

import phonenumbers
from phonenumbers import geocoder
import re

from rest_framework import serializers

class Data_validation:

    def __init__(self) -> None:
        self.email = None
        self.phone_number = None
        self.password = None

    def __str__(self) -> str:
        return "Data_validation-obj"
    

    def email_validation(self, email: str):
        """
        Ensure that the email is in a valid format
        """
        if not re.match(r'^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$', email):
            raise serializers.ValidationError("Email address is not valid")
        self.email = email



    def password_validation(self, password: str):
        """
        Ensure that the password meets minimum requirements
        """
        if not re.match(r'^(?=.*\d)(?=.*[a-zA-Z])[a-zA-Z\d]{8,}$', password):
            raise serializers.ValidationError("Password must contain at least 8 characters, including both letters and digits")
        self.password = password



    def phone_number_validation(self, number: int):
        """
        Ensure that the mobile number is in a valid format
        """
        value = '+' + str(number)
        
        try:
            parsed_number = phonenumbers.parse(value, None)

            if not phonenumbers.is_valid_number(parsed_number):
                raise serializers.ValidationError("Mobile number is not valid, Please Check you Enter Contuntry code to")
            
            self.phone_number = number

            return geocoder.country_name_for_number(parsed_number, lang ='en')
        
        except ValidationError as e:
            raise serializers.ValidationError("Error validating phone number")
        

            
    def img_validation(self, value):
        max_size = 1024 * 1024  # 1 MB

        if value.size > max_size:
            raise serializers.ValidationError(_('The video file size should not exceed 1 MB.'))        
        
        
    def Blog_img_validator(self, value):
        max_size = 10 * 1024 * 1024  # 10 MB

        if value.size > max_size:
            raise ValidationError(_('The image file size should not exceed 10 MB.'))
        
        
    def Blog_video_file_validation(self, value):
        max_size = 50 * 1024 * 1024  # 50 MB
        if value.size > max_size:
            raise ValidationError(_('The video file size should not exceed 50 MB.'))


    def validate_title(self, value):
        if not value.isalpha():
            raise ValidationError("Title must only contain alphabetic characters.")
        

    def validate_content(self, value):
        if len(value) < 10:
            raise ValidationError("Content must be at least 10 characters long.")