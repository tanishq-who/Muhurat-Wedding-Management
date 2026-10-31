from django.urls import path
from . import views

urlpatterns = [
    path("enquiries/", views.enquiries, name="enquiries"),
    path("enquiries/<int:lead_id>/advance/", views.lead_advance, name="lead_advance"),
    path("weddings/<int:wedding_id>/quotes/", views.quotes, name="quotes"),
    path("quotes/<int:quote_id>/select/", views.quote_select, name="quote_select"),
    path("weddings/<int:wedding_id>/plan/", views.plan, name="plan"),
    path("weddings/<int:wedding_id>/booking-paid/", views.booking_paid, name="booking_paid"),
    path("tasks/<int:task_id>/move/", views.task_move, name="task_move"),
        path("weddings/<int:wedding_id>/timeline/", views.timeline, name="timeline"),
    path("bookings/<int:booking_id>/checkin/", views.vendor_checkin, name="vendor_checkin"),
    path("events/<int:event_id>/status/", views.event_status, name="event_status"),
]
