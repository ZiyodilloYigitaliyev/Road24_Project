from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from .serializers import UserSerializer 
import random
import os
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from dotenv import load_dotenv

load_dotenv()


@api_view(['POST'])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')
    phone_number = request.data.get('phone_number')

    if not email or not password:
        return Response({'error': 'Please provide both identifier (email or phone number) and password'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get((email==email) | (phone_number==phone_number))
    except ObjectDoesNotExist:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_404_NOT_FOUND)

    if not user.check_password(password):
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_404_NOT_FOUND)

    token, _ = Token.objects.get_or_create(user=user)
    serializer = UserSerializer(user)
    phone_number = user.phone_number if hasattr(user, 'phone_number') else None
    return Response({"token": token.key, "user": serializer.data, "phone_number": phone_number})


@api_view(['POST'])
def signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        user.set_password(request.data['password'])
        user.save()  # Save password after setting


        email = request.data.get('email')
        phone_number = request.data.get('phone_number')


        if phone_number and User.objects.filter(phone_number=phone_number).exists():
            return Response({'error': 'Phone number already exists'}, status=status.HTTP_400_BAD_REQUEST)
        if email and User.objects.filter(email=email).exists():
            return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)

        # Implement logic to store verification code securely (e.g., database)
        # request.session['verification_code'] = verification_code  # Not recommended for production

        if phone_number:
            verification_code = ''.join(random.choices('0123456789', k=6))
            twilio_client = Client(os.getenv(''), os.getenv(''))
            try:
                message = twilio_client.messages.create(
                    body=f'Your verification code is: {verification_code}',
                    from_='',
                    to=phone_number
                )
            except TwilioRestException as e:
                return Response({'error': f'An error occurred sending SMS: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        token = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "user": serializer.data}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def test_token(request):
    return Response({"message": f"Hello, {request.user.email}"})
