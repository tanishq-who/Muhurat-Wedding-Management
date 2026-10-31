"""Business logic for Muhurat. Views stay thin and call these functions."""
import base64
import io
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core import signing
from django.core.files.base import ContentFile
from django.db import transaction
from django.utils import timezone
from PIL import Image

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Image as RLImage, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from .plan_template import TASK_TEMPLATE
from .models import (
    Agreement,
    ClientPayment,
    ExtraCharge,
    Lead,
    Quote,
    ScheduleEvent,
    Task,
    TimeLog,
    Vendor,
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


def create_agreement(lead):
    """Create an unsigned Agreement for the lead (signer_name = lead.couple_name) unless one already exists; return it."""
    agreement = lead.agreements.first()
    if agreement:
        return agreement
    return Agreement.objects.create(lead=lead, signer_name=lead.couple_name)


def build_agreement_pdf(agreement):
    """A clean A4 PDF for a signed wedding planning service agreement. Return bytes."""
    lead = agreement.lead
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=40,
        rightMargin=40,
        topMargin=35,
        bottomMargin=35,
    )
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "AgreementTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        alignment=1,
        textColor=colors.HexColor("#7B1113"),
    )
    subtitle_style = ParagraphStyle(
        "AgreementSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=10,
        leading=14,
        alignment=1,
        textColor=colors.HexColor("#555555"),
    )
    heading_style = ParagraphStyle(
        "AgreementHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#7B1113"),
        spaceBefore=10,
        spaceAfter=4,
    )
    body_style = ParagraphStyle(
        "AgreementBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#222222"),
    )
    term_style = ParagraphStyle(
        "AgreementTerm",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        spaceBefore=3,
        spaceAfter=3,
        textColor=colors.HexColor("#333333"),
    )

    story = []
    story.append(Paragraph("The Royal Knot: Wedding Planning Service Agreement", title_style))
    story.append(Paragraph("Muhurat Wedding Management Services", subtitle_style))
    story.append(Spacer(1, 12))

    package_display = lead.get_package_display() if hasattr(lead, "get_package_display") else lead.package
    details_data = [
        [
            Paragraph(f"<b>Couple Name:</b> {lead.couple_name}", body_style),
            Paragraph(f"<b>Tentative Date:</b> {lead.tentative_date}", body_style),
        ],
        [
            Paragraph(f"<b>Guest Count:</b> {lead.guest_count}", body_style),
            Paragraph(f"<b>Theme:</b> {lead.theme or 'Traditional / Royal'}", body_style),
        ],
        [
            Paragraph(f"<b>Budget:</b> ₹{lead.max_budget:,.2f}", body_style),
            Paragraph(f"<b>Package:</b> {package_display}", body_style),
        ],
    ]
    t = Table(details_data, colWidths=[250, 250])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FDFBF7")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#D4AF37")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#EAE0D0")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(t)
    story.append(Spacer(1, 10))

    story.append(Paragraph("Terms and Conditions", heading_style))
    terms = [
        "<b>1. Scope of Service:</b> The planner provides end-to-end wedding planning, vendor curation, itinerary design, and day-of coordination services.",
        "<b>2. Three-Stage Payment Plan:</b> A 30% booking deposit is due upon agreement signing, a 40% advance payment is due one month before the wedding, and the final payment is settled post-event including any approved extra charges.",
        "<b>3. Vendor Confidentiality:</b> All negotiated rates, contracts, vendor disclosures, and custom design boards remain strictly confidential.",
        "<b>4. Cancellation:</b> Initial deposit and incurred vendor booking fees are non-refundable. Cancellations within 30 days of the start date require full advance forfeiture.",
        "<b>5. Client Approval & Extra Charges:</b> Any modifications or unexpected requirements outside the standard package will be documented as extra charges and billed upon approval.",
    ]
    for term in terms:
        story.append(Paragraph(term, term_style))

    story.append(Spacer(1, 10))
    story.append(Paragraph("Signatures & Acknowledgment", heading_style))
    story.append(Paragraph("By signing below, the parties confirm and agree to all terms outlined in this agreement.", body_style))
    story.append(Spacer(1, 6))

    sig_elements = []
    if agreement.signature_image:
        try:
            agreement.signature_image.seek(0)
            img_data = io.BytesIO(agreement.signature_image.read())
            rl_img = RLImage(img_data, width=140, height=45)
            sig_elements.append(rl_img)
        except Exception:
            sig_elements.append(Paragraph("[Signature on File]", body_style))
    else:
        sig_elements.append(Paragraph("[Unsigned]", body_style))

    signed_date_str = agreement.signed_at.strftime("%d %b %Y, %I:%M %p") if agreement.signed_at else "Pending"
    sig_table_data = [
        [
            Paragraph(f"<b>Signer Name:</b> {agreement.signer_name}", body_style),
            sig_elements[0] if sig_elements else Paragraph("", body_style),
        ],
        [
            Paragraph(f"<b>Signed Date:</b> {signed_date_str}", body_style),
            Paragraph("<b>Status:</b> Legally Signed & Verified" if agreement.is_signed else "<b>Status:</b> Unsigned", body_style),
        ],
    ]
    sig_table = Table(sig_table_data, colWidths=[250, 250])
    sig_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#D4AF37")),
    ]))
    story.append(sig_table)

    doc.build(story)
    return buf.getvalue()


