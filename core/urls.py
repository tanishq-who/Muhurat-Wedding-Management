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
    path("weddings/<int:wedding_id>/settlement/", views.settlement, name="settlement"),
    path("weddings/<int:id>/settlement/", views.settlement, name="settlement"),
    path("weddings/<int:wedding_id>/extras/add/", views.extra_add, name="extra_add"),
    path("weddings/<int:id>/extras/add/", views.extra_add, name="extra_add"),
    path("extras/<int:extra_id>/approve/", views.extra_approve, name="extra_approve"),
    path("extras/<int:id>/approve/", views.extra_approve, name="extra_approve"),
    path("bookings/<int:booking_id>/pay/", views.vendor_pay, name="vendor_pay"),
    path("bookings/<int:id>/pay/", views.vendor_pay, name="vendor_pay"),
    path("weddings/<int:wedding_id>/client-pay/", views.client_pay, name="client_pay"),
    path("weddings/<int:id>/client-pay/", views.client_pay, name="client_pay"),
    path("weddings/<int:wedding_id>/settle/", views.settlement_close, name="settlement_close"),
    path("weddings/<int:id>/settle/", views.settlement_close, name="settlement_close"),
]
