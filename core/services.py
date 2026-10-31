"""Business logic for Muhurat. Views stay thin and call these functions."""
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from .models import ClientPayment, Lead, Quote, Task, Wedding, WeddingVendor
from .plan_template import TASK_TEMPLATE
from .models import (ClientPayment, Lead, Quote, ScheduleEvent, Task,
                     VendorCheckIn, Wedding, WeddingVendor)     

User = get_user_model()


class ServiceError(Exception):
    """Raised when a business rule is broken. The message is safe to show the user."""


# ---------- Scene 1: enquiry pipeline ----------
LEAD_FLOW = {
    Lead.Stage.NEW: [Lead.Stage.MEETING, Lead.Stage.LOST],
    Lead.Stage.MEETING: [Lead.Stage.AGREEMENT, Lead.Stage.LOST],
    Lead.Stage.AGREEMENT: [Lead.Stage.CONFIRMED, Lead.Stage.LOST],
}


def advance_lead_stage(lead, new_stage):
    """Move a lead along New > Meeting > Agreement > Confirmed (or Lost)."""
    if new_stage not in LEAD_FLOW.get(lead.stage, []):
        raise ServiceError(f"Cannot move from {lead.get_stage_display()} to {new_stage}.")
    if new_stage == Lead.Stage.CONFIRMED:
        if not lead.agreements.filter(signed_at__isnull=False).exists():
            raise ServiceError("The service agreement must be signed before confirming.")
    lead.stage = new_stage
    lead.save(update_fields=["stage"])
    return lead


@transaction.atomic
def convert_lead_to_wedding(lead, package_price):
    """Create the Wedding from a confirmed lead (safe to call twice)."""
    if lead.stage != Lead.Stage.CONFIRMED:
        raise ServiceError("Only confirmed leads can become weddings.")
    existing = Wedding.objects.filter(lead=lead).first()
    if existing:
        return existing
    return Wedding.objects.create(
        lead=lead, couple_name=lead.couple_name, package=lead.package, theme=lead.theme,
        start_date=lead.tentative_date, end_date=lead.tentative_date + timedelta(days=2),
        guest_count=lead.guest_count, budget=lead.max_budget,
        package_price=Decimal(package_price), planner=lead.planner)


# ---------- Scene 2: quotes ----------
@transaction.atomic
def select_winning_quote(quote):
    """Pick the winner: close the other quotes and link the vendor to the wedding."""
    quote = Quote.objects.select_for_update().get(pk=quote.pk)
    if quote.status == Quote.Status.SELECTED:
        raise ServiceError("This quote is already selected.")
    if quote.status == Quote.Status.CLOSED:
        raise ServiceError("This quote is closed.")
    if quote.wedding.quotes.filter(category=quote.category, status=Quote.Status.SELECTED).exists():
        raise ServiceError(f"A {quote.category} has already been chosen for this wedding.")

    quote.status = Quote.Status.SELECTED
    quote.save(update_fields=["status"])

    quote.wedding.quotes.filter(category=quote.category).exclude(pk=quote.pk).exclude(
        status=Quote.Status.CLOSED).update(status=Quote.Status.CLOSED)

    booking, _ = WeddingVendor.objects.get_or_create(
        wedding=quote.wedding, vendor=quote.vendor, role=quote.category,
        defaults={"agreed_amount": quote.total, "responsible": quote.wedding.planner})
    return booking


# ---------- Scene 3: instant plan ----------
@transaction.atomic
def generate_wedding_plan(wedding):
    """Create 25+ tasks and the 3 payment stages. Calling it twice creates no duplicates."""
    owners = list(User.objects.filter(groups__name="Planner").order_by("id"))
    if not owners and wedding.planner:
        owners = [wedding.planner]

    tasks_created = 0
    if not wedding.tasks.exists():
        for n, (title, category, offset) in enumerate(TASK_TEMPLATE):
            Task.objects.create(
                wedding=wedding, title=title, category=category,
                owner=owners[n % len(owners)] if owners else None,
                due_date=wedding.start_date + timedelta(days=offset))
            tasks_created += 1

    price = wedding.package_price
    booking = (price * Decimal("0.30")).quantize(Decimal("0.01"))
    advance = (price * Decimal("0.40")).quantize(Decimal("0.01"))
    stages = [
        ("booking", booking, timezone.localdate()),
        ("advance", advance, wedding.start_date - timedelta(days=30)),
        ("final", price - booking - advance, wedding.end_date + timedelta(days=7)),
    ]
    payments_created = 0
    for kind, amount, due in stages:
        _, created = ClientPayment.objects.get_or_create(
            wedding=wedding, kind=kind, defaults={"amount": amount, "due_date": due})
        payments_created += int(created)
    return {"tasks_created": tasks_created, "payments_created": payments_created}


@transaction.atomic
def mark_booking_paid(wedding):
    """Booking deposit received: build the plan right away."""
    generate_wedding_plan(wedding)
    booking = wedding.client_payments.select_for_update().get(kind="booking")
    if booking.paid_on:
        raise ServiceError("The booking payment is already recorded.")
    booking.paid_on = timezone.localdate()
    booking.save(update_fields=["paid_on"])
    return booking


def move_task(task, stage):
    if stage not in Task.Stage.values:
        raise ServiceError("Unknown task stage.")
    task.stage = stage
    task.save(update_fields=["stage"])
    return task

    # ---------- Scene 4: wedding day ----------
def check_in_vendor(wedding_vendor, user, note=""):
    """Mark a vendor as arrived, right now. A vendor can only check in once."""
    if hasattr(wedding_vendor, "checkin"):
        raise ServiceError(f"{wedding_vendor.vendor.name} is already checked in.")
    return VendorCheckIn.objects.create(
        wedding_vendor=wedding_vendor, arrived_at=timezone.now(),
        checked_in_by=user, note=note)


def vendor_status_rows(wedding, now=None):
    """One row per vendor for the day-of screen: arrived, late, or expected."""
    now = now or timezone.now()
    rows = []
    bookings = (wedding.vendors.select_related("vendor", "responsible", "checkin")
                .order_by("expected_arrival"))
    for wv in bookings:
        checkin = getattr(wv, "checkin", None)
        minutes = 0
        if checkin:
            status = "arrived"
            if wv.expected_arrival:
                minutes = int((checkin.arrived_at - wv.expected_arrival).total_seconds() // 60)
        elif wv.expected_arrival and wv.expected_arrival < now:
            status = "late"
            minutes = int((now - wv.expected_arrival).total_seconds() // 60)
        else:
            status = "expected"
        rows.append({"booking": wv, "status": status, "minutes": minutes,
                     "checkin": checkin})
    return rows


def get_late_vendors(wedding, now=None):
    """Vendors whose arrival time has passed with no check-in, worst first."""
    late = [r for r in vendor_status_rows(wedding, now) if r["status"] == "late"]
    return sorted(late, key=lambda r: -r["minutes"])


def update_event_status(event, status):
    if status not in ScheduleEvent.Status.values:
        raise ServiceError("Unknown event status.")
    event.status = status
    event.save(update_fields=["status"])
    return event