from django.urls import path

from .views import (
    EmployeeApiView,
    add_company,
    add_employee,
    edit_employee,
    employees,
    login_request,
    logout_request,
)

urlpatterns = [
    path("", login_request, name="login"),
    path("employees", employees, name="employees"),
    path("logout", logout_request, name="logout"),
    path("add-company", add_company, name="addcompany"),
    path("add-employee", add_employee, name="addemployee"),
    path("edit-employee", edit_employee, name="editemployee"),
    path("api/v1/employees", EmployeeApiView.as_view(), name="employee-api"),
]
