"""
Seed demo data for Muhurat.
Run:  python manage.py seed_data --reset
"""
import random
from datetime import date, datetime, time, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from core.models import (
    Agreement, ClientPayment, ExtraCharge, Lead, Quote, QuoteLine,
    ScheduleEvent, Task, TimeLog, Vendor, VendorCheckIn, VendorPayment,
    Wedding, WeddingVendor,
)

User = get_user_model()
PASSWORD = "muhurat123"

USERS = [  # username, first, last, group
    ("founder", "Meera", "Rathore", "Founder"),
    ("planner1", "Aditi", "Sharma", "Planner"),
    ("planner2", "Rohit", "Singhvi", "Planner"),
    ("planner3", "Kavita", "Joshi", "Planner"),
    ("staff1", "Imran", "Khan", "Staff"),
    ("staff2", "Deepak", "Meena", "Staff"),
    ("staff3", "Suman", "Gehlot", "Staff"),
]

# role, share of vendor spend, usual arrival hour on the last wedding day
ROLES = [
    ("Venue", 18, 6), ("Caterer", 20, 12), ("Decorator", 14, 7), ("Florist", 5, 8),
    ("Photographer", 5, 15), ("Videographer", 4, 15), ("DJ", 3, 17),
    ("Dhol Drummer", 1, 17), ("Makeup Artist", 2, 13), ("Mehendi Artist", 1.5, 11),
    ("Lighting & Sound", 4, 11), ("Transport", 3, 14), ("Guest Accommodation", 9, 10),
    ("Baraat Band", 1.5, 17), ("Pandit", 0.5, 18), ("Performers", 2, 16),
    ("Invitations & Gifts", 2, 9), ("Security & Valet", 1.5, 9),
]
PREFIXES = ["Royal", "Shree", "Rajwada", "Mewar", "Marwar", "Pink City",
            "Lake City", "Golden", "Aravalli", "Heritage", "Maharani", "Regal"]

COUPLES = [
    ("Aarav", "Ananya"), ("Rohan", "Priya"), ("Vikram", "Meera"), ("Arjun", "Kavya"),
    ("Siddharth", "Ishita"), ("Karan", "Neha"), ("Aditya", "Riya"), ("Rahul", "Sneha"),
    ("Kabir", "Tara"), ("Ishaan", "Diya"), ("Dev", "Anjali"), ("Yash", "Pooja"),
    ("Harsh", "Simran"), ("Nikhil", "Aditi"), ("Manav", "Shreya"), ("Varun", "Nisha"),
    ("Kunal", "Radhika"), ("Tejas", "Mitali"), ("Rishi", "Avni"), ("Pranav", "Sanya"),
    ("Aryan", "Kritika"), ("Dhruv", "Naina"), ("Samar", "Zoya"), ("Veer", "Mahi"),
    ("Ayaan", "Rhea"),
]
VENUES = [("Amer Heritage Palace", "Jaipur"), ("Pichola Lake Haveli", "Udaipur"),
          ("Sheesh Mahal Resort", "Jaipur"), ("Aravalli Fort Resort", "Udaipur"),
          ("Moti Bagh Palace", "Jaipur"), ("Fateh Sagar Gardens", "Udaipur")]
THEMES = ["Royal Heritage", "Beach Chic", "Floral Pastel", "Regal Gold",
          "Boho Garden", "Lakeside Elegance", "Rajputana Royale"]

