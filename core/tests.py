import base64
from datetime import date, timedelta
from decimal import Decimal
import io
from unittest.mock import patch

from PIL import Image

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from core import services
from core.forms import ExtraChargeForm
from core.models import (
    Agreement,
    ClientPayment,
    ExtraCharge,
    Lead,
    Quote,
    Task,
    TimeLog,
    Vendor,
    VendorCheckIn,
    VendorPayment,
    Wedding,
    WeddingVendor,
)

User = get_user_model()


class SettlementServicesTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="planner", password="password123")
        self.wedding = Wedding.objects.create(
            couple_name="Aarav & Ananya",
            package="full",
            start_date=date.today() + timedelta(days=60),
            end_date=date.today() + timedelta(days=62),
            guest_count=400,
            budget=Decimal("5000000"),
            package_price=Decimal("4000000"),
            planner=self.user,
        )
        self.vendor1 = Vendor.objects.create(name="Royal Caterers", category="Caterer")
        self.vendor2 = Vendor.objects.create(name="Beat Masters DJ", category="DJ")

        self.wv1 = WeddingVendor.objects.create(
            wedding=self.wedding,
            vendor=self.vendor1,
            role="Caterer",
            agreed_amount=Decimal("300000"),
            responsible=self.user,
        )
        self.wv2 = WeddingVendor.objects.create(
            wedding=self.wedding,
            vendor=self.vendor2,
            role="DJ",
            agreed_amount=Decimal("100000"),
            responsible=self.user,
        )

        # Client payments via plan generation
        services.generate_wedding_plan(self.wedding)

        # Pending vendor payments for each WeddingVendor
        self.wv1_advance = VendorPayment.objects.create(
            wedding_vendor=self.wv1,
            kind=VendorPayment.Kind.ADVANCE,
            amount=Decimal("100000"),
            due_date=date.today() + timedelta(days=30),
        )
        self.wv1_balance = VendorPayment.objects.create(
            wedding_vendor=self.wv1,
            kind=VendorPayment.Kind.BALANCE,
            amount=Decimal("200000"),
            due_date=date.today() + timedelta(days=65),
        )
        self.wv2_advance = VendorPayment.objects.create(
            wedding_vendor=self.wv2,
            kind=VendorPayment.Kind.ADVANCE,
            amount=Decimal("40000"),
            due_date=date.today() + timedelta(days=30),
        )
        self.wv2_balance = VendorPayment.objects.create(
            wedding_vendor=self.wv2,
            kind=VendorPayment.Kind.BALANCE,
            amount=Decimal("60000"),
            due_date=date.today() + timedelta(days=65),
        )

    def test_approve_extra_twice_raises_service_error(self):
        """1. approve_extra twice raises ServiceError."""
        extra = services.add_extra_charge(
            wedding=self.wedding,
            wedding_vendor=self.wv1,
            description="Extra welcome drinks",
            quantity=Decimal("50"),
            client_unit_price=Decimal("200"),
            vendor_unit_cost=Decimal("120"),
        )
        self.assertFalse(extra.approved)
        services.approve_extra(extra)
        extra.refresh_from_db()
        self.assertTrue(extra.approved)

        with self.assertRaises(services.ServiceError):
            services.approve_extra(extra)

    def test_approved_extra_raises_owed_and_invoice_unapproved_does_not(self):
        """2. An approved extra raises the vendor's owed amount and the client invoice total; an unapproved one does not."""
        initial_rows = services.compute_settlement(self.wedding)
        initial_wv1_owed = next(r for r in initial_rows if r["booking"] == self.wv1)["owed"]
        initial_invoice = services.client_invoice(self.wedding)
        initial_client_total = initial_invoice["total"]

        self.assertEqual(initial_wv1_owed, Decimal("300000"))
        self.assertEqual(initial_client_total, Decimal("4000000"))

        # Add unapproved extra
        extra = services.add_extra_charge(
            wedding=self.wedding,
            wedding_vendor=self.wv1,
            description="Midnight snacks",
            quantity=Decimal("100"),
            client_unit_price=Decimal("500"),
            vendor_unit_cost=Decimal("300"),
        )
        # 100 * 500 = 50000 client total, 100 * 300 = 30000 vendor total

        unapproved_rows = services.compute_settlement(self.wedding)
        unapproved_wv1_owed = next(r for r in unapproved_rows if r["booking"] == self.wv1)["owed"]
        unapproved_invoice = services.client_invoice(self.wedding)
        unapproved_client_total = unapproved_invoice["total"]

        # An unapproved extra does NOT raise vendor owed or client total
        self.assertEqual(unapproved_wv1_owed, initial_wv1_owed)
        self.assertEqual(unapproved_client_total, initial_client_total)

        # Now approve extra
        services.approve_extra(extra)

        approved_rows = services.compute_settlement(self.wedding)
        approved_wv1_owed = next(r for r in approved_rows if r["booking"] == self.wv1)["owed"]
        approved_invoice = services.client_invoice(self.wedding)
        approved_client_total = approved_invoice["total"]

        # An approved extra DOES raise vendor owed and client total
        self.assertEqual(approved_wv1_owed, initial_wv1_owed + Decimal("30000"))
        self.assertEqual(approved_client_total, initial_client_total + Decimal("50000"))

    def test_record_vendor_payment_balance_pays_owed_minus_paid(self):
        """3. record_vendor_payment(kind="balance") pays exactly owed minus paid."""
        # Add approved extra for wv1: 20 * 1000 = 20000 vendor cost
        extra = services.add_extra_charge(
            wedding=self.wedding,
            wedding_vendor=self.wv1,
            description="Live chaat counter",
            quantity=Decimal("20"),
            client_unit_price=Decimal("1500"),
            vendor_unit_cost=Decimal("1000"),
        )
        services.approve_extra(extra)
        # Owed is now 300000 + 20000 = 320000

        # Pay advance: 100000
        services.record_vendor_payment(self.wv1, kind="advance", amount=Decimal("100000"))

        # Pay balance (amount typed is ignored/calculated as owed - paid)
        bal_payment = services.record_vendor_payment(self.wv1, kind="balance", amount=Decimal("999999"))
        self.assertEqual(bal_payment.amount, Decimal("220000"))
        self.assertTrue(bal_payment.is_paid)
        self.assertEqual(bal_payment.paid_on, timezone.localdate())

        rows = services.compute_settlement(self.wedding)
        wv1_row = next(r for r in rows if r["booking"] == self.wv1)
        self.assertEqual(wv1_row["paid"], Decimal("320000"))
        self.assertEqual(wv1_row["remaining"], Decimal("0"))
        self.assertEqual(wv1_row["status"], "paid")

    def test_paying_same_kind_twice_raises_service_error(self):
        """4. Paying the same kind twice raises ServiceError."""
        # Pay advance once
        services.record_vendor_payment(self.wv1, kind="advance", amount=Decimal("100000"))

        # Paying advance again raises ServiceError
        with self.assertRaises(services.ServiceError):
            services.record_vendor_payment(self.wv1, kind="advance", amount=Decimal("50000"))

        # Pay balance once
        services.record_vendor_payment(self.wv1, kind="balance")

        # Paying balance again raises ServiceError
        with self.assertRaises(services.ServiceError):
            services.record_vendor_payment(self.wv1, kind="balance")

        # Client payment stage twice raises ServiceError
        services.pay_client_stage(self.wedding, "booking")
        with self.assertRaises(services.ServiceError):
            services.pay_client_stage(self.wedding, "booking")

    def test_advance_larger_than_owed_raises_service_error(self):
        """5. An advance larger than owed raises ServiceError (over-payment)."""
        # wv2 owed is 100000. Trying to pay 120000 advance should fail.
        with self.assertRaises(services.ServiceError):
            services.record_vendor_payment(self.wv2, kind="advance", amount=Decimal("120000"))

    def test_balance_cannot_be_paid_before_advance(self):
        """6. Balance cannot be paid before the advance."""
        # wv2 advance has not been paid yet
        self.assertFalse(self.wv2_advance.is_paid)
        with self.assertRaises(services.ServiceError):
            services.record_vendor_payment(self.wv2, kind="balance")

    def test_pay_client_stage_final_includes_approved_extras(self):
        """7. pay_client_stage("final") includes approved extras in its amount."""
        # Package price: 4000000. Stages: booking (1200000), advance (1600000), final (1200000)
        extra = services.add_extra_charge(
            wedding=self.wedding,
            wedding_vendor=self.wv1,
            description="Grand entry fireworks",
            quantity=Decimal("1"),
            client_unit_price=Decimal("75000"),
            vendor_unit_cost=Decimal("50000"),
        )
        services.approve_extra(extra)

        services.pay_client_stage(self.wedding, "booking")
        services.pay_client_stage(self.wedding, "advance")

        final_stage = services.pay_client_stage(self.wedding, "final")
        self.assertEqual(final_stage.amount, Decimal("1275000"))
        self.assertEqual(final_stage.paid_on, timezone.localdate())

        inv = services.client_invoice(self.wedding)
        self.assertEqual(inv["total"], Decimal("4075000"))
        self.assertEqual(inv["received"], Decimal("4075000"))
        self.assertEqual(inv["balance_due"], Decimal("0"))

    def test_close_settlement_fails_while_unpaid_and_succeeds_when_paid(self):
        """8. close_settlement fails while a vendor or the client is unpaid, and succeeds once everything is paid."""
        # 1. Unapproved extra charge prevents close
        extra = services.add_extra_charge(
            wedding=self.wedding,
            wedding_vendor=self.wv1,
            description="Extra mocktail counter",
            quantity=Decimal("1"),
            client_unit_price=Decimal("20000"),
            vendor_unit_cost=Decimal("12000"),
        )
        with self.assertRaises(services.ServiceError) as ctx:
            services.close_settlement(self.wedding)
        self.assertIn("unapproved", str(ctx.exception).lower())

        services.approve_extra(extra)

        # 2. Vendors unpaid prevents close
        with self.assertRaises(services.ServiceError) as ctx:
            services.close_settlement(self.wedding)
        self.assertIn(self.vendor1.name, str(ctx.exception))

        # Pay vendor 1
        services.record_vendor_payment(self.wv1, kind="advance", amount=Decimal("100000"))
        services.record_vendor_payment(self.wv1, kind="balance")

        # Vendor 2 still unpaid prevents close
        with self.assertRaises(services.ServiceError) as ctx:
            services.close_settlement(self.wedding)
        self.assertIn(self.vendor2.name, str(ctx.exception))

        # Pay vendor 2
        services.record_vendor_payment(self.wv2, kind="advance", amount=Decimal("40000"))
        services.record_vendor_payment(self.wv2, kind="balance")

        # 3. Client unpaid prevents close
        with self.assertRaises(services.ServiceError) as ctx:
            services.close_settlement(self.wedding)
        self.assertIn("client has an outstanding balance", str(ctx.exception).lower())

        # Pay client all stages
        services.pay_client_stage(self.wedding, "booking")
        services.pay_client_stage(self.wedding, "advance")
        services.pay_client_stage(self.wedding, "final")

        # 4. Now close_settlement succeeds
        services.close_settlement(self.wedding)
        self.wedding.refresh_from_db()
        self.assertEqual(self.wedding.status, Wedding.Status.SETTLED)

        # 5. Cannot close already settled wedding
        with self.assertRaises(services.ServiceError):
            services.close_settlement(self.wedding)


class QuoteAndPlanServicesTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="planner2", password="password123")
        self.wedding = Wedding.objects.create(
            couple_name="Rohan & Priya",
            package="full",
            start_date=date.today() + timedelta(days=90),
            end_date=date.today() + timedelta(days=92),
            guest_count=350,
            budget=Decimal("3000000"),
            package_price=Decimal("2500000"),
            planner=self.user,
        )

    def test_select_winning_quote_closes_other_quotes(self):
        v1 = Vendor.objects.create(name="Decorator Alpha", category="Decorator")
        v2 = Vendor.objects.create(name="Decorator Beta", category="Decorator")
        v3 = Vendor.objects.create(name="Decorator Gamma", category="Decorator")

        q1 = Quote.objects.create(wedding=self.wedding, vendor=v1, category="Decorator", status=Quote.Status.REQUESTED)
        q2 = Quote.objects.create(wedding=self.wedding, vendor=v2, category="Decorator", status=Quote.Status.REQUESTED)
        q3 = Quote.objects.create(wedding=self.wedding, vendor=v3, category="Decorator", status=Quote.Status.REQUESTED)

        booking = services.select_winning_quote(q1)
        q1.refresh_from_db()
        q2.refresh_from_db()
        q3.refresh_from_db()

        self.assertEqual(q1.status, Quote.Status.SELECTED)
        self.assertEqual(q2.status, Quote.Status.CLOSED)
        self.assertEqual(q3.status, Quote.Status.CLOSED)
        self.assertEqual(booking.wedding, self.wedding)
        self.assertEqual(booking.vendor, v1)
        self.assertEqual(booking.role, "Decorator")

    def test_generate_wedding_plan_called_twice_no_duplicates(self):
        # First call
        res1 = services.generate_wedding_plan(self.wedding)
        task_count1 = self.wedding.tasks.count()
        payment_count1 = self.wedding.client_payments.count()

        self.assertGreater(task_count1, 0)
        self.assertEqual(payment_count1, 3)
        self.assertEqual(res1["tasks_created"], task_count1)
        self.assertEqual(res1["payments_created"], 3)

        # Second call
        res2 = services.generate_wedding_plan(self.wedding)
        task_count2 = self.wedding.tasks.count()
        payment_count2 = self.wedding.client_payments.count()

        self.assertEqual(task_count2, task_count1)
        self.assertEqual(payment_count2, 3)
        self.assertEqual(res2["tasks_created"], 0)
        self.assertEqual(res2["payments_created"], 0)


class SettlementViewsAndFormTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="planner3", password="password123")
        self.wedding = Wedding.objects.create(
            couple_name="Vikram & Meera",
            package="full",
            start_date=date.today() + timedelta(days=40),
            end_date=date.today() + timedelta(days=42),
            guest_count=300,
            budget=Decimal("4000000"),
            package_price=Decimal("3000000"),
            planner=self.user,
        )
        self.vendor = Vendor.objects.create(name="Star Decor", category="Decorator")
        self.wv = WeddingVendor.objects.create(
            wedding=self.wedding,
            vendor=self.vendor,
            role="Decorator",
            agreed_amount=Decimal("200000"),
            responsible=self.user,
        )
        services.generate_wedding_plan(self.wedding)

    def test_extra_charge_form_limits_queryset(self):
        other_wedding = Wedding.objects.create(
            couple_name="Other Couple",
            package="full",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=2),
            guest_count=100,
            budget=Decimal("1000000"),
            package_price=Decimal("800000"),
            planner=self.user,
        )
        other_vendor = Vendor.objects.create(name="Other DJ", category="DJ")
        other_wv = WeddingVendor.objects.create(
            wedding=other_wedding,
            vendor=other_vendor,
            role="DJ",
            agreed_amount=Decimal("50000"),
        )

        form = ExtraChargeForm(wedding=self.wedding)
        self.assertIn(self.wv, form.fields["wedding_vendor"].queryset)
        self.assertNotIn(other_wv, form.fields["wedding_vendor"].queryset)

    def test_views_flow(self):
        c = Client()
        settlement_url = reverse("settlement", kwargs={"wedding_id": self.wedding.id})

        # Login required
        resp = c.get(settlement_url)
        self.assertEqual(resp.status_code, 302)

        c.force_login(self.user)
        # GET settlement page
        with patch("core.views.render") as mock_render:
            mock_render.return_value = HttpResponse("rendered")
            resp = c.get(settlement_url)
            self.assertEqual(resp.content.decode(), "rendered")
            mock_render.assert_called_once()
            args, kwargs = mock_render.call_args
            self.assertEqual(args[1], "core/settlement.html")
            context = args[2]
            self.assertEqual(context["wedding"], self.wedding)
            self.assertIn("rows", context)
            self.assertIn("extras", context)
            self.assertIn("client", context)
            self.assertEqual(context["client_total"], context["client"]["total"])
            self.assertIn("extra_form", context)

        # POST extra_add
        resp = c.post(
            reverse("extra_add", kwargs={"wedding_id": self.wedding.id}),
            {
                "wedding_vendor": self.wv.id,
                "description": "Extra fairy lights",
                "quantity": "2",
                "client_unit_price": "2500",
                "vendor_unit_cost": "1500",
            },
        )
        self.assertEqual(resp.status_code, 302)
        extra = ExtraCharge.objects.get(description="Extra fairy lights")
        self.assertFalse(extra.approved)

        # POST extra_approve
        resp = c.post(reverse("extra_approve", kwargs={"extra_id": extra.id}))
        self.assertEqual(resp.status_code, 302)
        extra.refresh_from_db()
        self.assertTrue(extra.approved)

        # POST vendor_pay with invalid amount
        resp = c.post(
            reverse("vendor_pay", kwargs={"booking_id": self.wv.id}),
            {"kind": "advance", "amount": "invalid-amount"},
        )
        self.assertEqual(resp.status_code, 302)

        # POST vendor_pay advance
        resp = c.post(
            reverse("vendor_pay", kwargs={"booking_id": self.wv.id}),
            {"kind": "advance", "amount": "50000", "reference": "ADV123"},
        )
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(VendorPayment.objects.filter(wedding_vendor=self.wv, kind="advance", paid_on__isnull=False).exists())

        # POST client_pay
        resp = c.post(
            reverse("client_pay", kwargs={"wedding_id": self.wedding.id}),
            {"kind": "booking"},
        )
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(ClientPayment.objects.get(wedding=self.wedding, kind="booking").is_paid)

        # POST settlement_close (fails because vendors and client stages remain unpaid)
        resp = c.post(reverse("settlement_close", kwargs={"wedding_id": self.wedding.id}))
        self.assertEqual(resp.status_code, 302)
        self.wedding.refresh_from_db()
        self.assertNotEqual(self.wedding.status, Wedding.Status.SETTLED)