@transaction.atomic
def sign_agreement(agreement, signer_name, signature_data_url):
    """Validate base64 signature PNG, save to agreement, generate signed PDF."""
    agreement = Agreement.objects.select_for_update().get(pk=agreement.pk)

    if agreement.is_signed or agreement.signed_at is not None:
        raise ServiceError("This agreement is already signed.")

    if not signer_name or not str(signer_name).strip():
        raise ServiceError("Signer name is required.")

    prefix = "data:image/png;base64,"
    if not signature_data_url or not isinstance(signature_data_url, str) or not signature_data_url.startswith(prefix):
        raise ServiceError("Invalid signature format. Must be a PNG data URL starting with 'data:image/png;base64,'.")

    b64_data = signature_data_url[len(prefix):]
    try:
        raw_bytes = base64.b64decode(b64_data)
    except Exception:
        raise ServiceError("Invalid base64 signature encoding.")

    if len(raw_bytes) > 1024 * 1024:
        raise ServiceError("Signature image exceeds 1 MB limit.")

    try:
        img = Image.open(io.BytesIO(raw_bytes))
        img.verify()
        if img.format != "PNG":
            raise ServiceError("Signature image must be a PNG.")
    except ServiceError:
        raise
    except Exception:
        raise ServiceError("Invalid or corrupted signature image.")

    agreement.signer_name = str(signer_name).strip()
    agreement.signed_at = timezone.now()
    agreement.signature_image.save(f"signature_{agreement.id}.png", ContentFile(raw_bytes), save=False)

    pdf_bytes = build_agreement_pdf(agreement)
    agreement.signed_pdf.save(f"agreement_{agreement.id}.pdf", ContentFile(pdf_bytes), save=False)
    agreement.save()

    return agreement


def build_invoice_pdf(wedding):
    """PDF of client_invoice(wedding): package price, each approved extra, total, received, balance due. Return bytes."""
    inv = client_invoice(wedding)
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=40,
        rightMargin=40,
        topMargin=35,
        bottomMargin=35,
    )
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "InvoiceTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        alignment=1,
        textColor=colors.HexColor("#7B1113"),
    )
    subtitle_style = ParagraphStyle(
        "InvoiceSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=10,
        leading=14,
        alignment=1,
        textColor=colors.HexColor("#555555"),
    )
    heading_style = ParagraphStyle(
        "InvoiceHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#7B1113"),
        spaceBefore=10,
        spaceAfter=4,
    )
    body_style = ParagraphStyle(
        "InvoiceBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#222222"),
    )

    story = []
    story.append(Paragraph("Client Invoice", title_style))
    story.append(Paragraph("The Royal Knot: Muhurat Wedding Management", subtitle_style))
    story.append(Spacer(1, 14))

    wedding_info = [
        [
            Paragraph(f"<b>Couple:</b> {wedding.couple_name}", body_style),
            Paragraph(f"<b>Dates:</b> {wedding.start_date} to {wedding.end_date}", body_style),
        ],
        [
            Paragraph(f"<b>Venue / City:</b> {wedding.venue or 'TBD'}, {wedding.city or ''}", body_style),
            Paragraph(f"<b>Package:</b> {wedding.get_package_display() if hasattr(wedding, 'get_package_display') else wedding.package}", body_style),
        ],
    ]
    t_info = Table(wedding_info, colWidths=[250, 250])
    t_info.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FDFBF7")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#D4AF37")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(t_info)
    story.append(Spacer(1, 12))

    story.append(Paragraph("Invoice Breakdown", heading_style))
    table_data = [
        [
            Paragraph("<b>Item / Description</b>", body_style),
            Paragraph("<b>Qty</b>", body_style),
            Paragraph("<b>Unit Price (₹)</b>", body_style),
            Paragraph("<b>Total (₹)</b>", body_style),
        ],
        [
            Paragraph("Wedding Package Price", body_style),
            Paragraph("1", body_style),
            Paragraph(f"{inv['package_price']:,.2f}", body_style),
            Paragraph(f"{inv['package_price']:,.2f}", body_style),
        ],
    ]
    for extra in inv["extras"]:
        table_data.append([
            Paragraph(f"Extra: {extra.description}", body_style),
            Paragraph(f"{extra.quantity}", body_style),
            Paragraph(f"{extra.client_unit_price:,.2f}", body_style),
            Paragraph(f"{extra.client_total:,.2f}", body_style),
        ])

    table_data.append([
        Paragraph("<b>Total Invoice Amount</b>", body_style),
        Paragraph("", body_style),
        Paragraph("", body_style),
        Paragraph(f"<b>₹{inv['total']:,.2f}</b>", body_style),
    ])
    table_data.append([
        Paragraph("<b>Received (Paid to Date)</b>", body_style),
        Paragraph("", body_style),
        Paragraph("", body_style),
        Paragraph(f"<b>₹{inv['received']:,.2f}</b>", body_style),
    ])
    table_data.append([
        Paragraph("<b>Balance Due</b>", body_style),
        Paragraph("", body_style),
        Paragraph("", body_style),
        Paragraph(f"<b>₹{inv['balance_due']:,.2f}</b>", body_style),
    ])

    t_breakdown = Table(table_data, colWidths=[240, 50, 100, 110])
    t_breakdown.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#7B1113")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D4AF37")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LINEBELOW", (0, 0), (-1, 0), 1.5, colors.HexColor("#D4AF37")),
        ("BACKGROUND", (0, -3), (-1, -1), colors.HexColor("#FDFBF7")),
    ]))
    story.append(t_breakdown)

    doc.build(story)
    return buf.getvalue()


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


