from rest_framework import serializers
from account.models import MyUser
from django.utils.encoding import smart_str, DjangoUnicodeDecodeError, force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from .utils import Util

class UserRegistrationSerializer(serializers.ModelSerializer):
    
    password2= serializers.CharField(style={'input_type': 'password'}, write_only=True)
    
    class Meta:
        model = MyUser
        fields = ['email','name','password','password2','tc']

        extra_kwargs= {
            'password': {'write_only': True}
        }

    # Validating password and confrim password while Registration
    def validate(self, data):
        password= data.get('password')
        password2= data.get('password2')
        
        if password != password2:
            raise serializers.ValidationError("Password and confrim password doesn't match.")
        return data
    
    def create(self, validate_data):
        return MyUser.objects.create_user(**validate_data)
    
    

class UserLoginSerializer(serializers.ModelSerializer):
    email= serializers.EmailField(max_length=255)
    class Meta:
        model = MyUser
        fields = ['email', 'password']


class UserProfileSreializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ['id', 'name', 'email']

    
class SendPasswordResetEmailSreializer(serializers.Serializer):
    email= serializers.EmailField(max_length=255)
    class Meta:
        fields= ['email']
    
    def validate(self, data):
        email= data.get('email')
        if MyUser.objects.filter(email=email).exists():
            user = MyUser.objects.get(email=email)
            uid= urlsafe_base64_encode(force_bytes(user.id))
            print('Encoded UID: ', uid)
            token= PasswordResetTokenGenerator().make_token(user)
            print('Pasword reset token: ', token)
            link = 'http://localhost:3000/api/user/reset_password_email/'+uid+'/'+token
            print(link)
            body= 'Click following link to reset your password '+link
            data={
                'subject': 'Reset your password',
                'body': body,
                'to_email': user.email
            }
            # Send Email
            Util.send_email(data)
            return data
        else:
            raise serializers.ValidationError('You are not a register user')


class UserResetPasswordSreializer(serializers.Serializer):
    password= serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)
    password2= serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)
    class Meta:
        fields = ['password', 'password2']
        
    def validate(self, data):
        try:
            password= data.get('password')
            password2= data.get('password2')
            uid= self.context.get('uid')
            token=self.context.get('token')
            if password != password2:
                raise serializers.ValidationError("Password and confrim password doesn't match.")
            id= smart_str(urlsafe_base64_decode(uid))
            user= MyUser.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise serializers.ValidationError('Token is not valid or expired')
            user.set_password(password)
            user.save()
            return data
        except DjangoUnicodeDecodeError as identifier:
            PasswordResetTokenGenerator().check_token(user, token)
            raise serializers.ValidationError('Token is not valid or expired')