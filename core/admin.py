from django.contrib import admin
from .models import (
    Lead, Wedding, Agreement, Vendor, WeddingVendor, VendorCheckIn,
    Quote, QuoteLine, Task, ClientPayment, VendorPayment,
    ExtraCharge, ScheduleEvent, TimeLog,
)


class QuoteLineInline(admin.TabularInline):
    model = QuoteLine
    extra = 1


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ("couple_name", "phone", "tentative_date", "guest_count", "max_budget", "stage")
    list_filter = ("stage", "source", "package")
    search_fields = ("couple_name", "phone")


@admin.register(Wedding)
class WeddingAdmin(admin.ModelAdmin):
    list_display = ("couple_name", "city", "start_date", "guest_count", "budget", "status")
    list_filter = ("status", "package", "city")
    search_fields = ("couple_name",)


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "city", "rating")
    list_filter = ("category", "city")
    search_fields = ("name",)


@admin.register(WeddingVendor)
class WeddingVendorAdmin(admin.ModelAdmin):
    list_display = ("wedding", "vendor", "role", "agreed_amount", "expected_arrival")
    list_filter = ("role",)


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ("wedding", "vendor", "category", "status")
    list_filter = ("status", "category")
    inlines = [QuoteLineInline]


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "wedding", "category", "owner", "stage", "due_date")
    list_filter = ("stage", "category")


@admin.register(ClientPayment)
class ClientPaymentAdmin(admin.ModelAdmin):
    list_display = ("wedding", "kind", "amount", "due_date", "paid_on")
    list_filter = ("kind",)


@admin.register(VendorPayment)
class VendorPaymentAdmin(admin.ModelAdmin):
    list_display = ("wedding_vendor", "kind", "amount", "due_date", "paid_on")
    list_filter = ("kind",)


@admin.register(ScheduleEvent)
class ScheduleEventAdmin(admin.ModelAdmin):
    list_display = ("wedding", "title", "start_time", "responsible", "status")
    list_filter = ("status",)


@admin.register(ExtraCharge)
class ExtraChargeAdmin(admin.ModelAdmin):
    list_display = ("wedding", "description", "quantity", "client_unit_price", "approved")
    list_filter = ("approved",)


admin.site.register(Agreement)
admin.site.register(VendorCheckIn)
admin.site.register(TimeLog)