# title, category, days relative to the first wedding day
TASKS = [
    ("Shortlist and visit venues", "Venue", -150), ("Finalise venue contract", "Venue", -140),
    ("Plan seating and floor layout", "Venue", -60), ("Arrange guest room allocation", "Venue", -45),
    ("Finalise theme and mood board", "Design", -135), ("Approve stage and mandap design", "Design", -90),
    ("Order floral and decor materials", "Design", -50), ("Approve invitation design and print", "Design", -110),
    ("Request three caterer quotes", "Vendors", -130), ("Finalise caterer and menu tasting", "Vendors", -100),
    ("Book photographer and videographer", "Vendors", -105), ("Book DJ, dhol and band", "Vendors", -95),
    ("Book makeup and mehendi artists", "Vendors", -90), ("Confirm transport and guest pickups", "Vendors", -40),
    ("Collect vendor contracts", "Vendors", -70), ("Send invitations and track RSVPs", "Guests", -75),
    ("Confirm final guest count", "Guests", -20), ("Plan Mehendi ceremony", "Mehendi", -3),
    ("Run Mehendi day", "Mehendi", 0), ("Plan Sangeet performances", "Sangeet", -20),
    ("Sound and lighting check for Sangeet", "Sangeet", 1), ("Wedding rehearsal (practice run)", "Wedding", -2),
    ("Baraat and groom arrival coordination", "Wedding", 2), ("Garland exchange and vows coordination", "Wedding", 2),
    ("Vendor check-in and control desk", "Wedding", 2), ("Plan reception menu and entertainment", "Reception", -25),
    ("Run reception", "Reception", 2), ("Post-event cleanup and handover", "Reception", 3),
    ("Collect extra bills and settle vendors", "Reception", 7),
]

DAY_EVENTS = [  # day offset, hour, minute, title
    (0, 16, 0, "Mehendi ceremony"), (1, 19, 0, "Sangeet night"),
    (2, 15, 0, "Venue and vendor setup complete"), (2, 17, 30, "Groom arrival (Baraat)"),
    (2, 18, 30, "Garland exchange (Jaimala)"), (2, 20, 0, "Wedding vows (Pheras)"),
    (2, 21, 30, "Reception"),
]

# (description, is_per_plate, unit_price) for the 3 competing caterer quotes
QUOTE_LINES = [
    [("Regional thali menu (per plate)", True, 1850), ("Live chaat and dosa counters", False, 180000),
     ("Service staff and captains", False, 120000)],
    [("Regional menu with 2 sweets (per plate)", True, 1700), ("Crockery and serviceware", False, 150000),
     ("Service staff", False, 140000), ("Late-night snack counter", False, 90000)],
    [("Premium regional menu (per plate)", True, 2150), ("Live counters and mocktail bar", False, 110000)],
]

OPEN_LEADS = [("Ritvik & Anushka", "new"), ("Mohit & Tanvi", "new"), ("Lakshya & Prerna", "new"),
              ("Aniket & Sakshi", "meeting"), ("Jay & Palak", "meeting"),
              ("Utkarsh & Bhavna", "agreement"), ("Sameer & Hetal", "agreement"),
              ("Gaurav & Ritu", "lost")]

BASE_DATE = date(2026, 8, 15)
LIVE_INDEX = 12          # Harsh & Simran: wedding day is TODAY
QUOTE_DEMO_INDEX = 23    # Veer & Mahi: 3 caterer quotes waiting
BARE_INDEX = 24          # Ayaan & Rhea: nothing created yet (for plan generator demo)
LOSS = {3, 6, 8, 15}     # loss-making weddings
LOW_MARGIN = {5, 17}     # thin-margin weddings


def rnd(x, step=1000):
    """Round a number to the nearest `step` and return a Decimal."""
    return Decimal(int(round(float(x) / step)) * step)


def phone():
    return "9" + "".join(random.choices("0123456789", k=9))


