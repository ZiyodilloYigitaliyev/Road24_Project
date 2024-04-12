from rest_framework.decorators import api_view
from twilio.rest import Client
import random
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
import os 
from dotenv import load_dotenv

load_dotenv()

@api_view(['POST'])
def login(request):
    user = get_object_or_404(User, username=request.data['username'])
    if not user.check_password(request.data['password']):
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
    token, create = Token.objects.get_or_create(user=user)
    serializer = UserSerializer(instance=user)
    return Response({"token": token.key, "user": serializer.data})

@api_view(['POST'])
def signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        user = User.objects.get(username=request.data['username'])
        user.set_password(request.data['password'])
        user.save()
        token = Token.objects.create(user=user)
        return Response({"token": token.key, "user": serializer.data})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def test_token(request):
    return Response({"passed for {} ".format(request.user.email)})



@api_view(['POST'])
def register_user(request):
    phone_number = request.data.get('phone_number')
    if not phone_number:
        return JsonResponse({'error': 'Phone number is required'}, status=400)

    verification_code = ''.join(random.choices('0123456789', k=6))

    request.session['verification_code'] = verification_code

    twilio_client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))

    message = twilio_client.messages.create(
        body=f'Your verification code is: {verification_code}',
        twilio_number = os.getenv("TWILIO_PHONE_NUMBER"),
        to = phone_number
    )

    return JsonResponse({'message': 'Verification code sent successfully'}, status=200)