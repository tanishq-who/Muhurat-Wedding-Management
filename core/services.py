"""Business logic for Muhurat. Views stay thin and call these functions."""
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from .plan_template import TASK_TEMPLATE
from .models import (
    ClientPayment,
    ExtraCharge,
    Lead,
    Quote,
    ScheduleEvent,
    Task,
    VendorCheckIn,
    VendorPayment,
    Wedding,
    WeddingVendor,
)

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


# ---------- Scene 5: post-wedding settlement ----------
def add_extra_charge(wedding, wedding_vendor, description, quantity, client_unit_price, vendor_unit_cost=Decimal("0")):
    """Add an extra charge to a wedding. Quantity and client price must be > 0."""
    if quantity is None or client_unit_price is None:
        raise ServiceError("Quantity and client unit price are required.")
    try:
        quantity = Decimal(str(quantity))
    except Exception:
        raise ServiceError("Invalid quantity.")
    try:
        client_unit_price = Decimal(str(client_unit_price))
    except Exception:
        raise ServiceError("Invalid client unit price.")
    try:
        vendor_unit_cost = Decimal(str(vendor_unit_cost if vendor_unit_cost is not None else 0))
    except Exception:
        raise ServiceError("Invalid vendor unit cost.")

    if quantity <= Decimal("0"):
        raise ServiceError("Quantity must be greater than zero.")
    if client_unit_price <= Decimal("0"):
        raise ServiceError("Client unit price must be greater than zero.")
    if vendor_unit_cost < Decimal("0"):
        raise ServiceError("Vendor unit cost cannot be negative.")
    if wedding_vendor is not None and wedding_vendor.wedding_id != wedding.id:
        raise ServiceError("Vendor booking does not belong to this wedding.")

    return ExtraCharge.objects.create(
        wedding=wedding,
        wedding_vendor=wedding_vendor,
        description=description,
        quantity=quantity,
        client_unit_price=client_unit_price,
        vendor_unit_cost=vendor_unit_cost,
        approved=False,
    )


def approve_extra(extra):
    """Approve an extra charge. Cannot approve twice."""
    if extra.approved:
        raise ServiceError("This extra charge is already approved.")
    extra.approved = True
    extra.save(update_fields=["approved"])
    return extra


def compute_settlement(wedding):
    """Return a settlement row dict per vendor booking, ordered by role."""
    rows = []
    bookings = (wedding.vendors.select_related("vendor")
                .prefetch_related("extras", "payments")
                .order_by("role"))
    for wv in bookings:
        agreed = wv.agreed_amount
        approved_extras = [e for e in wv.extras.all() if e.approved]
        extras = sum((e.vendor_total for e in approved_extras), Decimal("0"))
        owed = agreed + extras
        paid_payments = [p for p in wv.payments.all() if p.paid_on is not None]
        paid = sum((p.amount for p in paid_payments), Decimal("0"))
        remaining = owed - paid
        if remaining <= Decimal("0"):
            status = "paid"
        elif paid > Decimal("0"):
            status = "partial"
        else:
            status = "unpaid"
        advance = next((p for p in wv.payments.all() if p.kind == VendorPayment.Kind.ADVANCE), None)
        balance = next((p for p in wv.payments.all() if p.kind == VendorPayment.Kind.BALANCE), None)
        rows.append({
            "booking": wv,
            "agreed": agreed,
            "extras": extras,
            "owed": owed,
            "paid": paid,
            "remaining": remaining,
            "status": status,
            "advance": advance,
            "balance": balance,
        })
    return rows


