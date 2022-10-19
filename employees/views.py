import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from employees.serializers import EmployeeSerializer
from .models import Company, Employee
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.utils import IntegrityError
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser


def login_request(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")

            user = authenticate(username=username, password=password)

            if user is not None:

                login(request, user)
                messages.info(request, f"You are now logged in as {username}")
                return redirect("employees")
            else:
                messages.error(request, "Invalid username or password")
        else:
            messages.error(request, "Invalid username or password.")
    form = AuthenticationForm()
    return render(
        request=request, template_name="login.html", context={"login_form": form}
    )


@login_required(login_url="login")
def employees(request):
    employees = Employee.objects.all()
    page = request.GET.get("page", 1)
    paginator = Paginator(employees, 5)
    try:
        employees = paginator.page(page)
    except PageNotAnInteger:
        employees = paginator.page(1)
    except EmptyPage:
        employees = paginator.page(paginator.num_pages)
    companies = Company.objects.all()
    return render(
        request,
        "employees.html",
        {"employees": employees, "companies": companies},
    )


@csrf_exempt
@login_required(login_url="login")
def add_employee(request):
    try:
        request.FILES["profile_pic"]
    except KeyError:
        messages.error(request, "Choose a picture")
        return JsonResponse({"message": "failed"})
    if request.method == "POST" and request.FILES["profile_pic"]:
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        company_id = request.POST.get("company_id")
        profile_pic = request.FILES["profile_pic"]
        company = get_object_or_404(Company, pk=company_id)
        email_address = request.POST.get("email_address")

        try:
            employee = Employee.objects.create(
                first_name=first_name,
                last_name=last_name,
                company=company,
                email_address=email_address,
            )
        except IntegrityError:
            messages.error(request, "Email already exists")
            return JsonResponse({"message": "failed"})
        ext = profile_pic.name.split(".")[-1]
        employee.profile_pic.save(email_address + ext, profile_pic, save=True)
        employee.save()
        messages.success(request, "Employee Added")
        return JsonResponse({"message": "success"})


@csrf_exempt
@login_required(login_url="login")
def edit_employee(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        company_id = request.POST.get("company_id")
        profile_pic = request.FILES.get("profile_pic", None)
        print(company_id)
        company = get_object_or_404(Company, pk=company_id)
        email_address = request.POST.get("email_address")

        employee = get_object_or_404(Employee, email_address=email_address)
        employee.email_address = email_address
        employee.first_name = first_name
        employee.company = company
        employee.last_name = last_name
        if profile_pic:
            ext = profile_pic.name.split(".")[-1]
            employee.profile_pic.save(email_address + ext, profile_pic, save=True)
        employee.save()
        messages.success(request, "Employee Edited")
        return JsonResponse({"message": "success"})


@csrf_exempt
@login_required(login_url="login")
def add_company(request):
    if request.method == "POST":
        body_unicode = request.body.decode("utf-8")
        body = json.loads(body_unicode)
        name = body.get("name")
        company = Company.objects.create(name=name)
        company.save()

        return JsonResponse({"message": "success"})


def logout_request(request):
    logout(request)
    messages.info(request, "You have sucessfully logged out.")
    return redirect("login")


class EmployeeApiView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = EmployeeSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        employees = Employee.objects.all()
        serializer = self.serializer_class(instance=employees, many=True)
        return Response(
            {"message": "All Employees", "status": True, "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Employee Added", "status": True},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"message": serializer.errors, "status": False},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
