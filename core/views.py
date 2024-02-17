from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from .forms import CustomUserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from .models import Project, News
from question.models import SurveyResult
from .stock import StockAnalyzer
# Create your views here.



def loading(request):
    return render(request, 'index.html')

def home(request):
    if request.user.is_authenticated:
        # Kullanıcının anket sonucunu kontrol et
        try:
            survey_result = SurveyResult.objects.get(user=request.user)
            # Anket sonucu varsa, ana sayfaya yönlendir
            return render(request, 'home.html', {'show_navbar': True})
        except SurveyResult.DoesNotExist:
            # Anket sonucu yoksa, anket sayfasına yönlendir
            return redirect('questionaire')
    else:
        return render(request, 'home.html',  {'show_navbar': True})


def sign_up(request):
    if request.method == 'POST':
        username = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            return render(request, 'signup.html', {'error_message': 'Username already exists'})
        elif User.objects.filter(email=email).exists():
            return render(request, 'signup.html', {'error_message': 'Email already exists'})
        
        user = User.objects.create(username=username, email=email)
        user.set_password(password)
        user.save()

        login(request, user)
        return redirect('home')
    return render(request, 'signup.html')

def sign_in(request):
    error_message = None

    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            error_message = "Invalid email or password."

    return render(request, 'signin.html', {'error_message': error_message})

def account(request):
    return render(request, 'account.html')

def logout_view(request):
    logout(request)
    # Çıkış yapıldıktan sonra kullanıcıyı ana sayfaya yönlendir
    return redirect('home')

def sign_up_mailli(request):
    if request.method == 'POST':
        username = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Kullanıcı adı veya e-posta zaten varsa hata mesajı döndür
        if User.objects.filter(username=username).exists():
            return render(request, 'signup.html', {'error_message': 'Username already exists'})
        elif User.objects.filter(email=email).exists():
            return render(request, 'signup.html', {'error_message': 'Email already exists'})

        # Yeni kullanıcı oluştur
        user = User.objects.create_user(username=username, email=email, password=password)
        
        # Kullanıcıyı otomatik olarak giriş yap
        login(request, user)

        # Hoş geldiniz e-postası gönder
        send_welcome_email(user.email)

        # Ana sayfaya yönlendir
        return redirect('home')
    return render(request, 'signup.html')

def send_welcome_email(email):
    subject = 'Welcome to Our Website'
    message = 'Hi there, welcome to our website. We are glad to have you with us.'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email,]
    
    send_mail(subject, message, email_from, recipient_list)

def questionaire(request):
    return render(request, 'questionaire.html')

def dashboard_view(request):
    # Assuming Project and News models exist as shown
    projects = Project.objects.all()
    news_articles = News.objects.all().order_by('-created_at')[:5]

    # Sector Results initialized
    sector_results = {"Technology": [], "Consumer Products": [], "Industrial": []}

    # Example usage with tickers categorized by sector
    ticker_sectors = {
        "AAPL": "Technology",
        "MSFT": "Technology",
        "NVDA": "Technology",
        "WMT": "Consumer Products",
        "MC.PA": "Consumer Products",
        "KO": "Consumer Products",
        "AIR": "Industrial",
        "SAF.PA": "Industrial",
        "GE": "Industrial"
    }

    # Define weights and tickers for analysis
    aggressive_weights = {
        "Stock Price": 0.05,  
        "Dividends": 0.05,      
        "P/E Ratio": 0.10,  
        "Transaction Volume": 0.05,     
        "P/B Ratio": 0.20,  
        "Revenue Growth": 0.30,      
        "Profit Margin": 0.10,          
        "Sector Beta": 0.15              
    }
    tickers_example = list(ticker_sectors.keys())
    analyzer = StockAnalyzer(tickers_example, aggressive_weights)
    analyzer.fetch_and_score_stocks()
    results = analyzer.results

    # Categorize results by sector
    for ticker, data in results.items():
        sector = ticker_sectors.get(ticker, "Unknown")
        stock_data = {
            "ticker_name": ticker,
            "price": round(data["Data"]['Stock Price'], 2),
            "change": round(data["Data"]["Percentage Change for the Day"], 2)
        }
        sector_results[sector].append(stock_data)

    return render(request, 'dashboard.html', {
        'projects': projects,
        'news_articles': news_articles,
        'sector_results': sector_results,
        'show_navbar': False,
    })

def news_detail(request, slug):
    # Fetch the news article by slug or return 404
    news = get_object_or_404(News, slug=slug)
     # Görüntülenme sayısını artır
    news.views += 1
    news.save(update_fields=['views'])

    return render(request, 'news_detail.html', {'news': news})