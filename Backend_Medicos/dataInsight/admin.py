from django.contrib import admin
from django import forms
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ManyToManyWidget
from .models import Hospital
from import_export.formats.base_formats import XLSX
from django.urls import path

from .models import *
import csv
from io import TextIOWrapper
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse


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


class HospitalResource(resources.ModelResource):

    class Meta:
        model = Hospital
        import_id_fields = ("name",)
        fields = (
            "name",
            "address",
            "provider_number",
            "zipcode",
            "qualities",
            "hospital_types",
            "emergency_services",
            "latitude",
            "longitude",
        )

    def before_save_instance(self, instance, using_transactions, dry_run):
        """Use Google Maps API for geocoding before saving."""
        if not dry_run and (instance.latitude is None or instance.longitude is None):
            api_key = "AIzaSyCNGy4xiZxYz8QVJDKXsGRlGxh0iBiyj_c"  # Replace with your actual API key
            latitude, longitude = get_google_maps_location(instance.address, api_key)
            if latitude and longitude:
                instance.latitude = latitude
                instance.longitude = longitude


class AddressInline(admin.TabularInline):
    model = Address
    extra = 1  # How many extra forms to show


class PhoneNumberInline(admin.TabularInline):
    model = PhoneNumber
    extra = 1


class HospitalAdmin(ImportExportModelAdmin):
    resource_class = HospitalResource
    list_display = (
        "name",
        "address",
        "provider_number",
        "zipcode",
        "hospital_types",
        "emergency_services",
        "latitude",
        "longitude",
    )
    formats = [XLSX]


class FileUploadForm(forms.Form):
    file = forms.FileField()


class DoctorAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "specialties",
        "consetion",
        "educations",
        "genders",
        "zipcode",
    ]
    inlines = [AddressInline, PhoneNumberInline]

    def get_urls(self):
        from django.urls import path

        urls = super().get_urls()
        my_urls = [
            path("upload-csv/", self.upload_csv),
        ]
        return my_urls + urls

    def upload_csv(self, request):
        if request.method == "POST":
            form = FileUploadForm(request.POST, request.FILES)
            if form.is_valid():
                self.handle_uploaded_file(request.FILES["file"])
                self.message_user(request, "File uploaded successfully.")
                return HttpResponseRedirect("..")
        else:
            form = FileUploadForm()
        payload = {"form": form}
        return TemplateResponse(request, "admin/csv_upload.html", payload)

    def handle_uploaded_file(self, f):
        file = TextIOWrapper(f.file, encoding="utf-8")
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            doctor_name = row.get("name")
            specialties = row.get("specialties")
            consetion = row.get("consetion")
            educations = row.get("educations")
            genders = row.get("genders")
            zipcode = row.get("zipcode")
            doctor_name = row["name"]
            doctor, created = Doctors.objects.update_or_create(
                name=doctor_name,
                defaults={
                    "specialties": specialties,
                    "consetion": consetion,
                    "educations": educations,
                    "genders": genders,
                    "zipcode": zipcode,
                },
            )
            address_1 = row["address_1"]
            if address_1:
                Address.objects.create(doctor=doctor, address_line=address_1)

            address_2 = row["address_2"]
            if address_2:
                Address.objects.create(doctor=doctor, address_line=address_2)

            phone_number_1 = row["provider number 1"]
            if phone_number_1:
                PhoneNumber.objects.create(doctor=doctor, number=phone_number_1)

            phone_number_2 = row["provider number 2"]
            if phone_number_2:
                PhoneNumber.objects.create(doctor=doctor, number=phone_number_2)


class BenefitsAndCostsInline(admin.StackedInline):
    model = BenefitsAndCosts
    extra = 1


class DrugCoverageInline(admin.TabularInline):
    model = DrugCoverage
    extra = 1


class ExtraBenefitsInline(admin.StackedInline):
    model = ExtraBenefits
    extra = 1


class PlanAddressesInline(admin.TabularInline):
    model = PlanAddresses
    extra = 1