# ---------- Scene 6: founder's season review ----------
class SeasonSummaryResult(tuple):
    """Tuple containing (weddings, totals) with attribute and dict-like access."""
    def __new__(cls, weddings, totals):
        return super().__new__(cls, (weddings, totals))

    @property
    def weddings(self):
        return self[0]

    @property
    def totals(self):
        return self[1]

    def __getitem__(self, item):
        if item == "weddings":
            return self[0]
        if item == "totals":
            return self[1]
        if isinstance(item, str) and item in self[1]:
            return self[1][item]
        return super().__getitem__(item)

    def get(self, key, default=None):
        if key == "weddings":
            return self[0]
        if key == "totals":
            return self[1]
        if key in self[1]:
            return self[1][key]
        return default


class DueItem(dict):
    """Dictionary representing an upcoming due item with attribute access."""
    def __init__(self, payment, overdue, days, amount, due_date, wedding=None, **kwargs):
        super().__init__(
            payment=payment,
            overdue=overdue,
            days=days,
            amount=amount,
            due_date=due_date,
            wedding=wedding,
            **kwargs,
        )
        self.__dict__ = self


def wedding_profit(wedding):
    """Return financial summary dict for a single wedding."""
    approved_extras = list(wedding.extras.filter(approved=True))
    extras_client_total = sum((e.client_total for e in approved_extras), Decimal("0"))
    revenue = wedding.package_price + extras_client_total

    agreed_vendor_total = sum((wv.agreed_amount for wv in wedding.vendors.all()), Decimal("0"))
    extras_vendor_total = sum((e.vendor_total for e in approved_extras), Decimal("0"))
    vendor_cost = agreed_vendor_total + extras_vendor_total

    labour_cost = sum((tl.hours * tl.hourly_cost for tl in wedding.time_logs.all()), Decimal("0"))
    profit = revenue - vendor_cost - labour_cost

    margin = round(float((profit / revenue) * 100), 1) if revenue else 0.0
    received = sum((cp.amount for cp in wedding.client_payments.filter(paid_on__isnull=False)), Decimal("0"))
    low_margin = margin < 15

    return {
        "wedding": wedding,
        "couple_name": wedding.couple_name,
        "start_date": wedding.start_date,
        "status": wedding.status,
        "revenue": revenue,
        "vendor_cost": vendor_cost,
        "labour_cost": labour_cost,
        "profit": profit,
        "margin": margin,
        "received": received,
        "low_margin": low_margin,
    }


