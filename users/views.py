import json
import bcrypt
import jwt

from django.http      import JsonResponse
from django.views     import View
from django.db.models import Q

from users.models      import User, Position, ApplyList
from users.validations import email_validation, phone_validation, password_validation
from users.utils       import login_required
from companies.models  import Notification

from my_settings import SECRET_KEY, algorithm

class SignUpView(View):
    def post(self, request):
        try:
            data         = json.loads(request.body)
            email        = data['email']
            password     = data['password']
            name         = data['name']
            phonenumber  = data['phonenumber']
            position     = data['position']

            if User.objects.filter(email=email).exists():
                return JsonResponse({'MESSAGE': 'ALREADY_EXISTS_USER'}, status=401)

            if not email_validation(email):
                return JsonResponse({'MESSAGE': 'INVALID_EMAIL'}, status=400)

            if not password_validation(password):
                return JsonResponse({'MESSAGE': 'INVALID_PASSWORD'}, status=400)

            if not phone_validation(phonenumber):
                return JsonResponse({'MESSAGE': 'INVALID_NUMBER'}, status=400)
            
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            User.objects.create(
                    email       = email,
                    password    = hashed_password,
                    name        = name,
                    phonenumber = phonenumber,
                    position_id = Position.objects.get(name=position).id
                    )
            return JsonResponse({'MESSAGE': 'SUCCESS'}, status=201)

        except KeyError:
            return JsonResponse({'MESSAGE': "KEY_ERROR"}, status=400)

class EmailCheckView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)

            email = data['email']

            if not email_validation(email):
                return JsonResponse({'MESSAGE': 'INVALID_EMAIL'}, status=400)

            if not User.objects.filter(email=email).exists():
                return JsonResponse({'MESSAGE': 'ACCOUNT_NOT_EXIST'}, status=401)

            return JsonResponse({'MESSAGE': 'SUCCESS'}, status=200)

        except KeyError:
            return JsonResponse({'MESSAGE': "KEY_ERROR"}, status=400)

class SignInView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)

            email = data['email']
            password = data['password']

            user = User.objects.get(email=email)
            
            if not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
                return JsonResponse({'MESSAGE': 'INCORRECT_PASSWORD'}, status=400)

            access_token = jwt.encode({'user_id': user.id}, SECRET_KEY, algorithm = algorithm)

            return JsonResponse({'MESSAGE':'SUCCESS', 'TOKEN': access_token}, status=200)

        except KeyError:
            return JsonResponse({'MESSAGE': "KEY_ERROR"}, status=400)

class ApplyView(View):
    @login_required
    def get(self, request):
        try:
            user            = request.user
            notification_id = request.GET['notification']

            if not Notification.objects.filter(id=notification_id).exists():
                return JsonResponse({'MESSAGE':'INVALID_NOTIFICATION_ID'}, status=401)

            if not ApplyList.objects.filter(user_id = user.id, notification_id = notification_id).exists():
                return JsonResponse({'MESSAGE': 'SUCCESS'}, status=200)

            return JsonResponse({'MESSAGE': 'ALREADY_APPLY'}, status=400)
        
        except KeyError:
            return JsonResponse({'MESSAGE': "KEY_ERROR"}, status=400)

        except ValueError:
            return JsonResponse({'MESSAGE': "VALUE_ERROR"}, status=400)

    @login_required
    def post(self, request):
        data = json.loads(request.body)

        user            = request.user
        notification_id = data['notification_id']

        ApplyList.objects.create(user_id = user.id, notification_id = notification_id)

        return JsonResponse({'MESSAGE': 'SUCCESS'}, status=200)

class ApplylistView(View):
    @login_required
    def get(self, request):
        user = request.user
        
        applylists = ApplyList.objects.filter(user_id = user.id)

        user_applylists = [
                {
                    'img'  : applylist.notification.image_set.all().first().image_url,
                    'company_name'   : applylist.notification.company.name,
                    'apply_position' : '웹 개발자',
                    'apply_date'     : applylist.created_at.strftime('%Y-%m'),
                    'apply_status'   : '접수'
                    } for applylist in applylists]

        return JsonResponse({'MESSAGE': 'SUCCESS', 'APPLYLIST' : user_applylists }, status=200)
