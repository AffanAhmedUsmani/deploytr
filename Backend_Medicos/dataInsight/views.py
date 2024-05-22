from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from .models import *
from .distance import *
from django.http import JsonResponse
from django.views.generic import View
from collections import defaultdict


class NearbyDoctorsAPI(APIView):
    def get(self, request, zipcode, format=None):
        try:
            central_lat, central_lon = get_lat_lon_from_zip(zipcode)

            doctors_dict = defaultdict(
                lambda: {
                    "id": None,
                    "name": "",
                    "specialties": "",
                    "locations": [],
                    "phone_numbers": set(),
                }
            )

            for doctor in Doctors.objects.all():
                doctor_info = doctors_dict[doctor.id]
                doctor_info["id"] = doctor.id
                doctor_info["name"] = doctor.name
                doctor_info["specialties"] = doctor.specialties

                addresses = doctor.addresses.all()
                for address in addresses:
                    if address.latitude and address.longitude:
                        distance = haversine(
                            central_lon, central_lat, address.longitude, address.latitude
                        )
                        if distance <= 100:
                            location = {
                                "latitude": address.latitude,
                                "longitude": address.longitude,
                            }
                            if location not in doctor_info["locations"]:
                                doctor_info["locations"].append(location)

                phone_numbers = [
                    phone.number
                    for phone in doctor.phone_numbers.all()
                    if phone.number and phone.number != "null"
                ]
                doctor_info["phone_numbers"].update(phone_numbers)

            # Convert sets to lists and prepare the final list of doctors
            nearby_doctors = []
            for doctor_id, data in doctors_dict.items():
                data["phone_numbers"] = list(data["phone_numbers"])  # Convert set to list
                nearby_doctors.append(data)

            return Response(nearby_doctors)
        
        except:
            
            return Response({"message": "Invalid search term, please try something different"}, status=status.HTTP_400_BAD_REQUEST)


class DoctorDetailView(APIView):
    def get(self, request, doctor_id, format=None):
        try:
            doctor = Doctors.objects.get(pk=doctor_id)
        except :
            return Response({"message": "Invalid search term, please try something different"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = DoctorDetailSerializer(doctor)
        return Response(serializer.data)


class NearbyHospitalsAPI(APIView):
    def get(self, request, zipcode, format=None):
        try:
            central_lat, central_lon = get_lat_lon_from_zip(zipcode)
            nearby_hospitals = []
            for hospital in Hospital.objects.all():
                if hospital.latitude and hospital.longitude:
                    distance = haversine(
                        central_lon, central_lat, hospital.longitude, hospital.latitude
                    )
                    if distance <= 100:
                        nearby_hospitals.append(
                            {
                                "id": hospital.id,
                                "name": hospital.name,
                                "address": hospital.address,
                                "latitude": hospital.latitude,
                                "longitude": hospital.longitude,
                                "hospital_types": hospital.hospital_types,
                                "qualities": hospital.qualities,
                                "provider_number": hospital.provider_number,
                            }
                        )

            return Response(nearby_hospitals)
        except:
                return Response({"message": "Invalid search term, please try something different"}, status=status.HTTP_400_BAD_REQUEST)



class HospitalDetailView(View):
    def get(self, request, hospital_id):
        try:
            hospital = Hospital.objects.get(id=hospital_id)
            serializer = HospitalSerializer(hospital)
            return JsonResponse(serializer.data)
        except :
            return Response({"message": "Invalid search term, please try something different"}, status=status.HTTP_400_BAD_REQUEST)



class NearbyPlansAPI(APIView):
    def get(self, request, zipcode, plan_type, format=None):
        try:
            central_lat, central_lon = get_lat_lon_from_zip(zipcode)
            nearby_plans = []
            for plan in PlanOverview.objects.filter(plan_type=plan_type):
                addresses = PlanAddresses.objects.filter(plan=plan)
                for address in addresses:
                    if address.latitude and address.longitude:
                        distance = haversine(
                            central_lon, central_lat, address.longitude, address.latitude
                        )

                        if distance <= 100:
                            # Fetch benefits and costs related to the plan
                            benefits_costs = BenefitsAndCosts.objects.filter(plan=plan).first()
                            extra_benefits = ExtraBenefits.objects.filter(plan=plan).first()
                            # Construct response data
                            plan_data = {
                                "id": plan.id,
                                "plan_name": plan.plan_name,
                                "plan_type": plan.plan_type,
                                "plan_id": plan.plan_id,
                                "latitude": address.latitude,
                                "longitude": address.longitude,
                                "benefits_and_costs": [],
                            }

                            
                            if benefits_costs:
                                plan_data["benefits_and_costs"].append(
                                    {
                                        "total_monthly_premiums": benefits_costs.total_monthly_premiums,
                                        "health_premiums": benefits_costs.health_premiums,
                                        "drug_premiums": benefits_costs.drug_premiums,
                                        "standard_part_b_premiums": benefits_costs.standard_part_b_premiums,
                                        "part_b_premium_reductions": benefits_costs.part_b_premium_reductions,
                                        "health_deductibles": benefits_costs.health_deductibles,
                                        "drug_deductibles": benefits_costs.drug_deductibles,
                                        "max_pay_for_health_services": benefits_costs.max_pay_for_health_services,
                                    }
                                )

                            
                            if extra_benefits:
                                extra_benefits_data = {
                                    field.name: ("$0 copay" in getattr(extra_benefits, field.name))
                                    for field in extra_benefits._meta.fields
                                    if field.name != 'plan'  # Exclude 'plan' field from the loop
                                }
                                plan_data["extra_benefits"] = extra_benefits_data
                                
                            nearby_plans.append(plan_data)

            return Response(nearby_plans)
        except Exception as e:
            return Response({"message": f"{e}Invalid search term, please try something different"}, status=status.HTTP_400_BAD_REQUEST)




class PlanDetailView(APIView):
    def get(self, request, id):
        try:
            plan = PlanOverview.objects.filter(id=id).first()
            if not plan:
                return Response({'message': 'Plan not found'}, status=status.HTTP_404_NOT_FOUND)
            
            serializer = CompletePlanSerializer(plan)
            return Response(serializer.data)
        except:
            return Response({"message": "Invalid search term, please try something different"}, status=status.HTTP_400_BAD_REQUEST)



class LocationList(APIView):
    def get(self, request):
        locations = Location.objects.all()
        serializer = LocationSerializer(locations, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = LocationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
