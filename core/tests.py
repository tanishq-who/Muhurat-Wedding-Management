from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from core import services
from core.forms import ExtraChargeForm
from core.models import (
    ClientPayment,
    ExtraCharge,
    Quote,
    Task,
    Vendor,
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
