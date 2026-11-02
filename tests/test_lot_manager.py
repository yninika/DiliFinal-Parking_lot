"""Unit tests for the lot manager module."""

import unittest
from datetime import datetime, timedelta

from contracts import IVehicle, ISlot, ITicket, IFees, ParkingLotError
from lot_manager import LotManager

# ------------------------------------------------
# FAKE CONTRACT IMPLEMENTATIONS
# ------------------------------------------------

class FakeVehicle(IVehicle):
    """A simple fake vehicle for testing."""

    def __init__(self, plate, vehicle_type="car"):
        self._plate = plate
        self._vehicle_type = vehicle_type

    @property
    def vehicle_plate(self):
        """Return the fake vehicle's plate."""
        return self._plate

    @property
    def vehicle_type(self):
        """Return the fake vehicle's type."""
        return self._vehicle_type


class FakeSlot(ISlot):
    """A simple fake parking slot for testing."""

    def __init__(self, number, slot_type="regular", level=1):
        self._number = number
        self._slot_type = slot_type
        self._level = level
        self._vehicle = None

    @property
    def slot_number(self):
        """Return the slot number."""
        return self._number

    @property
    def slot_type(self):
        """Return the slot type."""
        return self._slot_type

    @property
    def level(self):
        """Return the slot level."""
        return self._level

    @property
    def is_available(self):
        """Return whether the slot is empty."""
        return self._vehicle is None

    @property
    def assigned_vehicle(self):
        """Return the vehicle assigned to this slot."""
        return self._vehicle

    def can_fit(self, vehicle):
        """Check whether this slot can fit the vehicle."""
        if self._slot_type == "regular":
            return vehicle.vehicle_type in ("car", "motorcycle")

        return vehicle.vehicle_type == "motorcycle"

    def assign_vehicle(self, vehicle):
        """Assign a vehicle to this slot."""
        if not self.is_available:
            raise ParkingLotError("Slot is already occupied.")

        if not self.can_fit(vehicle):
            raise ParkingLotError("Vehicle does not fit.")

        self._vehicle = vehicle

    def remove_vehicle(self):
        """Remove and return the assigned vehicle."""
        if self.is_available:
            raise ParkingLotError("Slot is already empty.")

        vehicle = self._vehicle
        self._vehicle = None
        return vehicle

class FakeTicket(ITicket):
    """A simple fake parking ticket for testing."""

    def __init__(self, number, vehicle, slot, entry_time):
        self._number = number
        self._vehicle = vehicle
        self._slot = slot
        self._entry_time = entry_time
        self._exit_time = None

    @property
    def ticket_number(self):
        """Return the ticket number."""
        return self._number

    @property
    def vehicle(self):
        """Return the ticket's vehicle."""
        return self._vehicle

    @property
    def slot(self):
        """Return the ticket's parking slot."""
        return self._slot

    @property
    def entry_time(self):
        """Return the entry time."""
        return self._entry_time

    @property
    def exit_time(self):
        """Return the exit time."""
        return self._exit_time

    def close(self, exit_time):
        """Close the ticket using the supplied exit time."""
        if self._exit_time is not None:
            raise ParkingLotError("Ticket is already closed.")

        if exit_time < self._entry_time:
            raise ValueError("Exit time cannot be before entry time.")

        self._exit_time = exit_time

class FakeFees(IFees):
    """A simple fake fee calculator for testing."""

    @property
    def car_hourly_rate(self):
        """Return the fake car rate."""
        return 30.0

    @property
    def motorcycle_hourly_rate(self):
        """Return the fake motorcycle rate."""
        return 15.0

    def compute_fee(self, ticket):
        """Return a fixed fee for a closed ticket."""
        if ticket.exit_time is None:
            raise ParkingLotError("Cannot calculate an open ticket.")

        return 42.0

# ------------------------------------------------
# LOT MANAGER TESTS
# ------------------------------------------------

class TestLotManager(unittest.TestCase):
    """Test the parking lot manager."""

    def setUp(self):
        """Create a manager with fake dependencies before each test."""
        self.slot = FakeSlot(1)
        self.fees = FakeFees()

        self.manager = LotManager(
            slots=[self.slot],
            fee_calculator=self.fees,
            ticket_factory=FakeTicket,
        )

    def test_park_vehicle_creates_ticket(self):
        """Parking a vehicle should assign a slot and create a ticket."""
        vehicle = FakeVehicle("ABC-123")

        ticket = self.manager.park_vehicle(vehicle)

        self.assertEqual(ticket.ticket_number, 1)
        self.assertIs(ticket.vehicle, vehicle)
        self.assertIs(ticket.slot, self.slot)
        self.assertIs(self.slot.assigned_vehicle, vehicle)
        self.assertEqual(self.manager.active_ticket_count, 1)

    def test_duplicate_vehicle_cannot_be_parked(self):
        """A vehicle that is already parked cannot be parked again."""
        vehicle = FakeVehicle("ABC-123")

        self.manager.park_vehicle(vehicle)

        with self.assertRaises(ParkingLotError):
            self.manager.park_vehicle(vehicle)

    def test_no_suitable_slot_raises_error(self):
        """Parking should fail when no suitable slot is available."""
        vehicle = FakeVehicle("XYZ-789", "truck")

        with self.assertRaises(ParkingLotError):
            self.manager.park_vehicle(vehicle)

    def test_release_vehicle_calculates_fee(self):
        """Releasing a vehicle should close its ticket and return its fee."""
        vehicle = FakeVehicle("ABC-123")
        ticket = self.manager.park_vehicle(vehicle)

        exit_time = datetime.now() + timedelta(hours=2)

        fee = self.manager.release_vehicle(
            ticket.ticket_number,
            exit_time,
        )

        self.assertEqual(fee, 42.0)
        self.assertEqual(ticket.exit_time, exit_time)
        self.assertTrue(self.slot.is_available)
        self.assertEqual(self.manager.active_ticket_count, 0)

    def test_unknown_ticket_cannot_be_released(self):
        """An unknown ticket number should raise ParkingLotError."""
        with self.assertRaises(ParkingLotError):
            self.manager.release_vehicle(999, datetime.now())

    def test_exit_time_before_entry_is_rejected(self):
        """A ticket cannot be closed before its entry time."""
        vehicle = FakeVehicle("ABC-123")
        ticket = self.manager.park_vehicle(vehicle)

        invalid_exit_time = ticket.entry_time - timedelta(minutes=1)

        with self.assertRaises(ValueError):
            self.manager.release_vehicle(
                ticket.ticket_number,
                invalid_exit_time,
            )

        self.assertEqual(self.manager.active_ticket_count, 1)
        self.assertFalse(self.slot.is_available)

    def test_slots_property_returns_tuple(self):
        """The slots property should return an immutable tuple."""
        self.assertIsInstance(self.manager.slots, tuple)

    def test_len_returns_active_ticket_count(self):
        """The __len__ method should return the active ticket count."""
        self.assertEqual(len(self.manager), 0)

        self.manager.park_vehicle(FakeVehicle("ABC-123"))

        self.assertEqual(len(self.manager), 1)

if __name__ == "__main__":
    unittest.main()