@transaction.atomic
def record_vendor_payment(wedding_vendor, kind, amount=None, user=None, reference=""):
    """Record a vendor payment (advance or balance). Atomic with select_for_update."""
    wedding_vendor = WeddingVendor.objects.select_for_update().get(pk=wedding_vendor.pk)

    if kind not in (VendorPayment.Kind.ADVANCE, VendorPayment.Kind.BALANCE):
        raise ServiceError("Payment kind must be 'advance' or 'balance'.")

    # Payment row of that kind
    payment = wedding_vendor.payments.select_for_update().filter(kind=kind).first()
    if payment and payment.paid_on is not None:
        raise ServiceError(f"A {kind} payment has already been recorded.")

    # Calculate owed and paid
    agreed = wedding_vendor.agreed_amount
    extras = sum((e.vendor_total for e in wedding_vendor.extras.filter(approved=True)), Decimal("0"))
    owed = agreed + extras
    paid = sum((p.amount for p in wedding_vendor.payments.filter(paid_on__isnull=False)), Decimal("0"))

    if kind == VendorPayment.Kind.BALANCE:
        advance_pmt = wedding_vendor.payments.filter(kind=VendorPayment.Kind.ADVANCE, paid_on__isnull=False).first()
        if not advance_pmt:
            raise ServiceError("The advance payment must be paid before paying balance.")
        amount = owed - paid
        if amount <= Decimal("0"):
            raise ServiceError("No remaining balance to pay.")
    elif kind == VendorPayment.Kind.ADVANCE:
        if amount is None or str(amount).strip() == "":
            if payment and payment.amount:
                amount = payment.amount
            else:
                raise ServiceError("An advance amount is required.")
        else:
            try:
                amount = Decimal(str(amount))
            except Exception:
                raise ServiceError("Invalid payment amount.")
        if amount <= Decimal("0"):
            raise ServiceError("Payment amount must be greater than zero.")

    if paid + amount > owed:
        raise ServiceError(f"Payment of {amount} would exceed total owed ({owed}). Already paid: {paid}.")

    today = timezone.localdate()
    if payment:
        payment.amount = amount
        payment.paid_on = today
        if reference:
            payment.reference = reference
        payment.save()
    else:
        payment = VendorPayment.objects.create(
            wedding_vendor=wedding_vendor,
            kind=kind,
            amount=amount,
            paid_on=today,
            reference=reference or "",
        )
    return payment


def client_invoice(wedding):
    """Return invoice breakdown dict for client."""
    package_price = wedding.package_price
    extras = list(wedding.extras.filter(approved=True))
    extras_total = sum((e.client_total for e in extras), Decimal("0"))
    total = package_price + extras_total
    payments = list(wedding.client_payments.order_by("due_date"))
    received = sum((p.amount for p in payments if p.paid_on is not None), Decimal("0"))
    balance_due = total - received
    return {
        "package_price": package_price,
        "extras": extras,
        "extras_total": extras_total,
        "total": total,
        "received": received,
        "balance_due": balance_due,
        "payments": payments,
    }


@transaction.atomic
def pay_client_stage(wedding, kind):
    """Mark a client milestone payment as paid. If final, adjust amount with extras."""
    try:
        stage = wedding.client_payments.select_for_update().get(kind=kind)
    except ClientPayment.DoesNotExist:
        raise ServiceError(f"Payment stage '{kind}' does not exist.")

    if stage.paid_on is not None:
        raise ServiceError(f"Payment stage '{stage.get_kind_display()}' is already paid.")

    if kind == ClientPayment.Kind.FINAL:
        invoice = client_invoice(wedding)
        other_stages = wedding.client_payments.exclude(pk=stage.pk)
        other_total = sum((p.amount for p in other_stages), Decimal("0"))
        stage.amount = invoice["total"] - other_total

    today = timezone.localdate()
    stage.paid_on = today
    stage.save()
    return stage


@transaction.atomic
def close_settlement(wedding):
    """Close the settlement for a wedding. Sets status to Settled."""
    wedding = Wedding.objects.select_for_update().get(pk=wedding.pk)

    if wedding.status == Wedding.Status.SETTLED:
        raise ServiceError("This wedding is already settled.")

    if wedding.extras.filter(approved=False).exists():
        raise ServiceError("Cannot close settlement: there are unapproved extra charges.")

    rows = compute_settlement(wedding)
    unpaid_vendors = [r["booking"].vendor.name for r in rows if r["remaining"] > Decimal("0")]
    if unpaid_vendors:
        names = ", ".join(unpaid_vendors)
        raise ServiceError(f"Cannot close settlement: vendors with outstanding balance: {names}.")

    invoice = client_invoice(wedding)
    if invoice["balance_due"] > Decimal("0"):
        raise ServiceError(f"Cannot close settlement: client has an outstanding balance of {invoice['balance_due']}.")

    wedding.status = Wedding.Status.SETTLED
    wedding.save(update_fields=["status"])
    return wedding



