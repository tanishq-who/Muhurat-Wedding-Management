from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from . import services
from .forms import LeadFoing
from .models import Lead, Quote, ScheduleEvent, Task, Wedding, WeddingVendor    


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