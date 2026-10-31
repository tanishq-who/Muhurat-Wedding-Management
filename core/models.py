from decimal import Decimal
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

User = settings.AUTH_USER_MODEL
POS = [MinValueValidator(Decimal("0.01"))]


class Lead(models.Model):
    class Stage(models.TextChoices):
        NEW = "new", "New"
        MEETING = "meeting", "Meeting"
        AGREEMENT = "agreement", "Agreement"
        CONFIRMED = "confirmed", "Confirmed"
        LOST = "lost", "Lost"

    class Source(models.TextChoices):
        CALL = "call", "Call"
        INSTAGRAM = "instagram", "Instagram"
        WHATSAPP = "whatsapp", "WhatsApp"
        OTHER = "other", "Other"

    couple_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    source = models.CharField(max_length=20, choices=Source.choices, default=Source.CALL)
    tentative_date = models.DateField()
    guest_count = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    theme = models.CharField(max_length=100, blank=True)
    max_budget = models.DecimalField(max_digits=14, decimal_places=2, validators=POS)
    package = models.CharField(max_length=20, choices=[("full", "Full-Service"), ("partial", "Partial / Day-of")], default="full")
    stage = models.CharField(max_length=20, choices=Stage.choices, default=Stage.NEW)
    planner = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="leads")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.couple_name} ({self.get_stage_display()})"


class Wedding(models.Model):
    class Status(models.TextChoices):
        PLANNING = "planning", "Planning"
        LIVE = "live", "Wedding Day"
        COMPLETED = "completed", "Completed"
        SETTLED = "settled", "Settled"

    lead = models.OneToOneField(Lead, null=True, blank=True, on_delete=models.SET_NULL)
    couple_name = models.CharField(max_length=150)
    package = models.CharField(max_length=20, choices=[("full", "Full-Service"), ("partial", "Partial / Day-of")])
    theme = models.CharField(max_length=100, blank=True)
    venue = models.CharField(max_length=150, blank=True)
    city = models.CharField(max_length=60, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    guest_count = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    budget = models.DecimalField(max_digits=14, decimal_places=2, validators=POS)
    package_price = models.DecimalField(max_digits=14, decimal_places=2, validators=POS)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PLANNING)
    planner = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="weddings")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["start_date"]

    def clean(self):
        if self.end_date and self.start_date and self.end_date < self.start_date:
            raise ValidationError("End date cannot be before start date.")

    def __str__(self):
        return f"{self.couple_name} - {self.start_date}"


class Agreement(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name="agreements")
    signer_name = models.CharField(max_length=150)
    signature_image = models.ImageField(upload_to="signatures/", blank=True)
    signed_pdf = models.FileField(upload_to="agreements/", blank=True)
    signed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def is_signed(self):
        return self.signed_at is not None


class Vendor(models.Model):
    name = models.CharField(max_length=150)
    category = models.CharField(max_length=50)  # caterer, decorator, DJ, makeup...
    phone = models.CharField(max_length=20, blank=True)
    city = models.CharField(max_length=60, blank=True)
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=Decimal("4.0"))

    def __str__(self):
        return f"{self.name} ({self.category})"


class WeddingVendor(models.Model):
    """A vendor hired for one wedding, with the agreed amount."""
    wedding = models.ForeignKey(Wedding, on_delete=models.CASCADE, related_name="vendors")
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT, related_name="bookings")
    role = models.CharField(max_length=80)
    agreed_amount = models.DecimalField(max_digits=14, decimal_places=2, validators=POS)
    expected_arrival = models.DateTimeField(null=True, blank=True)
    responsible = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        unique_together = ("wedding", "vendor", "role")

    def __str__(self):
        return f"{self.vendor.name} @ {self.wedding.couple_name}"


class VendorCheckIn(models.Model):
    wedding_vendor = models.OneToOneField(WeddingVendor, on_delete=models.CASCADE, related_name="checkin")
    arrived_at = models.DateTimeField()
    checked_in_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    note = models.CharField(max_length=200, blank=True)


