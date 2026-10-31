import csv
from decimal import Decimal
from functools import wraps
from urllib.parse import quote

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from . import services
from .forms import ExtraChargeForm, LeadForm
from .models import Agreement, ExtraCharge, Lead, Quote, ScheduleEvent, Task, Wedding, WeddingVendor


@login_required
def enquiries(request):
    if request.method == "POST":
        form = LeadForm(request.POST)
        if form.is_valid():
            lead = form.save(commit=False)
            lead.planner = request.user
            lead.save()
            messages.success(request, "Enquiry saved.")
            return redirect("enquiries")
    else:
        form = LeadForm()
    leads_by_stage = {v: Lead.objects.filter(stage=v).order_by("tentative_date")
                      for v, _ in Lead.Stage.choices}
    return render(request, "core/enquiries.html",
                  {"leads_by_stage": leads_by_stage, "stages": Lead.Stage.choices, "form": form})


@login_required
@require_POST
def lead_advance(request, lead_id):
    lead = get_object_or_404(Lead, pk=lead_id)
    try:
        services.advance_lead_stage(lead, request.POST.get("stage"))
        messages.success(request, f"{lead.couple_name} moved to {lead.get_stage_display()}.")
    except services.ServiceError as e:
        messages.error(request, str(e))
    return redirect("enquiries")


@login_required
def quotes(request, wedding_id):
    wedding = get_object_or_404(Wedding, pk=wedding_id)
    category = request.GET.get("category", "Caterer")
    quote_list = list(wedding.quotes.filter(category=category).prefetch_related("lines"))
    open_quotes = [q for q in quote_list if q.status != Quote.Status.CLOSED]
    lowest = min(open_quotes, key=lambda q: q.total) if open_quotes else None
    return render(request, "core/quotes.html", {
        "wedding": wedding, "category": category, "quotes": quote_list,
        "lowest_quote": lowest})


@login_required
@require_POST
def quote_select(request, quote_id):
    quote = get_object_or_404(Quote, pk=quote_id)
    try:
        services.select_winning_quote(quote)
        messages.success(request, f"{quote.vendor.name} selected. Other quotes closed.")
    except services.ServiceError as e:
        messages.error(request, str(e))
    return redirect("quotes", wedding_id=quote.wedding_id)


@login_required
def plan(request, wedding_id):
    wedding = get_object_or_404(Wedding, pk=wedding_id)
    tasks = wedding.tasks.select_related("owner")
    tasks_by_stage = {v: [t for t in tasks if t.stage == v] for v, _ in Task.Stage.choices}
    return render(request, "core/plan.html", {
        "wedding": wedding, "tasks_by_stage": tasks_by_stage, "stages": Task.Stage.choices,
        "milestones": wedding.client_payments.order_by("due_date")})


@login_required
@require_POST
def booking_paid(request, wedding_id):
    wedding = get_object_or_404(Wedding, pk=wedding_id)
    try:
        services.mark_booking_paid(wedding)
        messages.success(request, "Booking received. The wedding plan has been created.")
    except services.ServiceError as e:
        messages.error(request, str(e))
    return redirect("plan", wedding_id=wedding.id)


