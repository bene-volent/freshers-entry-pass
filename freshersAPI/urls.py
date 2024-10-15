

from django.urls import path,include
from rest_framework.routers import SimpleRouter
from . import views

router = SimpleRouter(trailing_slash=False)
router.register('passes',views.EntryPassView,basename='passes')

urlpatterns = [
    path('passes/download',views.download,name="Download Passes Details"),
    path('passes/mark-attendance',views.mark_attendance,name="Mark Attendance"),
    path("passes/roll-no", views.redirect_to_passes, name="Redirect to Passes"),
    path('passes/roll-no/<str:roll_no>',views.EntryPassView.as_view({'get':'retrieve_by_roll_no'}),name="Get Pass by Roll No"),
    path('',include((router.urls,'Freshers API'),'freshersAPI')),
]