def season_summary():
    """Return list of wedding_profit dicts sorted by profit descending, plus totals."""
    all_weddings = Wedding.objects.prefetch_related(
        "extras", "vendors", "time_logs", "client_payments"
    ).all()
    weddings = [wedding_profit(w) for w in all_weddings]
    weddings.sort(key=lambda w: w["profit"], reverse=True)

    total_revenue = sum((w["revenue"] for w in weddings), Decimal("0"))
    total_cost = sum((w["vendor_cost"] + w["labour_cost"] for w in weddings), Decimal("0"))
    total_profit = sum((w["profit"] for w in weddings), Decimal("0"))
    wedding_count = len(weddings)
    avg_margin = round(sum(w["margin"] for w in weddings) / wedding_count, 1) if wedding_count else 0.0
    loss_count = sum(1 for w in weddings if w["profit"] < Decimal("0"))
    low_margin_count = sum(1 for w in weddings if w["low_margin"])

    totals = {
        "total_revenue": total_revenue,
        "total_cost": total_cost,
        "total_profit": total_profit,
        "avg_margin": avg_margin,
        "wedding_count": wedding_count,
        "loss_count": loss_count,
        "low_margin_count": low_margin_count,
    }
    return SeasonSummaryResult(weddings, totals)


def vendor_scorecard():
    """Return scorecard dicts for all vendors with bookings, sorted by on_time_rate descending."""
    vendors = Vendor.objects.filter(bookings__isnull=False).distinct()
    results = []
    for v in vendors:
        b_qs = v.bookings.select_related("checkin").prefetch_related("extras", "payments").all()
        booking_count = len(b_qs)
        eligible = [b for b in b_qs if hasattr(b, "checkin") and b.expected_arrival is not None]
        if eligible:
            on_time = sum(1 for b in eligible if b.checkin.arrived_at <= b.expected_arrival + timedelta(minutes=10))
            on_time_rate = round((on_time / len(eligible)) * 100, 1)
        else:
            on_time_rate = 0.0

        agreed_total = sum((b.agreed_amount for b in b_qs), Decimal("0"))
        extras_total = sum((e.vendor_total for b in b_qs for e in b.extras.filter(approved=True)), Decimal("0"))
        cost_variance = round(float((extras_total / agreed_total) * 100), 1) if agreed_total else 0.0

        total_paid = sum((p.amount for b in b_qs for p in b.payments.filter(paid_on__isnull=False)), Decimal("0"))

        results.append({
            "vendor": v,
            "category": v.category,
            "rating": v.rating,
            "bookings": booking_count,
            "on_time_rate": on_time_rate,
            "cost_variance": cost_variance,
            "total_paid": total_paid,
        })

    results.sort(key=lambda item: item["on_time_rate"], reverse=True)
    return results


def upcoming_dues(days=30):
    """Return dict with unpaid upcoming and overdue client and vendor dues within given days."""
    today = timezone.localdate()
    cutoff = today + timedelta(days=days)

    unpaid_cp = ClientPayment.objects.filter(
        paid_on__isnull=True, due_date__lte=cutoff
    ).select_related("wedding").order_by("due_date")

    to_collect = []
    for cp in unpaid_cp:
        days_until = (cp.due_date - today).days
        overdue = cp.due_date < today
        to_collect.append(DueItem(
            payment=cp,
            overdue=overdue,
            days=days_until,
            amount=cp.amount,
            due_date=cp.due_date,
            wedding=cp.wedding,
            kind=cp.kind,
        ))

    unpaid_vp = VendorPayment.objects.filter(
        paid_on__isnull=True, due_date__isnull=False, due_date__lte=cutoff
    ).select_related("wedding_vendor__vendor", "wedding_vendor__wedding").order_by("due_date")

    to_pay = []
    for vp in unpaid_vp:
        days_until = (vp.due_date - today).days
        overdue = vp.due_date < today
        to_pay.append(DueItem(
            payment=vp,
            overdue=overdue,
            days=days_until,
            amount=vp.amount,
            due_date=vp.due_date,
            wedding=vp.wedding_vendor.wedding,
            vendor=vp.wedding_vendor.vendor,
            kind=vp.kind,
        ))

    to_collect_total = sum((item["amount"] for item in to_collect), Decimal("0"))
    to_pay_total = sum((item["amount"] for item in to_pay), Decimal("0"))

    return {
        "to_collect": to_collect,
        "to_pay": to_pay,
        "to_collect_total": to_collect_total,
        "to_pay_total": to_pay_total,
    }


def share_token_for_season():
    """Generate a signed season share token valid for 7 days."""
    return signing.dumps({"scope": "season"}, salt="season-share")


def verify_share_token(token):
    """Verify season share token. Raise ServiceError if invalid or expired."""
    try:
        return signing.loads(token, salt="season-share", max_age=timedelta(days=7))
    except (signing.BadSignature, signing.SignatureExpired):
        raise ServiceError("Invalid or expired share token.")
    except Exception:
        raise ServiceError("Invalid or expired share token.")