class Scene6SeasonReviewTestCase(TestCase):
    def setUp(self):
        from django.contrib.auth.models import Group
        self.founder_group, _ = Group.objects.get_or_create(name="Founder")
        self.founder_user = User.objects.create_user(username="founder_meera", password="password123")
        self.founder_user.groups.add(self.founder_group)
        self.regular_user = User.objects.create_user(username="regular_aditi", password="password123")
        self.superuser = User.objects.create_superuser(username="admin", password="password123")

        self.wedding = Wedding.objects.create(
            couple_name="Kabir & Tara",
            package="full",
            start_date=date.today() + timedelta(days=20),
            end_date=date.today() + timedelta(days=22),
            guest_count=250,
            budget=Decimal("2000000"),
            package_price=Decimal("1500000"),
            planner=self.regular_user,
        )
        self.vendor = Vendor.objects.create(name="Elite Sounds", category="DJ", rating=Decimal("4.5"))
        self.wv = WeddingVendor.objects.create(
            wedding=self.wedding,
            vendor=self.vendor,
            role="DJ",
            agreed_amount=Decimal("80000"),
            expected_arrival=timezone.now() - timedelta(hours=2),
        )
        # Check-in 5 minutes after expected arrival -> on-time!
        VendorCheckIn.objects.create(
            wedding_vendor=self.wv,
            arrived_at=self.wv.expected_arrival + timedelta(minutes=5),
            checked_in_by=self.regular_user,
        )
        # Approved extra charge
        extra = services.add_extra_charge(
            wedding=self.wedding,
            wedding_vendor=self.wv,
            description="Extra sound monitor",
            quantity=Decimal("1"),
            client_unit_price=Decimal("10000"),
            vendor_unit_cost=Decimal("6000"),
        )
        services.approve_extra(extra)

        # Time log: 10 hours at 1000/hr = 10000
        TimeLog.objects.create(
            wedding=self.wedding,
            user=self.regular_user,
            date=date.today(),
            hours=Decimal("10"),
            hourly_cost=Decimal("1000"),
        )

        # Client payment
        ClientPayment.objects.create(
            wedding=self.wedding,
            kind="booking",
            amount=Decimal("450000"),
            due_date=date.today() - timedelta(days=5),
            paid_on=date.today() - timedelta(days=5),
        )
        ClientPayment.objects.create(
            wedding=self.wedding,
            kind="advance",
            amount=Decimal("600000"),
            due_date=date.today() + timedelta(days=10),
        )

        # Vendor payment
        VendorPayment.objects.create(
            wedding_vendor=self.wv,
            kind="advance",
            amount=Decimal("40000"),
            due_date=date.today() - timedelta(days=2),
            paid_on=date.today() - timedelta(days=2),
        )
        VendorPayment.objects.create(
            wedding_vendor=self.wv,
            kind="balance",
            amount=Decimal("46000"),
            due_date=date.today() + timedelta(days=15),
        )

    def test_wedding_profit(self):
        profit_dict = services.wedding_profit(self.wedding)
        # revenue = package_price (1500000) + approved extras (10000) = 1510000
        self.assertEqual(profit_dict["revenue"], Decimal("1510000"))
        # vendor_cost = agreed (80000) + approved extras (6000) = 86000
        self.assertEqual(profit_dict["vendor_cost"], Decimal("86000"))
        # labour_cost = 10 * 1000 = 10000
        self.assertEqual(profit_dict["labour_cost"], Decimal("10000"))
        # profit = 1510000 - 86000 - 10000 = 1414000
        self.assertEqual(profit_dict["profit"], Decimal("1414000"))
        # margin = 1414000 / 1510000 * 100 = 93.6
        self.assertAlmostEqual(profit_dict["margin"], 93.6, places=1)
        # received = paid ClientPayment = 450000
        self.assertEqual(profit_dict["received"], Decimal("450000"))
        # low_margin = margin < 15 = False
        self.assertFalse(profit_dict["low_margin"])
        self.assertEqual(profit_dict["couple_name"], "Kabir & Tara")

        # Revenue includes approved extras only: unapproved extras must NOT increase revenue or vendor cost
        unapproved = services.add_extra_charge(
            wedding=self.wedding,
            wedding_vendor=self.wv,
            description="Unapproved lighting extra",
            quantity=Decimal("1"),
            client_unit_price=Decimal("50000"),
            vendor_unit_cost=Decimal("25000"),
        )
        profit_dict2 = services.wedding_profit(self.wedding)
        self.assertEqual(profit_dict2["revenue"], Decimal("1510000"))
        self.assertEqual(profit_dict2["vendor_cost"], Decimal("86000"))

        # Labour cost counted: adding a time log increases labour cost and reduces profit
        TimeLog.objects.create(
            wedding=self.wedding,
            user=self.regular_user,
            date=date.today(),
            hours=Decimal("5"),
            hourly_cost=Decimal("2000"),
        )
        profit_dict3 = services.wedding_profit(self.wedding)
        self.assertEqual(profit_dict3["labour_cost"], Decimal("20000"))
        self.assertEqual(profit_dict3["profit"], Decimal("1404000"))

        # low_margin flag: True when margin < 15, False when margin >= 15
        self.assertFalse(profit_dict3["low_margin"])
        w_low = Wedding.objects.create(
            couple_name="Low Margin Couple",
            package="essential",
            start_date=date.today() + timedelta(days=30),
            end_date=date.today() + timedelta(days=31),
            guest_count=100,
            budget=Decimal("500000"),
            package_price=Decimal("100000"),
        )
        v_low = Vendor.objects.create(name="Expensive Decorator", category="decorator")
        WeddingVendor.objects.create(
            wedding=w_low,
            vendor=v_low,
            role="decorator",
            agreed_amount=Decimal("90000"),
        )
        profit_low = services.wedding_profit(w_low)
        self.assertEqual(profit_low["margin"], 10.0)
        self.assertTrue(profit_low["low_margin"])

    def test_season_summary(self):
        # Create a second wedding with a loss
        w_loss = Wedding.objects.create(
            couple_name="Loss Couple",
            package="essential",
            start_date=date.today() + timedelta(days=40),
            end_date=date.today() + timedelta(days=41),
            guest_count=50,
            budget=Decimal("200000"),
            package_price=Decimal("50000"),
        )
        v_loss = Vendor.objects.create(name="High Cost Decorator", category="decorator")
        WeddingVendor.objects.create(
            wedding=w_loss,
            vendor=v_loss,
            role="decorator",
            agreed_amount=Decimal("70000"),
        )

        summary = services.season_summary()
        weddings, totals = summary
        self.assertGreaterEqual(len(weddings), 2)

        # Sorted by profit descending
        profits = [w["profit"] for w in weddings]
        self.assertEqual(profits, sorted(profits, reverse=True))

        # Totals match aggregated values
        self.assertEqual(totals["wedding_count"], len(weddings))
        self.assertEqual(totals["total_revenue"], sum(w["revenue"] for w in weddings))
        self.assertEqual(totals["total_cost"], sum(w["vendor_cost"] + w["labour_cost"] for w in weddings))
        self.assertEqual(totals["total_profit"], sum(w["profit"] for w in weddings))
        self.assertEqual(totals["loss_count"], sum(1 for w in weddings if w["profit"] < Decimal("0")))
        self.assertEqual(totals["low_margin_count"], sum(1 for w in weddings if w["low_margin"]))
        self.assertGreaterEqual(totals["loss_count"], 1)

    def test_vendor_scorecard(self):
        # self.vendor already has 1 booking that arrived 5 mins late (<= 10 mins) -> on-time
        # Add 2nd booking that arrived 25 mins late (> 10 mins) -> late
        wv2 = WeddingVendor.objects.create(
            wedding=self.wedding,
            vendor=self.vendor,
            role="DJ Assistant",
            agreed_amount=Decimal("20000"),
            expected_arrival=timezone.now() - timedelta(hours=1),
        )
        VendorCheckIn.objects.create(
            wedding_vendor=wv2,
            arrived_at=wv2.expected_arrival + timedelta(minutes=25),
            checked_in_by=self.regular_user,
        )
        # Add 3rd booking without check-in -> ignored in eligible count
        WeddingVendor.objects.create(
            wedding=self.wedding,
            vendor=self.vendor,
            role="DJ Backup",
            agreed_amount=Decimal("10000"),
            expected_arrival=timezone.now(),
        )

        # Create a second vendor who is 100% on time
        v_punctual = Vendor.objects.create(name="Punctual Catering", category="caterer", rating=Decimal("4.8"))
        wv_punctual = WeddingVendor.objects.create(
            wedding=self.wedding,
            vendor=v_punctual,
            role="caterer",
            agreed_amount=Decimal("60000"),
            expected_arrival=timezone.now() - timedelta(hours=3),
        )
        VendorCheckIn.objects.create(
            wedding_vendor=wv_punctual,
            arrived_at=wv_punctual.expected_arrival - timedelta(minutes=5),
            checked_in_by=self.regular_user,
        )

        scorecard = services.vendor_scorecard()
        # Verify self.vendor: 1 on-time out of 2 eligible = 50.0%
        v_entry = next(item for item in scorecard if item["vendor"] == self.vendor)
        self.assertEqual(v_entry["bookings"], 3)
        self.assertEqual(v_entry["on_time_rate"], 50.0)

        # Verify v_punctual: 1 on-time out of 1 eligible = 100.0%
        p_entry = next(item for item in scorecard if item["vendor"] == v_punctual)
        self.assertEqual(p_entry["bookings"], 1)
        self.assertEqual(p_entry["on_time_rate"], 100.0)

        # Scorecard sorted by on_time_rate descending
        rates = [item["on_time_rate"] for item in scorecard]
        self.assertEqual(rates, sorted(rates, reverse=True))

    def test_upcoming_dues(self):
        # Add an overdue unpaid client payment
        cp_overdue = ClientPayment.objects.create(
            wedding=self.wedding,
            kind="final",
            amount=Decimal("50000"),
            due_date=date.today() - timedelta(days=3),
            paid_on=None,
        )
        # Add a distant unpaid client payment (> 30 days)
        cp_distant = ClientPayment.objects.create(
            wedding=self.wedding,
            kind="extra",
            amount=Decimal("30000"),
            due_date=date.today() + timedelta(days=45),
            paid_on=None,
        )

        dues = services.upcoming_dues(days=30)
        collect_payments = [item["payment"] for item in dues["to_collect"]]

        # 1. Paid payments are excluded
        paid_client_payments = ClientPayment.objects.filter(wedding=self.wedding, paid_on__isnull=False)
        for cp in paid_client_payments:
            self.assertNotIn(cp, collect_payments)

        # 2. Overdue payments are included and have overdue=True
        self.assertIn(cp_overdue, collect_payments)
        overdue_item = next(item for item in dues["to_collect"] if item["payment"] == cp_overdue)
        self.assertTrue(overdue_item["overdue"])
        self.assertLess(overdue_item["days"], 0)

        # 3. Distant payments (> 30 days) are excluded
        self.assertNotIn(cp_distant, collect_payments)

        # 4. For vendor payments, paid payments are excluded
        pay_payments = [item["payment"] for item in dues["to_pay"]]
        paid_vendor_payments = VendorPayment.objects.filter(wedding_vendor=self.wv, paid_on__isnull=False)
        for vp in paid_vendor_payments:
            self.assertNotIn(vp, pay_payments)

    def test_share_token(self):
        # 1. Valid token works
        token = services.share_token_for_season()
        data = services.verify_share_token(token)
        self.assertEqual(data["scope"], "season")

        # 2. Tampered token raises ServiceError
        tampered_token = token[:-4] + ("XXXX" if token[-4:] != "XXXX" else "YYYY")
        with self.assertRaises(services.ServiceError):
            services.verify_share_token(tampered_token)

        # 3. Completely invalid token raises ServiceError
        with self.assertRaises(services.ServiceError):
            services.verify_share_token("invalid-token")

    def test_season_views(self):
        c = Client()
        # 1. Anonymous -> 403 on season
        resp = c.get(reverse("season"))
        self.assertEqual(resp.status_code, 403)

        # 2. Regular user (not founder) -> 403
        c.force_login(self.regular_user)
        resp = c.get(reverse("season"))
        self.assertEqual(resp.status_code, 403)

        # 3. Founder user -> 200 (mocking render)
        c.force_login(self.founder_user)
        with patch("core.views.render") as mock_render:
            mock_render.return_value = HttpResponse("ok")
            resp = c.get(reverse("season"))
            self.assertEqual(resp.status_code, 200)
            mock_render.assert_called_once()
            args, kwargs = mock_render.call_args
            self.assertEqual(args[1], "core/season.html")
            context = args[2]
            self.assertIn("weddings", context)
            self.assertIn("totals", context)
            self.assertIn("profit_data", context)
            self.assertIn("vendors", context)
            self.assertIn("dues", context)
            self.assertIn("share_url", context)

        # 4. season_csv -> returns text/csv
        resp = c.get(reverse("season_csv"))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp["Content-Type"], "text/csv")
        content = resp.content.decode()
        self.assertIn("wedding,date,revenue,vendor_cost,labour_cost,profit,margin", content)

        # 5. season_share -> no login required
        c.logout()
        token = services.share_token_for_season()
        with patch("core.views.render") as mock_render:
            mock_render.return_value = HttpResponse("shared_ok")
            resp = c.get(reverse("season_share", kwargs={"token": token}))
            self.assertEqual(resp.status_code, 200)
            args, kwargs = mock_render.call_args
            context = args[2]
            self.assertNotIn("share_url", context)

        # season_share with invalid token -> 403
        resp = c.get(reverse("season_share", kwargs={"token": "bad-token"}))
        self.assertEqual(resp.status_code, 403)

        # 6. wedding_profit -> login required
        profit_url = reverse("wedding_profit", kwargs={"wedding_id": self.wedding.id})
        resp = c.get(profit_url)
        self.assertEqual(resp.status_code, 302)

        c.force_login(self.regular_user)
        with patch("core.views.render") as mock_render:
            mock_render.return_value = HttpResponse("profit_ok")
            resp = c.get(profit_url)
            self.assertEqual(resp.status_code, 200)
            args, kwargs = mock_render.call_args
            self.assertEqual(args[1], "core/wedding_profit.html")
            context = args[2]
            self.assertEqual(context["wedding"], self.wedding)
            self.assertIn("profit", context)