class Command(BaseCommand):
    help = "Create demo data: users, vendors, 25 weddings and everything around them."

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true", help="Delete old demo data first")

    @transaction.atomic
    def handle(self, *args, **opts):
        random.seed(42)  # same data every run
        if opts["reset"]:
            self.wipe()
        elif Wedding.objects.exists():
            self.stdout.write(self.style.WARNING("Data already exists. Use --reset to rebuild."))
            return

        self.now = timezone.localtime()
        self.today = self.now.date()

        planners = self.make_users()
        vendors_by_role = self.make_vendors()
        for i in range(25):
            self.make_wedding(i, planners, vendors_by_role)
        self.make_open_leads(planners)

        self.stdout.write(self.style.SUCCESS(
            f"Done: {Wedding.objects.count()} weddings, {Vendor.objects.count()} vendors, "
            f"{WeddingVendor.objects.count()} bookings, {Task.objects.count()} tasks, "
            f"{Lead.objects.count()} leads. Login: founder / {PASSWORD}"))

    # ---------- helpers ----------
    def at(self, d, hour, minute=0):
        return timezone.make_aware(datetime.combine(d, time(hour, minute)))

    def wipe(self):
        Wedding.objects.all().delete()
        Lead.objects.all().delete()
        Vendor.objects.all().delete()
        User.objects.filter(username__in=[u[0] for u in USERS]).delete()

    def make_users(self):
        groups = {n: Group.objects.get_or_create(name=n)[0] for n in ("Founder", "Planner", "Staff")}
        planners = []
        for username, first, last, group in USERS:
            user, _ = User.objects.get_or_create(
                username=username, defaults={"first_name": first, "last_name": last})
            user.set_password(PASSWORD)
            user.save()
            user.groups.add(groups[group])
            if group == "Planner":
                planners.append(user)
        return planners

    def make_vendors(self):
        result = {}
        for role, _, _ in ROLES:
            result[role] = [
                Vendor.objects.create(
                    name=f"{p} {role} Co.", category=role, phone=phone(),
                    city=random.choice(["Jaipur", "Udaipur"]),
                    rating=Decimal(str(round(random.uniform(3.5, 4.9), 1))))
                for p in random.sample(PREFIXES, 3)
            ]
        return result

    # ---------- one wedding ----------
    def make_wedding(self, i, planners, vendors_by_role):
        today, now = self.today, self.now
        start = BASE_DATE + timedelta(days=i * 8)
        if i == LIVE_INDEX:
            start = today - timedelta(days=2)
        end = start + timedelta(days=2)

        if end < today - timedelta(days=7):
            status = Wedding.Status.SETTLED
        elif end < today:
            status = Wedding.Status.COMPLETED
        elif start <= today:
            status = Wedding.Status.LIVE
        else:
            status = Wedding.Status.PLANNING

        groom, bride = COUPLES[i]
        guests = random.randrange(400, 701, 10)
        budget = rnd(random.uniform(1.0e7, 5.0e7), 100000)       # 1 to 5 crore
        vendor_target = float(budget) * random.uniform(0.62, 0.72)
        if i in LOSS:
            factor = random.uniform(0.90, 0.96)
        elif i in LOW_MARGIN:
            factor = 1.10
        else:
            factor = random.uniform(1.18, 1.38)
        package_price = rnd(vendor_target * factor, 10000)
        planner = planners[i % len(planners)]
        venue, city = random.choice(VENUES)

        wedding = Wedding.objects.create(
            couple_name=f"{groom} & {bride}", package="full", theme=random.choice(THEMES),
            venue=venue, city=city, start_date=start, end_date=end, guest_count=guests,
            budget=budget, package_price=package_price, status=status, planner=planner)

        # Lead + signed agreement
        lead = Lead.objects.create(
            couple_name=wedding.couple_name, phone=phone(),
            email=f"{groom.lower()}.{bride.lower()}@example.com",
            source=random.choice(Lead.Source.values), tentative_date=start,
            guest_count=guests, theme=wedding.theme, max_budget=budget, package="full",
            stage=Lead.Stage.CONFIRMED, planner=planner)
        Agreement.objects.create(lead=lead, signer_name=f"{groom} & {bride}",
                                 signed_at=self.at(start - timedelta(days=130), 11))
        wedding.lead = lead
        wedding.save(update_fields=["lead"])

        if i == BARE_INDEX:   # leave empty so the plan generator can be demoed
            return

        # Vendors booked for this wedding
        wvs = {}
        total_weight = sum(w for _, w, _ in ROLES)
        for role, weight, hour in ROLES:
            if i == QUOTE_DEMO_INDEX and role == "Caterer":
                continue  # caterer still undecided: 3 quotes instead
            wvs[role] = WeddingVendor.objects.create(
                wedding=wedding, vendor=random.choice(vendors_by_role[role]), role=role,
                agreed_amount=rnd(vendor_target * weight / total_weight * random.uniform(0.9, 1.1)),
                expected_arrival=self.at(end, hour, random.choice([0, 15, 30, 45])),
                responsible=random.choice(planners))

        if i == QUOTE_DEMO_INDEX:
            self.make_quotes(wedding, guests, vendors_by_role["Caterer"])

        extra_cost = self.make_extras(wedding, wvs, status, i)
        self.make_client_payments(wedding, package_price, start, end, status)
        self.make_vendor_payments(wvs, start, end, status, extra_cost)
        self.make_tasks(wedding, planners, start, status, i)
        self.make_events(wedding, planners, start, status)
        self.make_checkins(wvs, status)
        self.make_timelogs(wedding, planners, start)

    # ---------- pieces ----------
    def make_quotes(self, wedding, guests, caterers):
        for vendor, lines, rate in zip(caterers, QUOTE_LINES, (9000, 12000, 15000)):
            quote = Quote.objects.create(
                wedding=wedding, vendor=vendor, category="Caterer",
                status=Quote.Status.RECEIVED, extra_hour_rate=rate,
                notes=f"Regional menu for about {guests} guests")
            for desc, per_plate, price in lines:
                QuoteLine.objects.create(quote=quote, description=desc,
                                         quantity=guests if per_plate else 1, unit_price=price)

    def make_extras(self, wedding, wvs, status, i):
        """Create extra charges; return {wedding_vendor_id: approved vendor cost}."""
        cost = {}

        def add(role, desc, qty, client_price, vendor_cost, approved):
            wv = wvs.get(role)
            extra = ExtraCharge.objects.create(
                wedding=wedding, wedding_vendor=wv, description=desc, quantity=Decimal(qty),
                client_unit_price=Decimal(client_price), vendor_unit_cost=Decimal(vendor_cost),
                approved=approved)
            if wv and approved:
                cost[wv.id] = cost.get(wv.id, Decimal("0")) + extra.vendor_total

        settled = status == Wedding.Status.SETTLED
        if status in (Wedding.Status.SETTLED, Wedding.Status.COMPLETED):
            plates = 60 if i == 9 else random.randrange(30, 81, 10)
            add("Caterer", f"{plates} extra plates at banquet", plates, 1800, 1400, True)
            add("DJ", "Extra DJ hours", random.randint(1, 3), 15000, 10000, settled)
        elif status == Wedding.Status.LIVE:
            add("Florist", "Extra generator for florist", 1, 12000, 9000, False)
        return cost

    def make_client_payments(self, wedding, price, start, end, status):
        booking = rnd(float(price) * 0.30)
        advance = rnd(float(price) * 0.40)
        final = price - booking - advance
        today = self.today
        plan = [
            ("booking", booking, start - timedelta(days=120)),
            ("advance", advance, start - timedelta(days=30)),
            ("final", final, end + timedelta(days=7)),
        ]
        for kind, amount, due in plan:
            if kind == "booking":
                paid = due <= today
            elif kind == "advance":
                paid = due <= today and (status != Wedding.Status.PLANNING or random.random() < 0.8)
            else:
                paid = status == Wedding.Status.SETTLED
            ClientPayment.objects.create(wedding=wedding, kind=kind, amount=amount, due_date=due,
                                         paid_on=due if paid else None)

    def make_vendor_payments(self, wvs, start, end, status, extra_cost):
        today = self.today
        for wv in wvs.values():
            advance = rnd(float(wv.agreed_amount) * random.choice([0.3, 0.4, 0.5]))
            adv_due = start - timedelta(days=30)
            VendorPayment.objects.create(
                wedding_vendor=wv, kind="advance", amount=advance, due_date=adv_due,
                paid_on=adv_due if adv_due <= today else None)
            bal_due = end + timedelta(days=7)
            balance = wv.agreed_amount - advance + extra_cost.get(wv.id, Decimal("0"))
            VendorPayment.objects.create(
                wedding_vendor=wv, kind="balance", amount=balance, due_date=bal_due,
                paid_on=bal_due if status == Wedding.Status.SETTLED else None)

    def make_tasks(self, wedding, planners, start, status, i):
        today = self.today
        finished = status in (Wedding.Status.SETTLED, Wedding.Status.COMPLETED)
        for n, (title, category, offset) in enumerate(TASKS):
            due = start + timedelta(days=offset)
            if finished or due < today - timedelta(days=7):
                stage = Task.Stage.DONE
            elif due <= today + timedelta(days=7):
                stage = random.choice([Task.Stage.IN_PROGRESS, Task.Stage.REVIEW])
            else:
                stage = Task.Stage.TO_PLAN
            Task.objects.create(wedding=wedding, title=title, category=category,
                                owner=planners[(i + n) % len(planners)], stage=stage, due_date=due)

    def make_events(self, wedding, planners, start, status):
        now = self.now
        for day, hour, minute, title in DAY_EVENTS:
            st = self.at(start + timedelta(days=day), hour, minute)
            if st + timedelta(minutes=90) < now:
                s = ScheduleEvent.Status.DONE
            elif st <= now:
                s = ScheduleEvent.Status.ONGOING
            else:
                s = ScheduleEvent.Status.UPCOMING
            ScheduleEvent.objects.create(wedding=wedding, start_time=st, title=title,
                                         responsible=random.choice(planners), status=s)
        if status == Wedding.Status.LIVE:   # the bride's car stuck in traffic
            ScheduleEvent.objects.create(
                wedding=wedding, start_time=self.at(start + timedelta(days=2), 17, 0),
                title="Bride's car arrives from hotel", responsible=random.choice(planners),
                status=ScheduleEvent.Status.DELAYED)

    def make_checkins(self, wvs, status):
        now = self.now
        if status not in (Wedding.Status.SETTLED, Wedding.Status.COMPLETED, Wedding.Status.LIVE):
            return
        for role, wv in wvs.items():
            exp = wv.expected_arrival
            if status == Wedding.Status.LIVE:
                if role in ("DJ", "Lighting & Sound"):   # running late, never checked in
                    wv.expected_arrival = now - timedelta(minutes=45 if role == "DJ" else 30)
                    wv.save(update_fields=["expected_arrival"])
                    continue
                if exp > now:
                    continue   # not due yet
                offset = random.randint(-10, 10)
            else:
                offset = random.randint(20, 60) if random.random() < 0.15 else random.randint(-15, 5)
            VendorCheckIn.objects.create(wedding_vendor=wv, arrived_at=min(exp + timedelta(minutes=offset), now),
                                         checked_in_by=wv.responsible)

    def make_timelogs(self, wedding, planners, start):
        lo = start - timedelta(days=90)
        hi = min(start + timedelta(days=2), self.today)
        if hi <= lo:
            return
        for _ in range(random.randint(20, 35)):
            TimeLog.objects.create(
                wedding=wedding, user=random.choice(planners),
                date=lo + timedelta(days=random.randint(0, (hi - lo).days)),
                hours=Decimal(random.choice([3, 4, 5, 6, 8])), hourly_cost=Decimal("1200"),
                note="Planning work")

    def make_open_leads(self, planners):
        for couple, stage in OPEN_LEADS:
            lead = Lead.objects.create(
                couple_name=couple, phone=phone(), source=random.choice(Lead.Source.values),
                tentative_date=self.today + timedelta(days=random.randint(60, 150)),
                guest_count=random.randrange(400, 601, 10), theme=random.choice(THEMES),
                max_budget=rnd(random.uniform(1.5e7, 4.0e7), 100000), package="full",
                stage=stage, planner=random.choice(planners))
            if stage == "agreement":
                Agreement.objects.create(lead=lead, signer_name=couple)   # sent but unsigned