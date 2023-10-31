from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from . serializers import *
from . send_email import *
from rest_framework.exceptions import APIException, NotFound
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes


'''API documentation Link -----> https://documenter.getpostman.com/view/24033907/2s9YXb9kUg'''

# Create your views here.



class User_register(generics.GenericAPIView):

    serializer_class = user_registration

    def post(self, request):

        serializer = user_registration(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()

            response = {
                'status': status.HTTP_200_OK,
                'message': "Sucessfully Registerd",
                'result': serializer.data,
                
            }

            return Response(response)
        
        return Response({
            'status': status.HTTP_400_BAD_REQUEST,
            'errors': serializer.errors
        })


class User_login(generics.GenericAPIView):

    serializer_class = login_serilalizer   

    def post(self, request):

        serializer = login_serilalizer(data=request.data)

        if serializer.is_valid():

            user = custom_usermodel.objects.filter(email = serializer.data.get("email")).first()
            
            if not user:
                raise APIException("invalid credentails..!")
            
            if not user.check_password(serializer.data.get("password")):
                    raise APIException("invalid Password..!")
            
            if not user.is_blocked:

                refresh = RefreshToken.for_user(user)
                otp_response = send_otp(request=request, user_email=user.email)
                response = {
                    'status': status.HTTP_200_OK,
                    'message':"succcesfully logined",
                    'OTP_result': otp_response,
                    'Tokens': {
                        'refresh_token': str(refresh),
                        'access_token': str(refresh.access_token)
                    }
                    
                }

                return Response(response)
            
            else:
                return Response({
                'status': status.HTTP_400_BAD_REQUEST,
                'message': "Your account has been Blocked By admin. Please contact Him"
            })
            
        return Response({
            'status': status.HTTP_400_BAD_REQUEST,
            'errors': serializer.errors
            })

class User_data(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get(self, request):
        serializer = UserSerializer(instance=request.user)
        user_details = serializer.data

        if 'profile_picture' in user_details:

            user_details['profile_picture'] = request.build_absolute_uri(request.user.profile_picture.url)
        
        return Response({
            'status': status.HTTP_200_OK,
            'UserData': user_details
        })
        

class OTP_Verification(generics.GenericAPIView):

    permission_classes=[AllowAny]
    serializer_class = OTPValidationSerializer

    def post(self, request):
        
        serializer = OTPValidationSerializer(data=request.data)

        if serializer.is_valid():
           
            try:
                otp_instance = OTP.objects.get(OTP_digit=serializer.data.get('OTP_digit'))

                if serializer.data.get('OTP_digit', None) != otp_instance.OTP_digit:
                    raise APIException("Invalid OTP ....!!")
                
                if otp_instance.expiry_time < timezone.now():
                    return Response({'message': 'OTP has expired'}, status=status.HTTP_400_BAD_REQUEST)

    
                otp_instance.is_verified = True
                otp_instance.author.is_active = True
                otp_instance.save()

                return Response({'message': 'OTP is valid and verified'}, status=status.HTTP_200_OK)
            except OTP.DoesNotExist:
                return Response({'message': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
                    
                    
        return Response({
            'status': status.HTTP_400_BAD_REQUEST,
            'errors': serializer.errors
            })
    
class Resend_OTP(generics.GenericAPIView):

    pagination_class = [IsAuthenticated]

    def get(self, request):

        try:

            otp_instance = OTP.objects.get(author=request.user)

            if otp_instance.request_times < 0:
                raise APIException({"error": "You have exceeded the limit for resending OTP"})
            
            otp_instance.request_times -= 1
            otp_instance.save()
            otp_response = send_otp(request=request, user_email=request.user.email)

            return Response({

                "Message": otp_response,

            })

        except OTP.DoesNotExist:
            raise APIException({'message': 'Invalid OTP'})  


class CreateTask(generics.CreateAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = CreateTaskSerializer

    def post(self, request):
        
        serializer = CreateTaskSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            serializer.save()

            return Response({
                'task': serializer.data,
                }, status=status.HTTP_201_CREATED)
        
        return Response({
            'status': status.HTTP_400_BAD_REQUEST,
            'errors': serializer.errors
        })    
    
class ViewTask(generics.ListAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = ListAllTaskSerializer

    def get(self, request):

        try:

            tasks_instance = Users_Task.objects.filter(user_id=request.user).order_by('-start_date')
            serializer = ListAllTaskSerializer(tasks_instance, many=True) 

            return Response(
                {
                    'status': status.HTTP_200_OK,
                    'result': serializer.data
                }
            )  
          
        except Users_Task.DoesNotExist:

            raise APIException({'erros':"Task Does Not Exists...!!!"})
        

class Edit_Task(generics.UpdateAPIView):

    pagination_class = [IsAuthenticated]
    serializer_class = EditTaskSerializer

    def put(self, request):

        try:

            Task_instance = Users_Task.objects.get(id=request.data['task_id'])
            serializer = EditTaskSerializer(instance=Task_instance, data=request.data)     
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'status':status.HTTP_200_OK,
                    'message':"sucessfully Updated",
                    'result': {
                        'updated task':serializer.data
                    }
                    })
            else:
                return Response({
                    'status':status.HTTP_400_BAD_REQUEST,
                    'error':serializer.errors
                    })
            
        except Users_Task.DoesNotExist:
            raise APIException({"error":"Task Not Found.......!!!"})       


class Delete_Task(generics.DestroyAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = DeleteTaskSerializer

    def delete(self, request):

        try:
            serializer = DeleteTaskSerializer(data=request.data)
            if serializer.is_valid():

                Users_Task.objects.get(id=serializer.data.get('task_id')).delete()
                
                return Response(
                    {
                        'status': status.HTTP_200_OK,
                        'message':'Deleted Successfully',
                    })
            else:
                return Response(
                    {
                        'status': status.HTTP_400_BAD_REQUEST,
                        'errors':serializer.errors
                    },
                )
        except Users_Task.DoesNotExist:

            raise APIException({"ERROR":"Task doesn't Found...!!"})


