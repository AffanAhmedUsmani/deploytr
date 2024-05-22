from django.db import models
from django.conf import settings
import requests


def get_google_maps_location(address, api_key):
    """Helper function to get latitude and longitude from Google Maps API."""
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address, "key": api_key}
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data["status"] == "OK":
            results = data["results"][0]
            location = results["geometry"]["location"]
            return location["lat"], location["lng"]
        else:
            print("Geocoding failed with status:", data["status"])
            return None, None
    else:
        print("Request failed with status code:", response.status_code)
        return None, None


class Hospital(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    provider_number = models.CharField(max_length=20)
    zipcode = models.CharField(max_length=10)
    qualities = models.TextField()
    hospital_types = models.CharField(max_length=100)
    emergency_services = models.BooleanField(default=False)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.latitude or not self.longitude:
            api_key = settings.GOOGLE_MAPS_API_KEY
            latitude, longitude = get_google_maps_location(self.address, api_key)
            if latitude and longitude:
                self.latitude = latitude
                self.longitude = longitude
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Doctors(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    specialties = models.CharField(max_length=100, blank=True, null=True)
    consetion = models.CharField(max_length=100, blank=True, null=True)
    educations = models.CharField(max_length=100, blank=True, null=True)
    genders = models.CharField(max_length=100, blank=True, null=True)
    zipcode = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name


class Address(models.Model):
    doctor = models.ForeignKey(
        Doctors, related_name="addresses", on_delete=models.CASCADE
    )
    address_line = models.TextField()
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.latitude or not self.longitude:
            api_key = (
                settings.GOOGLE_MAPS_API_KEY
            )  # Use the API key from Django settings
            latitude, longitude = get_google_maps_location(self.address_line, api_key)
            if latitude and longitude:
                self.latitude = latitude
                self.longitude = longitude
        super().save(*args, **kwargs)

    def __str__(self):
        return self.doctor.name


class PhoneNumber(models.Model):
    doctor = models.ForeignKey(
        Doctors, related_name="phone_numbers", on_delete=models.CASCADE
    )
    number = models.CharField(max_length=20)

    def __str__(self):
        return self.doctor.name


class Location(models.Model):
    name = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return self.name


class PlanOverview(models.Model):
    plan_name = models.CharField(max_length=255)
    plan_type = models.CharField(max_length=100)
    plan_id = models.CharField(max_length=100, unique=True)
    non_members_number = models.CharField(max_length=100)
    members_number = models.CharField(max_length=100)

    def __str__(self):
        return self.plan_name


class BenefitsAndCosts(models.Model):
    plan = models.OneToOneField(
        PlanOverview, on_delete=models.CASCADE, primary_key=True
    )
    total_monthly_premiums = models.CharField(max_length=255)
    health_premiums = models.CharField(max_length=255)
    drug_premiums = models.CharField(max_length=255)
    standard_part_b_premiums = models.CharField(max_length=255)
    part_b_premium_reductions = models.CharField(max_length=255)
    health_deductibles = models.CharField(max_length=255)
    drug_deductibles = models.CharField(max_length=255)
    max_pay_for_health_services = models.CharField(max_length=255)


class DrugCoverage(models.Model):
    plan = models.ForeignKey(PlanOverview, on_delete=models.CASCADE)
    tier_level = models.IntegerField()
    initial_coverage_phases = models.CharField(max_length=255)
    gap_coverage_phases = models.CharField(max_length=255)
    catastrophic_coverage_phases = models.CharField(max_length=255)


class ExtraBenefits(models.Model):
    plan = models.OneToOneField(
        PlanOverview, on_delete=models.CASCADE, primary_key=True
    )
    primary_doctor_visits = models.CharField(max_length=255)
    specialists_visits = models.CharField(max_length=255)
    diagnostics_test_procedures = models.CharField(max_length=255)
    lab_services = models.CharField(max_length=255)
    diagnostic_radiology_services = models.CharField(max_length=255)
    outpatient_x_rays = models.CharField(max_length=255)
    emergency_cares = models.CharField(max_length=255)
    urgent_cares = models.CharField(max_length=255)
    inpatient_hospital_coverages = models.CharField(max_length=255)
    outpatient_hospital_coverages = models.CharField(max_length=255)
    skilled_nursing_facilities = models.CharField(max_length=255)
    preventive_services = models.CharField(max_length=255)
    ground_ambulances = models.CharField(max_length=255)
    occupational_therapy_visits = models.CharField(max_length=255)
    physical_therapy_visits = models.CharField(max_length=255)
    chemotherapy_drugs = models.CharField(max_length=255)
    other_part_b_drugs = models.CharField(max_length=255)
    part_b_insulins = models.CharField(max_length=255)
    hearing_exams = models.CharField(max_length=255)
    fitting_or_evaluations = models.CharField(max_length=255)
    hearing_aids = models.CharField(max_length=255)
    oral_exams = models.CharField(max_length=255)
    cleanings = models.CharField(max_length=255)
    fluoride_treatments = models.CharField(max_length=255)
    dental_x_rays = models.CharField(max_length=255)
    non_routine_services = models.CharField(max_length=255)
    diagnostic_services = models.CharField(max_length=255)
    restorative_services = models.CharField(max_length=255)
    endodontics = models.CharField(max_length=255)
    periodontics = models.CharField(max_length=255)
    extractions = models.CharField(max_length=255)
    prosthodontics_and_other_services = models.CharField(max_length=255)
    routine_eye_exams = models.CharField(max_length=255)
    contact_lenses = models.CharField(max_length=255)
    eyeglasses = models.CharField(max_length=255)
    eyeglasses_frames_only = models.CharField(max_length=255)
    eyeglasses_lenses_only = models.CharField(max_length=255)
    upgrades = models.CharField(max_length=255)


class PlanAddresses(models.Model):
    plan = models.OneToOneField(
        PlanOverview, on_delete=models.CASCADE, primary_key=True
    )
    plan_addresses = models.CharField(max_length=255)
    longitude = models.FloatField()
    latitude = models.FloatField()

    def save(self, *args, **kwargs):
        if not self.latitude or not self.longitude:
            api_key = (
                settings.GOOGLE_MAPS_API_KEY
            )  # Use the API key from Django settings
            latitude, longitude = get_google_maps_location(self.plan_addresses, api_key)
            if latitude and longitude:
                self.latitude = latitude
                self.longitude = longitude
        super().save(*args, **kwargs)

    def __str__(self):
        return self.plan.plan_name