# ---------- Scene 5: post-wedding settlement ----------
def add_extra_charge(wedding, wedding_vendor, description, quantity, client_unit_price, vendor_unit_cost=Decimal("0")):
    """Add an extra charge to a wedding. Quantity and client price must be > 0."""
    if quantity is None or client_unit_price is None:
        raise ServiceError("Quantity and client unit price are required.")
    try:
        quantity = Decimal(str(quantity))
    except Exception:
        raise ServiceError("Invalid quantity.")
    try:
        client_unit_price = Decimal(str(client_unit_price))
    except Exception:
        raise ServiceError("Invalid client unit price.")
    try:
        vendor_unit_cost = Decimal(str(vendor_unit_cost if vendor_unit_cost is not None else 0))
    except Exception:
        raise ServiceError("Invalid vendor unit cost.")

    if quantity <= Decimal("0"):
        raise ServiceError("Quantity must be greater than zero.")
    if client_unit_price <= Decimal("0"):
        raise ServiceError("Client unit price must be greater than zero.")
    if vendor_unit_cost < Decimal("0"):
        raise ServiceError("Vendor unit cost cannot be negative.")
    if wedding_vendor is not None and wedding_vendor.wedding_id != wedding.id:
        raise ServiceError("Vendor booking does not belong to this wedding.")

    return ExtraCharge.objects.create(
        wedding=wedding,
        wedding_vendor=wedding_vendor,
        description=description,
        quantity=quantity,
        client_unit_price=client_unit_price,
        vendor_unit_cost=vendor_unit_cost,
        approved=False,
    )


def approve_extra(extra):
    """Approve an extra charge. Cannot approve twice."""
    if extra.approved:
        raise ServiceError("This extra charge is already approved.")
    extra.approved = True
    extra.save(update_fields=["approved"])
    return extra


def compute_settlement(wedding):
    """Return a settlement row dict per vendor booking, ordered by role."""
    rows = []
    bookings = (wedding.vendors.select_related("vendor")
                .prefetch_related("extras", "payments")
                .order_by("role"))
    for wv in bookings:
        agreed = wv.agreed_amount
        approved_extras = [e for e in wv.extras.all() if e.approved]
        extras = sum((e.vendor_total for e in approved_extras), Decimal("0"))
        owed = agreed + extras
        paid_payments = [p for p in wv.payments.all() if p.paid_on is not None]
        paid = sum((p.amount for p in paid_payments), Decimal("0"))
        remaining = owed - paid
        if remaining <= Decimal("0"):
            status = "paid"
        elif paid > Decimal("0"):
            status = "partial"
        else:
            status = "unpaid"
        advance = next((p for p in wv.payments.all() if p.kind == VendorPayment.Kind.ADVANCE), None)
        balance = next((p for p in wv.payments.all() if p.kind == VendorPayment.Kind.BALANCE), None)
        rows.append({
            "booking": wv,
            "agreed": agreed,
            "extras": extras,
            "owed": owed,
            "paid": paid,
            "remaining": remaining,
            "status": status,
            "advance": advance,
            "balance": balance,
        })
    return rows