class Quote(models.Model):
    class Status(models.TextChoices):
        REQUESTED = "requested", "Requested"
        RECEIVED = "received", "Received"
        SELECTED = "selected", "Selected"
        CLOSED = "closed", "Closed"

    wedding = models.ForeignKey(Wedding, on_delete=models.CASCADE, related_name="quotes")
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT)
    category = models.CharField(max_length=50, default="caterer")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.REQUESTED)
    extra_hour_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total(self):
        return sum((l.line_total for l in self.lines.all()), Decimal("0"))

    @property
    def price_per_plate(self):
        g = self.wedding.guest_count
        return (self.total / g).quantize(Decimal("0.01")) if g else Decimal("0")


class QuoteLine(models.Model):
    quote = models.ForeignKey(Quote, on_delete=models.CASCADE, related_name="lines")
    description = models.CharField(max_length=200)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1, validators=POS)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, validators=POS)

    @property
    def line_total(self):
        return self.quantity * self.unit_price


class Task(models.Model):
    class Stage(models.TextChoices):
        TO_PLAN = "to_plan", "To Plan"
        IN_PROGRESS = "in_progress", "In Progress"
        REVIEW = "review", "Review"
        DONE = "done", "Done"

    wedding = models.ForeignKey(Wedding, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=40)  # Venue, Design, Vendors, Mehendi, Sangeet, Wedding, Reception
    owner = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    stage = models.CharField(max_length=20, choices=Stage.choices, default=Stage.TO_PLAN)
    due_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["due_date", "id"]


class ClientPayment(models.Model):
    class Kind(models.TextChoices):
        BOOKING = "booking", "Booking"
        ADVANCE = "advance", "Advance"
        FINAL = "final", "Final"

    wedding = models.ForeignKey(Wedding, on_delete=models.CASCADE, related_name="client_payments")
    kind = models.CharField(max_length=20, choices=Kind.choices)
    amount = models.DecimalField(max_digits=14, decimal_places=2, validators=POS)
    due_date = models.DateField()
    paid_on = models.DateField(null=True, blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["wedding", "kind"], name="one_payment_per_stage")]

    @property
    def is_paid(self):
        return self.paid_on is not None


class VendorPayment(models.Model):
    class Kind(models.TextChoices):
        ADVANCE = "advance", "Advance"
        BALANCE = "balance", "Balance"

    wedding_vendor = models.ForeignKey(WeddingVendor, on_delete=models.CASCADE, related_name="payments")
    kind = models.CharField(max_length=20, choices=Kind.choices)
    amount = models.DecimalField(max_digits=14, decimal_places=2, validators=POS)
    due_date = models.DateField(null=True, blank=True)
    paid_on = models.DateField(null=True, blank=True)
    reference = models.CharField(max_length=80, blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["wedding_vendor", "kind"], name="no_duplicate_vendor_payment")]

    @property
    def is_paid(self):
        return self.paid_on is not None


class ExtraCharge(models.Model):
    wedding = models.ForeignKey(Wedding, on_delete=models.CASCADE, related_name="extras")
    wedding_vendor = models.ForeignKey(WeddingVendor, null=True, blank=True, on_delete=models.SET_NULL, related_name="extras")
    description = models.CharField(max_length=200)  # e.g. 60 extra plates
    quantity = models.DecimalField(max_digits=10, decimal_places=2, validators=POS)
    client_unit_price = models.DecimalField(max_digits=12, decimal_places=2, validators=POS)
    vendor_unit_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    approved = models.BooleanField(default=False)

    @property
    def client_total(self):
        return self.quantity * self.client_unit_price

    @property
    def vendor_total(self):
        return self.quantity * self.vendor_unit_cost


class ScheduleEvent(models.Model):
    class Status(models.TextChoices):
        UPCOMING = "upcoming", "Upcoming"
        ONGOING = "ongoing", "Ongoing"
        DONE = "done", "Done"
        DELAYED = "delayed", "Delayed"

    wedding = models.ForeignKey(Wedding, on_delete=models.CASCADE, related_name="events")
    start_time = models.DateTimeField()
    title = models.CharField(max_length=150)  # Groom arrival, Garland exchange, Vows, Reception
    responsible = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.UPCOMING)

    class Meta:
        ordering = ["start_time"]


class TimeLog(models.Model):
    wedding = models.ForeignKey(Wedding, on_delete=models.CASCADE, related_name="time_logs")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    hours = models.DecimalField(max_digits=5, decimal_places=2, validators=POS)
    hourly_cost = models.DecimalField(max_digits=8, decimal_places=2, default=500)
    note = models.CharField(max_length=200, blank=True)