@login_required
@require_POST
def task_move(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    try:
        services.move_task(task, request.POST.get("stage"))
    except services.ServiceError as e:
        messages.error(request, str(e))
    return redirect("plan", wedding_id=task.wedding_id)
@login_required
def timeline(request, wedding_id):
    wedding = get_object_or_404(Wedding, pk=wedding_id)
    return render(request, "core/timeline.html", {
        "wedding": wedding,
        "events": wedding.events.select_related("responsible"),
        "vendor_rows": services.vendor_status_rows(wedding),
        "late_vendors": services.get_late_vendors(wedding),
        "event_statuses": ScheduleEvent.Status.choices})


@login_required
@require_POST
def vendor_checkin(request, booking_id):
    booking = get_object_or_404(WeddingVendor, pk=booking_id)
    try:
        services.check_in_vendor(booking, request.user, request.POST.get("note", ""))
        messages.success(request, f"{booking.vendor.name} marked as arrived.")
    except services.ServiceError as e:
        messages.error(request, str(e))
    return redirect("timeline", wedding_id=booking.wedding_id)


@login_required
@require_POST
def event_status(request, event_id):
    event = get_object_or_404(ScheduleEvent, pk=event_id)
    try:
        services.update_event_status(event, request.POST.get("status"))
    except services.ServiceError as e:
        messages.error(request, str(e))
    return redirect("timeline", wedding_id=event.wedding_id)


# ---------- Scene 5: post-wedding settlement ----------
@login_required
def settlement(request, wedding_id=None, id=None):
    wedding = get_object_or_404(Wedding, pk=wedding_id or id)
    rows = services.compute_settlement(wedding)
    client = services.client_invoice(wedding)
    extras = wedding.extras.select_related("wedding_vendor__vendor").all()
    extra_form = ExtraChargeForm(wedding=wedding)
    return render(request, "core/settlement.html", {
        "wedding": wedding,
        "rows": rows,
        "extras": extras,
        "client": client,
        "client_total": client["total"],
        "extra_form": extra_form,
    })


@login_required
@require_POST
def extra_add(request, wedding_id=None, id=None):
    wedding = get_object_or_404(Wedding, pk=wedding_id or id)
    form = ExtraChargeForm(request.POST, wedding=wedding)
    if form.is_valid():
        try:
            services.add_extra_charge(
                wedding=wedding,
                wedding_vendor=form.cleaned_data.get("wedding_vendor"),
                description=form.cleaned_data.get("description"),
                quantity=form.cleaned_data.get("quantity"),
                client_unit_price=form.cleaned_data.get("client_unit_price"),
                vendor_unit_cost=form.cleaned_data.get("vendor_unit_cost") or Decimal("0"),
            )
            messages.success(request, "Extra charge added.")
        except services.ServiceError as e:
            messages.error(request, str(e))
    else:
        for field, errors in form.errors.items():
            for err in errors:
                messages.error(request, f"{field}: {err}" if field != "__all__" else err)
    return redirect("settlement", wedding_id=wedding.id)


@login_required
@require_POST
def extra_approve(request, extra_id=None, id=None):
    extra = get_object_or_404(ExtraCharge, pk=extra_id or id)
    try:
        services.approve_extra(extra)
        messages.success(request, f"Extra charge '{extra.description}' approved.")
    except services.ServiceError as e:
        messages.error(request, str(e))
    return redirect("settlement", wedding_id=extra.wedding_id)


@login_required
@require_POST
def vendor_pay(request, booking_id=None, id=None):
    booking = get_object_or_404(WeddingVendor, pk=booking_id or id)
    kind = request.POST.get("kind")
    amount_raw = request.POST.get("amount", "").strip()
    reference = request.POST.get("reference", "").strip()

    amount = None
    if amount_raw:
        try:
            amount = Decimal(amount_raw)
        except Exception:
            messages.error(request, "Invalid payment amount.")
            return redirect("settlement", wedding_id=booking.wedding_id)

    try:
        services.record_vendor_payment(
            wedding_vendor=booking,
            kind=kind,
            amount=amount,
            user=request.user,
            reference=reference,
        )
        messages.success(request, f"Payment recorded for {booking.vendor.name}.")
    except services.ServiceError as e:
        messages.error(request, str(e))
    return redirect("settlement", wedding_id=booking.wedding_id)


@login_required
@require_POST
def client_pay(request, wedding_id=None, id=None):
    wedding = get_object_or_404(Wedding, pk=wedding_id or id)
    kind = request.POST.get("kind")
    try:
        services.pay_client_stage(wedding, kind)
        messages.success(request, f"Client payment for '{kind}' recorded.")
    except services.ServiceError as e:
        messages.error(request, str(e))
    return redirect("settlement", wedding_id=wedding.id)


@login_required
@require_POST
def settlement_close(request, wedding_id=None, id=None):
    wedding = get_object_or_404(Wedding, pk=wedding_id or id)
    try:
        services.close_settlement(wedding)
        messages.success(request, f"Wedding settlement closed for {wedding.couple_name}.")
    except services.ServiceError as e:
        messages.error(request, str(e))
    return redirect("settlement", wedding_id=wedding.id)


# ---------- Scene 6: founder's season review ----------
def founder_required(view_func):
    """Decorator ensuring user is a superuser or belongs to the Founder group, else 403."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden("Founder access required.")
        is_founder = request.user.is_superuser or request.user.groups.filter(name="Founder").exists()
        if not is_founder:
            return HttpResponseForbidden("Founder access required.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view


@founder_required
def season(request):
    weddings, totals = services.season_summary()
    profit_data = {
        "labels": [w["couple_name"] for w in weddings],
        "profits": [float(w["profit"]) for w in weddings],
    }
    vendors = services.vendor_scorecard()
    dues = services.upcoming_dues()
    token = services.share_token_for_season()
    share_url = request.build_absolute_uri(reverse("season_share", kwargs={"token": token}))

    return render(request, "core/season.html", {
        "weddings": weddings,
        "totals": totals,
        "profit_data": profit_data,
        "vendors": vendors,
        "dues": dues,
        "share_url": share_url,
    })


@founder_required
def season_csv(request):
    weddings, _ = services.season_summary()
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="season_report.csv"'
    writer = csv.writer(response)
    writer.writerow(["wedding", "date", "revenue", "vendor_cost", "labour_cost", "profit", "margin"])
    for w in weddings:
        writer.writerow([
            w["couple_name"],
            w["start_date"],
            w["revenue"],
            w["vendor_cost"],
            w["labour_cost"],
            w["profit"],
            w["margin"],
        ])
    return response


def season_share(request, token):
    try:
        services.verify_share_token(token)
    except services.ServiceError as e:
        return HttpResponseForbidden(str(e))

    weddings, totals = services.season_summary()
    profit_data = {
        "labels": [w["couple_name"] for w in weddings],
        "profits": [float(w["profit"]) for w in weddings],
    }
    vendors = services.vendor_scorecard()
    dues = services.upcoming_dues()

    return render(request, "core/season.html", {
        "weddings": weddings,
        "totals": totals,
        "profit_data": profit_data,
        "vendors": vendors,
        "dues": dues,
    })


@login_required
def wedding_profit(request, wedding_id=None, id=None):
    wedding = get_object_or_404(Wedding, pk=wedding_id or id)
    profit = services.wedding_profit(wedding)
    return render(request, "core/wedding_profit.html", {
        "wedding": wedding,
        "profit": profit,
    })


# ---------- Digital Agreement & Invoices (Scene 1) ----------
@login_required
def agreement(request, lead_id=None, id=None):
    lead = get_object_or_404(Lead, pk=lead_id or id)
    agmt = services.create_agreement(lead)
    return render(request, "core/agreement.html", {"lead": lead, "agreement": agmt})


@login_required
@require_POST
def agreement_sign(request, agreement_id=None, id=None):
    agmt = get_object_or_404(Agreement, pk=agreement_id or id)
    signer_name = request.POST.get("signer_name")
    signature = request.POST.get("signature")

    if not signature and request.content_type == "application/json":
        try:
            import json
            data = json.loads(request.body)
            signer_name = signer_name or data.get("signer_name")
            signature = data.get("signature")
        except Exception:
            pass

    try:
        agmt = services.sign_agreement(agmt, signer_name, signature)
        pdf_url = reverse("agreement_pdf", kwargs={"agreement_id": agmt.id})
        return JsonResponse({"ok": True, "pdf_url": pdf_url})
    except services.ServiceError as e:
        return JsonResponse({"ok": False, "error": str(e)}, status=400)


@login_required
def agreement_pdf(request, agreement_id=None, id=None):
    agmt = get_object_or_404(Agreement, pk=agreement_id or id)
    if not agmt.is_signed or not agmt.signed_pdf:
        raise Http404("Agreement is not signed.")
    try:
        agmt.signed_pdf.seek(0)
        content = agmt.signed_pdf.read()
    except Exception:
        raise Http404("PDF file not found.")
    response = HttpResponse(content, content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="agreement_{agmt.id}.pdf"'
    return response


@login_required
def invoice_pdf(request, wedding_id=None, id=None):
    wedding = get_object_or_404(Wedding, pk=wedding_id or id)
    pdf_bytes = services.build_invoice_pdf(wedding)
    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="invoice_{wedding.id}.pdf"'
    return response


@login_required
def agreement_whatsapp(request, lead_id=None, id=None):
    lead = get_object_or_404(Lead, pk=lead_id or id)
    digits = "".join(ch for ch in lead.phone if ch.isdigit())
    phone_number = ("91" + digits) if len(digits) == 10 else digits
    agreement_url = request.build_absolute_uri(reverse("agreement", kwargs={"lead_id": lead.id}))
    msg = f"Hello {lead.couple_name}, please review and sign your wedding planning service agreement: {agreement_url}"
    return redirect(f"https://wa.me/{phone_number}?text={quote(msg)}")


