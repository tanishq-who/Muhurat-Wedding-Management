# title, category, days relative to the first wedding day
from core.management.commands.seed_data import TASKS
TASK_TEMPLATE = [
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
