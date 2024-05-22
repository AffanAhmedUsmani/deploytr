# location/serializers.py
from rest_framework import serializers
from .models import *



class PlanOverviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanOverview
        fields = '__all__'

class BenefitsAndCostsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BenefitsAndCosts
        fields = '__all__'

class DrugCoverageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DrugCoverage
        fields = '__all__'

class ExtraBenefitsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtraBenefits
        fields = '__all__'

class PlanAddressesSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanAddresses
        fields = '__all__'



class CompletePlanSerializer(serializers.ModelSerializer):
    benefits_and_costs = BenefitsAndCostsSerializer(source='benefitsandcosts', read_only=True)
    drug_coverage = DrugCoverageSerializer(source='drugcoverage_set', many=True, read_only=True)
    extra_benefits = ExtraBenefitsSerializer(source='extrabenefits', read_only=True)
    plan_addresses = PlanAddressesSerializer(source='planaddresses', read_only=True)

    class Meta:
        model = PlanOverview
        fields = ['plan_name', 'plan_type', 'plan_id', 'non_members_number', 'members_number', 
                  'benefits_and_costs', 'drug_coverage', 'extra_benefits', 'plan_addresses']




class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = "__all__"


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ["address_line", "latitude", "longitude"]


class PhoneNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhoneNumber
        fields = ["number"]


class DoctorDetailSerializer(serializers.ModelSerializer):
    addresses = AddressSerializer(many=True, read_only=True)
    phone_numbers = PhoneNumberSerializer(many=True, read_only=True)

    class Meta:
        model = Doctors
        fields = [
            "id",
            "name",
            "specialties",
            "consetion",
            "educations",
            "genders",
            "zipcode",
            "addresses",
            "phone_numbers",
        ]


class HospitalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hospital
        fields = "__all__"
