from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from .forms import CustomUserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from .models import Project, News
from question.models import SurveyResult
from .stockAnalyzer import AggressiveStockAnalyzer, ConservativeStockAnalyzer, ModerateStockAnalyzer
# Create your views here.
import yfinance as yf
from .models import StockData


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

        # login(request, user)
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect('home')
    return render(request, 'signup.html')

def sign_in(request):
    error_message = None

    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, username=email, password=password, backend='django.contrib.auth.backends.ModelBackend')
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            error_message = "Invalid email or password."

    return render(request, 'signin.html', {'error_message': error_message})

def account(request):
    return render(request, 'account.html', {'show_navbar': True})

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

@login_required
def questionaire(request):
    return render(request, 'questionaire.html')

def fetch_and_save_stock_data():
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

    for ticker, sector in ticker_sectors.items():
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1d", interval="1m")

        if not hist.empty:
            current_price = hist['Close'].iloc[-1]
            open_price = hist['Open'].iloc[0]
            percentage_change = ((current_price - open_price) / open_price) * 100

            # Fetch additional info
            info = stock.info

            # Update or create the stock data object
            stock_data, created = StockData.objects.update_or_create(
                ticker=ticker,
                defaults={
                    'current_price': current_price,
                    'open_price': open_price,
                    'percentage_change': percentage_change,
                    'info': info,  # Directly assign if using JSONField
                    # 'info': json.dumps(info) if using TextField
                }
            )

            if created:
                print(f"Created new record for {ticker}")
            else:
                print(f"Updated record for {ticker}")

@login_required
def dashboard_view(request):
    # fetch_and_save_stock_data()
    # Assuming Project and News models exist as shown
    projects = Project.objects.all()
    news_articles = News.objects.all().order_by('-created_at')[:5]
    
    try:
        profile = get_object_or_404(SurveyResult, user=request.user).profile
    except SurveyResult.DoesNotExist:
        return redirect('questionaire')

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

    tickers_example = list(ticker_sectors.keys())
    if profile == 'Aggressive':
        analyzer = AggressiveStockAnalyzer(tickers_example)
        sector_results = {"Technology": [], "Consumer Products": [], "Industrial": []}
    elif profile == 'Conservative':
        analyzer =ConservativeStockAnalyzer(tickers_example)
        sector_results = {"Consumer Products": [], "Industrial": [], "Technology": []}
    elif profile == 'Moderate':
        analyzer = ModerateStockAnalyzer(tickers_example)
        sector_results = {"Consumer Products": [], "Industrial": [], "Technology": []}
    else:
        return redirect('questionaire')

    analyzer.fetch_and_score_stocks()
    results = analyzer.results

    sector_colors = {
        "Technology": "bg-gray-500",
        "Consumer Products": "bg-blue-500",
        "Industrial": "bg-yellow-500"
    }

    # Categorize results by sector
    for ticker, data in results.items():
        sector = ticker_sectors.get(ticker, "Unknown")
        stock_data = {
            "AllData": data["Data"]['AllData'],
            "company_name": ' '.join(data["Data"]['Name'].split()[:2]),
            "ticker_name": ticker,
            "price": round(data["Data"]['Stock Price'], 2),
            "change": round(data["Data"]["Percentage Change for the Day"], 2),
            "color": sector_colors.get(sector, "bg-gray-500")
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