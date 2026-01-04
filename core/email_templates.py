# core/email_templates.py

OTP_EMAIL_TEMPLATE = """<!DOCTYPE html>
<html lang="en" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OTP Verification</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;800&display=swap');
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Tajawal', sans-serif;
        }}
        
        body {{
            background-color: #f5f7fa;
            padding: 20px;
            direction: rtl;
        }}
        
        .email-container {{
            max-width: 600px;
            margin: 0 auto;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
        }}
        
        .header {{
            background: white;
            padding: 30px;
            text-align: center;
            border-bottom: 1px solid #f0f0f0;
        }}
        
        .logo {{
            width: 80px;
            height: 80px;
            margin: 0 auto 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 28px;
            font-weight: 800;
        }}
        
        .brand-name {{
            color: #333;
            font-size: 28px;
            font-weight: 800;
            margin-bottom: 10px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        
        .brand-subtitle {{
            color: #666;
            font-size: 16px;
            font-weight: 400;
        }}
        
        .content {{
            padding: 40px;
            background: white;
        }}
        
        .greeting {{
            color: #333;
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 20px;
            text-align: center;
        }}
        
        .message {{
            color: #555;
            font-size: 16px;
            line-height: 1.6;
            margin-bottom: 30px;
            text-align: center;
        }}
        
        .otp-container {{
            background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%);
            border-radius: 15px;
            padding: 25px;
            margin: 30px 0;
            border: 2px dashed #667eea;
            text-align: center;
        }}
        
        .otp-title {{
            color: #555;
            font-size: 16px;
            margin-bottom: 15px;
            font-weight: 500;
        }}
        
        .otp-code {{
            font-size: 48px;
            font-weight: 800;
            letter-spacing: 10px;
            color: #333;
            background: white;
            padding: 15px 30px;
            border-radius: 10px;
            display: inline-block;
            margin: 10px 0;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            border: 2px solid #e0e6ff;
        }}
        
        .otp-expiry {{
            color: #888;
            font-size: 14px;
            margin-top: 15px;
            font-weight: 500;
        }}
        
        .warning {{
            background: #fff8e1;
            border-left: 4px solid #ffc107;
            padding: 15px;
            border-radius: 8px;
            margin: 30px 0;
        }}
        
        .warning-title {{
            color: #333;
            font-weight: 700;
            margin-bottom: 5px;
        }}
        
        .warning-text {{
            color: #666;
            font-size: 14px;
        }}
        
        .footer {{
            background: #f8f9fa;
            padding: 30px;
            text-align: center;
            border-top: 1px solid #e9ecef;
        }}
        
        .social-links {{
            margin: 20px 0;
        }}
        
        .social-link {{
            display: inline-block;
            margin: 0 10px;
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
            font-size: 14px;
            transition: color 0.3s;
        }}
        
        .social-link:hover {{
            color: #764ba2;
        }}
        
        .social-icon {{
            width: 30px;
            height: 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 50%;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            color: white;
            margin-right: 8px;
            font-size: 14px;
        }}
        
        .copyright {{
            color: #888;
            font-size: 12px;
            margin-top: 20px;
        }}
        
        .button {{
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 30px;
            text-decoration: none;
            border-radius: 25px;
            font-weight: 600;
            margin: 10px 5px;
            transition: transform 0.3s;
        }}
        
        .button:hover {{
            transform: translateY(-2px);
        }}
        
        @media (max-width: 600px) {{
            .content {{
                padding: 20px;
            }}
            
            .otp-code {{
                font-size: 36px;
                letter-spacing: 8px;
                padding: 12px 20px;
            }}
            
            .greeting {{
                font-size: 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <div class="logo">👨‍💼</div>
            <h1 class="brand-name">پلتفورم هوشمند خدمت</h1>
            <p class="brand-subtitle">Smart Service Platform</p>
        </div>
        
        <div class="content">
            <h2 class="greeting">سلام کاربر عزیز!</h2>
            <p class="message">
                برای تکمیل فرآیند ثبت‌نام و تأیید هویت شما، لطفاً کد تأیید زیر را در برنامه وارد نمایید.
            </p>
            
            <div class="otp-container">
                <div class="otp-title">کد تأیید یکبار مصرف</div>
                <div class="otp-code">{otp}</div>
                <div class="otp-expiry">⏰ این کد تا {expiry_minutes} دقیقه دیگر معتبر است</div>
            </div>
            
            <div class="warning">
                <div class="warning-title">⚠️ نکات ایمنی</div>
                <div class="warning-text">
                    • این کد را در اختیار هیچ فردی قرار ندهید<br>
                    • کارمندان ما هرگز از شما درخواست کد تأیید نمی‌کنند<br>
                    • در صورت عدم درخواست این کد، لطفاً این ایمیل را نادیده بگیرید
                </div>
            </div>
            
            <div style="text-align: center; margin-top: 30px;">
                <a href="#" class="button">ورود به پنل کاربری</a>
                <a href="#" class="button" style="background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);">پشتیبانی آنلاین</a>
            </div>
        </div>
        
        <div class="footer">
            <div class="social-links">
                <a href="#" class="social-link">
                    <span class="social-icon">📘</span> فیسبوک
                </a>
                <a href="#" class="social-link">
                    <span class="social-icon">📷</span> اینستاگرام
                </a>
                <a href="#" class="social-link">
                    <span class="social-icon">💼</span> لینکدین
                </a>
                <a href="#" class="social-link">
                    <span class="social-icon">🐦</span> توییتر
                </a>
                <a href="#" class="social-link">
                    <span class="social-icon">📱</span> تلگرام
                </a>
            </div>
            
            <p class="copyright">
                © {current_year} پلتفورم هوشمند خدمت - تمامی حقوق محفوظ است<br>
                آدرس: کابل، افغانستان | تلفن: ۰۷۸۰ ۱۲۳ ۴۵۶۷ | ایمیل: info@smartservice.af
            </p>
        </div>
    </div>
</body>
</html>"""

