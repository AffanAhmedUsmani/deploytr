from django.urls import path
from .views import *

urlpatterns = [
    path("locations/", LocationList.as_view(), name="location-list"),
    path(
        "api-v1/nearby-doctors/<str:zipcode>/",
        NearbyDoctorsAPI.as_view(),
        name="nearby-doctors",
    ),
    path(
        "api-v1/nearby-hospitals/<str:zipcode>/",
        NearbyHospitalsAPI.as_view(),
        name="nearby-hospitals",
    ),
    path(
        "api-v1/nearby-plans/<str:zipcode>/<str:plan_type>/",
        NearbyPlansAPI.as_view(),
        name="nearby-plans",
    ),
    path(
        "api-v1/hospital-detail/<int:hospital_id>/",
        HospitalDetailView.as_view(),
        name="hospital-detail",
    ),
    path(
        "api-v1/doctor-detail/<int:doctor_id>/",
        DoctorDetailView.as_view(),
        name="doctor-detail",
    ),
    
    
    path('api-v1/plan/<str:id>/', PlanDetailView.as_view(), name='plan-detail'),

]
