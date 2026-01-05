from django.urls import path
from . import views

urlpatterns = [
    # New Unified Auth Flow with 2FA
    path("auth/customer/initiate/", views.InitiateAuthView.as_view(), {"role": "customer"}, name="auth_customer_initiate"),
    path("auth/professional/initiate/", views.InitiateAuthView.as_view(), {"role": "professional"}, name="auth_professional_initiate"),
    path("auth/admin/initiate/", views.InitiateAuthView.as_view(), {"role": "admin"}, name="auth_admin_initiate"),
    path("auth/verify-otp/", views.VerifyAuthOTPView.as_view(), name="auth_verify_otp"),
    path("auth/complete-registration/", views.CompleteRegistrationView.as_view(), name="auth_complete_registration"),
    path("auth/authenticate/", views.AuthenticatePasswordView.as_view(), name="auth_authenticate"),
    path("auth/resend-otp/", views.ResendOTPView.as_view(), name="auth_resend_otp"),

    # Legacy endpoints (keep for backward compatibility)
    path("customer-register/", views.RegisterView.as_view(), {"role":"customer"}, name="customer_register"),
    path("professional-register/", views.RegisterView.as_view(), {"role":"professional"}, name="professional_register"),
    path("admin-register/", views.RegisterView.as_view(), {"role":"admin"}, name="admin_register"),
    path("verify-otp/", views.VerifyOTPView.as_view(), name="verify_otp"),
    path("login/", views.LoginView.as_view(), name="login"),

    # Utility endpoints (unchanged)
    path("change-password/", views.ChangePasswordView.as_view(), name="change_password"),
    path("forgot-password/", views.ForgotPasswordView.as_view(), name="forgot_password"),
    path("reset-password/", views.ResetPasswordView.as_view(), name="reset_password"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
]

