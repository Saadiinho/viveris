# invites/views.py

from django.core.mail import send_mail
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def invite_friend(request):
    user = request.user  # The logged-in user
    friend_email = request.data.get('email')
    if not friend_email:
        return Response({"error": "No email provided"}, status=status.HTTP_400_BAD_REQUEST)

    # Compose the invitation email
    referral_code = user.referral_code  # from your User model
    subject = "Invitation à rejoindre SmartTri"
    # This link might be your app store link or a link to your website
    # that instructs them to download the app and sign up with the code
    message = (
        f"Bonjour,\n\n"
        f"{user.username} vous invite à rejoindre SmartTri !\n"
        f"Téléchargez l'application sur iOS ou Android.\n"
        f"Lorsque vous vous inscrivez, utilisez ce code de parrainage : {referral_code}\n\n"
        "Vous gagnerez 100 points, et votre ami aussi !\n"
        "Lien iOS: https://apps.apple.com/smarrtri)\n"
        "Lien Android: https://play.google.com/store/apps/smarttri \n\n"
        "À bientôt sur SmartTri !"
    )

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,  # e.g. "noreply@smarttri.com"
        [friend_email],
        fail_silently=False,
    )

    # Optionally store the invitation in a model if you want:
    # Invitation.objects.create(inviter=user, invitee_email=friend_email)

    return Response({"detail": "Invitation sent!"}, status=status.HTTP_200_OK)