WELCOME_EMAIL_TEMPLATE = """<!DOCTYPE html>
<html lang="en" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Welcome to Smart Service Platform</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;800&display=swap');
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Tajawal', sans-serif;
        }}
        
        body {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            direction: rtl;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .welcome-container {{
            max-width: 600px;
            margin: 0 auto;
            background: white;
            border-radius: 25px;
            overflow: hidden;
            box-shadow: 0 30px 80px rgba(0, 0, 0, 0.2);
        }}
        
        .confetti-top {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 150px;
            position: relative;
            overflow: hidden;
        }}
        
        .confetti-top::before {{
            content: "🎉";
            position: absolute;
            font-size: 60px;
            top: 20px;
            left: 20px;
            opacity: 0.3;
        }}
        
        .confetti-top::after {{
            content: "✨";
            position: absolute;
            font-size: 50px;
            top: 40px;
            right: 30px;
            opacity: 0.3;
        }}
        
        .welcome-header {{
            text-align: center;
            padding: 40px 30px 20px;
            position: relative;
            margin-top: -80px;
        }}
        
        .avatar-circle {{
            width: 120px;
            height: 120px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 50%;
            margin: 0 auto 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 5px solid white;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }}
        
        .avatar-emoji {{
            font-size: 50px;
            color: white;
        }}
        
        .welcome-title {{
            color: #333;
            font-size: 32px;
            font-weight: 800;
            margin-bottom: 10px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        
        .welcome-subtitle {{
            color: #666;
            font-size: 18px;
            margin-bottom: 30px;
        }}
        
        .welcome-content {{
            padding: 0 40px 40px;
        }}
        
        .greeting-box {{
            background: linear-gradient(135deg, #f8f9ff 0%, #f0f3ff 100%);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            border: 2px solid #e0e6ff;
            text-align: center;
        }}
        
        .user-greeting {{
            color: #333;
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 15px;
        }}
        
        .user-message {{
            color: #555;
            font-size: 16px;
            line-height: 1.6;
            margin-bottom: 20px;
        }}
        
        .user-name {{
            font-size: 28px;
            font-weight: 800;
            color: #667eea;
            display: block;
            margin: 10px 0;
        }}
        
        .features-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        
        .feature-card {{
            background: white;
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
            border: 1px solid #f0f0f0;
            transition: transform 0.3s;
        }}
        
        .feature-card:hover {{
            transform: translateY(-5px);
        }}
        
        .feature-icon {{
            width: 50px;
            height: 50px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 15px;
            color: white;
            font-size: 22px;
        }}
        
        .feature-title {{
            color: #333;
            font-weight: 700;
            margin-bottom: 8px;
        }}
        
        .feature-desc {{
            color: #666;
            font-size: 12px;
            line-height: 1.4;
        }}
        
        .cta-section {{
            text-align: center;
            margin: 40px 0 30px;
        }}
        
        .cta-button {{
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 40px;
            text-decoration: none;
            border-radius: 30px;
            font-weight: 700;
            font-size: 18px;
            box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
            transition: all 0.3s;
        }}
        
        .cta-button:hover {{
            transform: translateY(-3px);
            box-shadow: 0 15px 35px rgba(102, 126, 234, 0.4);
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin: 40px 0;
            background: #f8f9fa;
            border-radius: 15px;
            padding: 20px;
        }}
        
        .stat-item {{
            text-align: center;
        }}
        
        .stat-number {{
            font-size: 28px;
            font-weight: 800;
            color: #667eea;
            display: block;
        }}
        
        .stat-label {{
            font-size: 12px;
            color: #666;
            margin-top: 5px;
        }}
        
        .social-section {{
            background: #f8f9fa;
            border-radius: 20px;
            padding: 30px;
            margin-top: 30px;
            text-align: center;
        }}
        
        .social-title {{
            color: #333;
            font-size: 18px;
            font-weight: 700;
            margin-bottom: 20px;
        }}
        
        .social-icons {{
            display: flex;
            justify-content: center;
            gap: 15px;
            flex-wrap: wrap;
        }}
        
        .social-icon-circle {{
            width: 45px;
            height: 45px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            text-decoration: none;
            font-size: 20px;
            transition: transform 0.3s;
        }}
        
        .social-icon-circle:hover {{
            transform: scale(1.1);
        }}
        
        .footer-note {{
            text-align: center;
            padding: 30px;
            background: #2c3e50;
            color: white;
            border-radius: 0 0 25px 25px;
        }}
        
        .footer-logo {{
            font-size: 24px;
            font-weight: 800;
            margin-bottom: 10px;
        }}
        
        .footer-contact {{
            font-size: 14px;
            opacity: 0.8;
            margin-top: 15px;
        }}
        
        @media (max-width: 600px) {{
            .welcome-content {{
                padding: 0 20px 20px;
            }}
            
            .features-grid {{
                grid-template-columns: 1fr;
            }}
            
            .stats-grid {{
                grid-template-columns: 1fr;
            }}
            
            .confetti-top {{
                height: 100px;
            }}
        }}
    </style>
</head>
<body>
    <div class="welcome-container">
        <div class="confetti-top"></div>
        
        <div class="welcome-header">
            <div class="avatar-circle">
                <span class="avatar-emoji">👋</span>
            </div>
            <h1 class="welcome-title">پلتفورم هوشمند خدمت</h1>
            <p class="welcome-subtitle">Smart Service Platform</p>
        </div>
        
        <div class="welcome-content">
            <div class="greeting-box">
                <h2 class="user-greeting">خوش آمدید!</h2>
                <p class="user-message">
                    سلام <span class="user-name">{username}</span>،
                    <br>
                    به خانواده بزرگ <strong>پلتفورم هوشمند خدمت</strong> خوش آمدید! 
                    حساب کاربری شما با موفقیت ایجاد شد و اکنون می‌توانید از تمامی خدمات پلتفرم ما استفاده نمایید.
                </p>
                <div style="font-size: 14px; color: #4CAF50; margin-top: 10px;">
                    ✅ ایمیل شما تأیید شد | ✅ حساب شما فعال است | ✅ آماده استفاده!
                </div>
            </div>
            
            <div class="features-grid">
                <div class="feature-card">
                    <div class="feature-icon">🔍</div>
                    <h3 class="feature-title">جستجوی خدمات</h3>
                    <p class="feature-desc">صدها خدمت‌دهنده حرفه‌ای را بیابید</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">📅</div>
                    <h3 class="feature-title">رزرو نوبت</h3>
                    <p class="feature-desc">زمان مورد نظر خود را رزرو کنید</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">⭐</div>
                    <h3 class="feature-title">امتیازدهی</h3>
                    <p class="feature-desc">تجربه خود را به اشتراک بگذارید</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">💰</div>
                    <h3 class="feature-title">پرداخت امن</h3>
                    <p class="feature-desc">پرداخت‌های مطمئن و سریع</p>
                </div>
            </div>
            
            <div class="stats-grid">
                <div class="stat-item">
                    <span class="stat-number">۵۰۰+</span>
                    <span class="stat-label">خدمت‌دهنده</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">۱۰K+</span>
                    <span class="stat-label">کاربر فعال</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">۹۸٪</span>
                    <span class="stat-label">رضایت کاربران</span>
                </div>
            </div>
            
            <div class="cta-section">
                <a href="#" class="cta-button">شروع کار با پلتفرم 🚀</a>
            </div>
            
            <div class="social-section">
                <h3 class="social-title">ما را در شبکه‌های اجتماعی دنبال کنید</h3>
                <div class="social-icons">
                    <a href="#" class="social-icon-circle">📘</a>
                    <a href="#" class="social-icon-circle">📷</a>
                    <a href="#" class="social-icon-circle">💼</a>
                    <a href="#" class="social-icon-circle">🐦</a>
                    <a href="#" class="social-icon-circle">📱</a>
                </div>
            </div>
        </div>
        
        <div class="footer-note">
            <div class="footer-logo">پلتفورم هوشمند خدمت</div>
            <div style="font-size: 14px; opacity: 0.9; margin-top: 10px;">
                پلتفرم جامع ارائه خدمات حرفه‌ای در افغانستان
            </div>
            <div class="footer-contact">
                کابل، افغانستان | تلفن: ۰۷۸۰ ۱۲۳ ۴۵۶۷ | ایمیل: support@smartservice.af
                <br>
                © {current_year} تمامی حقوق محفوظ است
            </div>
        </div>
    </div>
</body>
</html>"""