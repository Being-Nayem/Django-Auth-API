from rest_framework import serializers
from account.models import MyUser

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