class PlanOverviewAdmin(admin.ModelAdmin):
    list_display = [
        "plan_name",
        "plan_type",
        "plan_id",
        "non_members_number",
        "members_number",
    ]
    inlines = [
        BenefitsAndCostsInline,
        DrugCoverageInline,
        ExtraBenefitsInline,
        PlanAddressesInline,
    ]

    def get_urls(self):
        from django.urls import path

        urls = super().get_urls()
        my_urls = [
            path("upload-csv/", self.upload_csv),
        ]
        return my_urls + urls

    def upload_csv(self, request):
        if request.method == "POST":
            form = FileUploadForm(request.POST, request.FILES)
            if form.is_valid():
                self.handle_uploaded_file(request.FILES["file"])
                self.message_user(request, "CSV uploaded successfully!")
                return HttpResponseRedirect("..")
        else:
            form = FileUploadForm()
        payload = {"form": form}
        return TemplateResponse(request, "admin/csv_upload.html", payload)

    def handle_uploaded_file(self, f):
        file = TextIOWrapper(f.file, encoding="utf-8")
        csv_reader = csv.DictReader(file)
        for row in csv_reader:

            plan_overview, _ = PlanOverview.objects.update_or_create(
                plan_id=row["Plan ID"],
                defaults={
                    "plan_name": row["Plan Name"],
                    "plan_type": row["Plan Type"],
                    "non_members_number": row["Non-Members Number"],
                    "members_number": row["Members Number"],
                },
            )

            # Assuming there's one BenefitsAndCosts entry per PlanOverview
            BenefitsAndCosts.objects.update_or_create(
                plan=plan_overview,
                defaults={
                    "total_monthly_premiums": row["Total Monthly Premiums"],
                    "health_premiums": row["Health Premiums"],
                    "drug_premiums": row["Drug Premiums"],
                    "standard_part_b_premiums": row["Standard Part B Premiums"],
                    "part_b_premium_reductions": row["Part B Premium Reductions"],
                    "health_deductibles": row["Health Deductibles"],
                    "drug_deductibles": row["Drug Deductibles"],
                    "max_pay_for_health_services": row[
                        "Maximum Pay for Health Services"
                    ],
                },
            )

            # Handle DrugCoverage - assume multiple tiers can be defined for each plan
            for tier_level in range(
                1, 7
            ):  # Adjust the range based on possible tier levels
                tier_data_prefix = f"Tier {tier_level}"
                DrugCoverage.objects.update_or_create(
                    plan=plan_overview,
                    tier_level=tier_level,
                    defaults={
                        "initial_coverage_phases": row.get(
                            f"{tier_data_prefix} Initial Coverage Phases", ""
                        ),
                        "gap_coverage_phases": row.get(
                            f"{tier_data_prefix} Gap Coverage Phases", ""
                        ),
                        "catastrophic_coverage_phases": row.get(
                            f"{tier_data_prefix} Catastrophic Coverage Phases", ""
                        ),
                    },
                )

            ExtraBenefits.objects.update_or_create(
                plan=plan_overview,
                defaults={
                    "primary_doctor_visits": row["Primary Doctor Visits"],
                    "specialists_visits": row["Specialists Visits"],
                    "diagnostics_test_procedures": row[
                        "Diagnostics Test and Procedures"
                    ],
                    "lab_services": row["Lab Services"],
                    "diagnostic_radiology_services": row[
                        "Diagnostic Radiology Services"
                    ],
                    "outpatient_x_rays": row["Outpatient X-rays"],
                    "emergency_cares": row["Emergency Cares"],
                    "urgent_cares": row["Urgent Cares"],
                    "inpatient_hospital_coverages": row["Inpatient Hospital Coverages"],
                    "outpatient_hospital_coverages": row[
                        "Outpatient Hospital Coverages"
                    ],
                    "skilled_nursing_facilities": row["Skilled Nursing Facilities"],
                    "preventive_services": row["Preventive Services"],
                    "ground_ambulances": row["Ground Ambulances"],
                    "occupational_therapy_visits": row["Occupational Therapy Visits"],
                    "physical_therapy_visits": row[
                        "Physical Therapy and Speech and Language Therapy Visits"
                    ],
                    "chemotherapy_drugs": row["Chemotherapy Drugs"],
                    "other_part_b_drugs": row["Other Part B Drugs"],
                    "part_b_insulins": row["Part B Insulins"],
                    "hearing_exams": row["Hearing Exams"],
                    "fitting_or_evaluations": row["Fitting or Evaluations"],
                    "hearing_aids": row["Hearing Aids"],
                    "oral_exams": row["Oral Exams"],
                    "cleanings": row["Cleanings"],
                    "fluoride_treatments": row["Fluoride Treatments"],
                    "dental_x_rays": row["Dental X-rays"],
                    "non_routine_services": row["Non-routine Services"],
                    "diagnostic_services": row["Diagnostic Services"],
                    "restorative_services": row["Restorative Services"],
                    "endodontics": row["Endodontics"],
                    "periodontics": row["Periodontics"],
                    "extractions": row["Extractions"],
                    "prosthodontics_and_other_services": row[
                        "Prosthodontics and Other Services"
                    ],
                    "routine_eye_exams": row["Routine Eye Exams"],
                    "contact_lenses": row["Contact Lenses"],
                    "eyeglasses": row["Eyeglasses"],
                    "eyeglasses_frames_only": row["Eyeglasses Frames Only"],
                    "eyeglasses_lenses_only": row["Eyeglasses Lenses Only"],
                    "upgrades": row["Upgrades"],
                },
            )
            address_1 = row["Plan Addresses"]
            if address_1:
                PlanAddresses.objects.get_or_create(
                    plan=plan_overview, defaults={"plan_addresses": address_1}
                )


admin.site.register(PlanOverview, PlanOverviewAdmin)
admin.site.register(Doctors, DoctorAdmin)
# admin.site.register(Address)
# admin.site.register(PhoneNumber)
admin.site.register(Hospital, HospitalAdmin)
# admin.site.register(Quality)  # If you want to manage qualities directly from admin
