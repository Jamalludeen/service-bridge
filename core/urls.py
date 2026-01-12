from django.urls import path
from . import views

urlpatterns = [
    path("customer-register/", views.RegisterView.as_view(), {"role":"customer"}, name="customer_register"),
    path("professional-register/", views.RegisterView.as_view(), {"role":"professional"}, name="professional_register"),
    path("admin-register/", views.RegisterView.as_view(), {"role":"admin"}, name="admin_register"),
    path("verify-otp/", views.VerifyOTPView.as_view(), name="verify_otp"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("otp-new/", views.RequestNewOTPView.as_view(), name="new_otp"),

    # Utility endpoints (unchanged)
    path("change-password/", views.ChangePasswordView.as_view(), name="change_password"),
    path("forgot-password/", views.ForgotPasswordView.as_view(), name="forgot_password"),
    path("reset-password/", views.ResetPasswordView.as_view(), name="reset_password"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
]

