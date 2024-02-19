from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import SurveyResult
import json

@csrf_exempt
def survey_result_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        print("Gelen veri:", data)
        total_score = data.get('total_score')
        profile = data.get('profile')

        # Kullanıcının anket sonucunu kaydet
        SurveyResult.objects.update_or_create(
            user=request.user,
            defaults={'total_score': total_score, 'profile': profile},
        )

        # Doğrudan URL'ye yönlendirme yapılıyor
        # return redirect('survey_result')
        return JsonResponse({"succes": "Basarili"}, status=200)

    else:
        return JsonResponse({"error": "Geçersiz istek"}, status=400)

@login_required
def survey_result(request):
    # Kullanıcının anket sonucunu al
    survey_result = get_object_or_404(SurveyResult, user=request.user)

    # Kullanıcıya özel mesaj ve anket sonuçları ile response döndür
    context = {
        'prenom': request.user.first_name,
        'nom': request.user.last_name,
        'score': survey_result.total_score,
        'profile': survey_result.profile,
    }
    return render(request, 'result.html', context)