class Scene1DigitalAgreementTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="leadplanner", password="password123")
        self.lead = Lead.objects.create(
            couple_name="Rohan & Priya",
            phone="9876543210",
            email="rohan@example.com",
            tentative_date=date.today() + timedelta(days=90),
            guest_count=250,
            theme="Royal Palace",
            max_budget=Decimal("1500000"),
            package="royal",
            planner=self.user,
        )
        self.wedding = Wedding.objects.create(
            lead=self.lead,
            couple_name=self.lead.couple_name,
            package="royal",
            theme=self.lead.theme,
            start_date=self.lead.tentative_date,
            end_date=self.lead.tentative_date + timedelta(days=2),
            guest_count=self.lead.guest_count,
            budget=self.lead.max_budget,
            package_price=Decimal("450000"),
            planner=self.user,
        )

        img = Image.new("RGBA", (100, 40), (255, 255, 255, 0))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        self.valid_sig = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")

    def test_create_agreement(self):
        agmt = services.create_agreement(self.lead)
        self.assertIsNotNone(agmt.id)
        self.assertEqual(agmt.lead, self.lead)
        self.assertEqual(agmt.signer_name, self.lead.couple_name)
        self.assertFalse(agmt.is_signed)
        self.assertIsNone(agmt.signed_at)

        agmt2 = services.create_agreement(self.lead)
        self.assertEqual(agmt.id, agmt2.id)
        self.assertEqual(self.lead.agreements.count(), 1)

    def test_sign_agreement_validation(self):
        agmt = services.create_agreement(self.lead)

        with self.assertRaises(services.ServiceError):
            services.sign_agreement(agmt, "", self.valid_sig)

        with self.assertRaises(services.ServiceError):
            services.sign_agreement(agmt, "Rohan", "data:image/jpeg;base64,1234")
        with self.assertRaises(services.ServiceError):
            services.sign_agreement(agmt, "Rohan", "not-a-data-url")

        with self.assertRaises(services.ServiceError):
            services.sign_agreement(agmt, "Rohan", "data:image/png;base64,???invalid-b64???")

        # Reject non-PNG image data encoded in PNG data URL
        jpeg_img = Image.new("RGB", (50, 50), (255, 0, 0))
        jpeg_buf = io.BytesIO()
        jpeg_img.save(jpeg_buf, format="JPEG")
        jpeg_in_png = "data:image/png;base64," + base64.b64encode(jpeg_buf.getvalue()).decode("ascii")
        with self.assertRaises(services.ServiceError):
            services.sign_agreement(agmt, "Rohan", jpeg_in_png)

        fake_large_payload = "data:image/png;base64," + base64.b64encode(b"0" * (1024 * 1024 + 10)).decode("ascii")
        with self.assertRaises(services.ServiceError):
            services.sign_agreement(agmt, "Rohan", fake_large_payload)

        fake_corrupt = "data:image/png;base64," + base64.b64encode(b"this is not an image").decode("ascii")
        with self.assertRaises(services.ServiceError):
            services.sign_agreement(agmt, "Rohan", fake_corrupt)

    def test_sign_agreement_success_and_prevent_double_sign(self):
        agmt = services.create_agreement(self.lead)
        signed = services.sign_agreement(agmt, "Rohan", self.valid_sig)

        self.assertTrue(signed.is_signed)
        self.assertIsNotNone(signed.signed_at)
        self.assertEqual(signed.signer_name, "Rohan")
        self.assertTrue(bool(signed.signature_image))
        self.assertTrue(bool(signed.signed_pdf))

        # Produces a PDF that starts with b"%PDF"
        with signed.signed_pdf.open("rb") as f:
            pdf_bytes = f.read()
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))

        # Second signing raises ServiceError
        with self.assertRaises(services.ServiceError):
            services.sign_agreement(signed, "Rohan Again", self.valid_sig)

    def test_advance_lead_stage(self):
        lead = Lead.objects.create(
            couple_name="Vikram & Neha",
            phone="9123456780",
            email="vikram@example.com",
            tentative_date=date.today() + timedelta(days=120),
            guest_count=150,
            max_budget=Decimal("1000000"),
            package="royal",
            planner=self.user,
        )
        # Advance NEW -> MEETING -> AGREEMENT
        services.advance_lead_stage(lead, Lead.Stage.MEETING)
        services.advance_lead_stage(lead, Lead.Stage.AGREEMENT)
        self.assertEqual(lead.stage, Lead.Stage.AGREEMENT)

        # Confirming without a signed agreement fails (raises ServiceError)
        with self.assertRaises(services.ServiceError):
            services.advance_lead_stage(lead, Lead.Stage.CONFIRMED)
        self.assertEqual(lead.stage, Lead.Stage.AGREEMENT)

        # Create unsigned agreement -> still fails
        agmt = services.create_agreement(lead)
        with self.assertRaises(services.ServiceError):
            services.advance_lead_stage(lead, Lead.Stage.CONFIRMED)
        self.assertEqual(lead.stage, Lead.Stage.AGREEMENT)

        # Sign the agreement
        agmt = services.sign_agreement(agmt, "Vikram", self.valid_sig)
        self.assertTrue(agmt.is_signed)

        # Confirming with a signed agreement succeeds
        services.advance_lead_stage(lead, Lead.Stage.CONFIRMED)
        self.assertEqual(lead.stage, Lead.Stage.CONFIRMED)

    def test_build_agreement_pdf(self):
        agmt = services.create_agreement(self.lead)
        pdf_bytes = services.build_agreement_pdf(agmt)
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))

    def test_build_invoice_pdf(self):
        extra = services.add_extra_charge(
            wedding=self.wedding,
            wedding_vendor=None,
            description="Fireworks Display",
            quantity=1,
            client_unit_price=Decimal("25000"),
            vendor_unit_cost=Decimal("15000"),
        )
        services.approve_extra(extra)

        pdf_bytes = services.build_invoice_pdf(self.wedding)
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))

    def test_agreement_views(self):
        c = Client()
        resp = c.get(reverse("agreement", kwargs={"id": self.lead.id}))
        self.assertEqual(resp.status_code, 302)

        c.force_login(self.user)

        with patch("core.views.render") as mock_render:
            mock_render.return_value = HttpResponse("ok")
            resp = c.get(reverse("agreement", kwargs={"id": self.lead.id}))
            self.assertEqual(resp.status_code, 200)
            args, kwargs = mock_render.call_args
            self.assertEqual(args[1], "core/agreement.html")
            context = args[2]
            self.assertEqual(context["lead"], self.lead)
            self.assertIsNotNone(context["agreement"])

        agmt = self.lead.agreements.first()

        resp = c.get(reverse("agreement_pdf", kwargs={"id": agmt.id}))
        self.assertEqual(resp.status_code, 404)

        resp = c.post(
            reverse("agreement_sign", kwargs={"id": agmt.id}),
            data={"signer_name": "", "signature": "invalid"},
        )
        self.assertEqual(resp.status_code, 400)
        self.assertFalse(resp.json()["ok"])

        resp = c.post(
            reverse("agreement_sign", kwargs={"id": agmt.id}),
            data={"signer_name": "Rohan", "signature": self.valid_sig},
        )
        self.assertEqual(resp.status_code, 200)
        json_data = resp.json()
        self.assertTrue(json_data["ok"])
        self.assertIn("pdf_url", json_data)

        resp = c.get(reverse("agreement_pdf", kwargs={"id": agmt.id}))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp["Content-Type"], "application/pdf")
        self.assertTrue(resp.content.startswith(b"%PDF"))

        resp = c.get(reverse("invoice_pdf", kwargs={"id": self.wedding.id}))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp["Content-Type"], "application/pdf")
        self.assertTrue(resp.content.startswith(b"%PDF"))

        resp = c.get(reverse("agreement_whatsapp", kwargs={"id": self.lead.id}))
        self.assertEqual(resp.status_code, 302)
        redirect_url = resp.url
        self.assertTrue(redirect_url.startswith("https://wa.me/919876543210?text="))
        self.assertIn("/leads/" + str(self.lead.id) + "/agreement/", redirect_url)


