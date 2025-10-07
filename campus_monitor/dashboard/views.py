from django.shortcuts import render
from django.http import JsonResponse
import json
import os

def index(request):
    return render(request, 'dashboard/index.html')

def search_page(request):
    return render(request, 'dashboard/search.html')

def timeline_page(request):
    return render(request, 'dashboard/timeline.html')

def predict_page(request):
    return render(request, 'dashboard/predict.html')

def alerts_page(request):
    return render(request, 'dashboard/alerts.html')

def api_search(request):
    with open(os.path.join(os.path.dirname(__file__), 'data', 'entities.json')) as f:
        data = json.load(f)
    return JsonResponse(data, safe=False)

def api_timeline(request):
    with open(os.path.join(os.path.dirname(__file__), 'data', 'timeline.json')) as f:
        data = json.load(f)
    return JsonResponse(data, safe=False)

def api_predict(request):
    with open(os.path.join(os.path.dirname(__file__), 'data', 'predictions.json')) as f:
        data = json.load(f)
    return JsonResponse(data, safe=False)

def api_alerts(request):
    with open(os.path.join(os.path.dirname(__file__), 'data', 'alerts.json')) as f:
        data = json.load(f)
    return JsonResponse(data, safe=False)