@transaction.atomic
def record_vendor_payment(wedding_vendor, kind, amount=None, user=None, reference=""):
    """Record a vendor payment (advance or balance). Atomic with select_for_update."""
    wedding_vendor = WeddingVendor.objects.select_for_update().get(pk=wedding_vendor.pk)

    if kind not in (VendorPayment.Kind.ADVANCE, VendorPayment.Kind.BALANCE):
        raise ServiceError("Payment kind must be 'advance' or 'balance'.")

    # Payment row of that kind
    payment = wedding_vendor.payments.select_for_update().filter(kind=kind).first()
    if payment and payment.paid_on is not None:
        raise ServiceError(f"A {kind} payment has already been recorded.")

    # Calculate owed and paid
    agreed = wedding_vendor.agreed_amount
    extras = sum((e.vendor_total for e in wedding_vendor.extras.filter(approved=True)), Decimal("0"))
    owed = agreed + extras
    paid = sum((p.amount for p in wedding_vendor.payments.filter(paid_on__isnull=False)), Decimal("0"))

    if kind == VendorPayment.Kind.BALANCE:
        advance_pmt = wedding_vendor.payments.filter(kind=VendorPayment.Kind.ADVANCE, paid_on__isnull=False).first()
        if not advance_pmt:
            raise ServiceError("The advance payment must be paid before paying balance.")
        amount = owed - paid
        if amount <= Decimal("0"):
            raise ServiceError("No remaining balance to pay.")
    elif kind == VendorPayment.Kind.ADVANCE:
        if amount is None or str(amount).strip() == "":
            if payment and payment.amount:
                amount = payment.amount
            else:
                raise ServiceError("An advance amount is required.")
        else:
            try:
                amount = Decimal(str(amount))
            except Exception:
                raise ServiceError("Invalid payment amount.")
        if amount <= Decimal("0"):
            raise ServiceError("Payment amount must be greater than zero.")

    if paid + amount > owed:
        raise ServiceError(f"Payment of {amount} would exceed total owed ({owed}). Already paid: {paid}.")

    today = timezone.localdate()
    if payment:
        payment.amount = amount
        payment.paid_on = today
        if reference:
            payment.reference = reference
        payment.save()
    else:
        payment = VendorPayment.objects.create(
            wedding_vendor=wedding_vendor,
            kind=kind,
            amount=amount,
            paid_on=today,
            reference=reference or "",
        )
    return payment


def client_invoice(wedding):
    """Return invoice breakdown dict for client."""
    package_price = wedding.package_price
    extras = list(wedding.extras.filter(approved=True))
    extras_total = sum((e.client_total for e in extras), Decimal("0"))
    total = package_price + extras_total
    payments = list(wedding.client_payments.order_by("due_date"))
    received = sum((p.amount for p in payments if p.paid_on is not None), Decimal("0"))
    balance_due = total - received
    return {
        "package_price": package_price,
        "extras": extras,
        "extras_total": extras_total,
        "total": total,
        "received": received,
        "balance_due": balance_due,
        "payments": payments,
    }


@transaction.atomic
def pay_client_stage(wedding, kind):
    """Mark a client milestone payment as paid. If final, adjust amount with extras."""
    try:
        stage = wedding.client_payments.select_for_update().get(kind=kind)
    except ClientPayment.DoesNotExist:
        raise ServiceError(f"Payment stage '{kind}' does not exist.")

    if stage.paid_on is not None:
        raise ServiceError(f"Payment stage '{stage.get_kind_display()}' is already paid.")

    if kind == ClientPayment.Kind.FINAL:
        invoice = client_invoice(wedding)
        other_stages = wedding.client_payments.exclude(pk=stage.pk)
        other_total = sum((p.amount for p in other_stages), Decimal("0"))
        stage.amount = invoice["total"] - other_total

    today = timezone.localdate()
    stage.paid_on = today
    stage.save()
    return stage


@transaction.atomic
def close_settlement(wedding):
    """Close the settlement for a wedding. Sets status to Settled."""
    wedding = Wedding.objects.select_for_update().get(pk=wedding.pk)

    if wedding.status == Wedding.Status.SETTLED:
        raise ServiceError("This wedding is already settled.")

    if wedding.extras.filter(approved=False).exists():
        raise ServiceError("Cannot close settlement: there are unapproved extra charges.")

    rows = compute_settlement(wedding)
    unpaid_vendors = [r["booking"].vendor.name for r in rows if r["remaining"] > Decimal("0")]
    if unpaid_vendors:
        names = ", ".join(unpaid_vendors)
        raise ServiceError(f"Cannot close settlement: vendors with outstanding balance: {names}.")

    invoice = client_invoice(wedding)
    if invoice["balance_due"] > Decimal("0"):
        raise ServiceError(f"Cannot close settlement: client has an outstanding balance of {invoice['balance_due']}.")

    wedding.status = Wedding.Status.SETTLED
    wedding.save(update_fields=["status"])
    return wedding