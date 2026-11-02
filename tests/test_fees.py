# Author: Ana Lynica B. Ferolino (module: fees)
"""Tests for the fees module, using fakes instead of teammates' classes."""

import unittest
from datetime import datetime, timedelta

from contracts import IVehicle, ITicket, ParkingLotError
from fees import StandardFees


class FakeVehicle(IVehicle):
    """Minimal IVehicle for testing."""
    def __init__(self, vehicle_type="car", plate="ABC123"):
        self._type = vehicle_type
        self._plate = plate

    @property
    def vehicle_plate(self):
        return self._plate

    @property
    def vehicle_type(self):
        return self._type


class FakeTicket(ITicket):
    """Minimal ITicket for testing; stays open if minutes is None."""
    def __init__(self, vehicle_type="car", minutes=60):
        self._vehicle = FakeVehicle(vehicle_type)
        self._entry = datetime(2026, 11, 2, 8, 0)
        self._exit = (None if minutes is None
                      else self._entry + timedelta(minutes=minutes))

    @property
    def ticket_number(self):
        return 1

    @property
    def vehicle(self):
        return self._vehicle

    @property
    def slot(self):
        return None

    @property
    def entry_time(self):
        return self._entry

    @property
    def exit_time(self):
        return self._exit

    def close(self, exit_time):
        self._exit = exit_time


class TestStandardFees(unittest.TestCase):
    def setUp(self):
        self.fees = StandardFees(car_hourly_rate=50, motorcycle_hourly_rate=20,
                                 grace_minutes=15)

    def test_exact_hour_car(self):
        self.assertEqual(self.fees.compute_fee(FakeTicket("car", 60)), 50.0)

    def test_partial_hour_rounds_up(self):
        self.assertEqual(self.fees.compute_fee(FakeTicket("car", 61)), 100.0)

    def test_motorcycle_uses_its_own_rate(self):
        self.assertEqual(
            self.fees.compute_fee(FakeTicket("motorcycle", 120)), 40.0)

    def test_within_grace_is_free(self):
        self.assertEqual(self.fees.compute_fee(FakeTicket("car", 15)), 0.0)

    def test_just_past_grace_charges_minimum_one_hour(self):
        self.assertEqual(self.fees.compute_fee(FakeTicket("car", 16)), 50.0)

    def test_result_rounded_to_two_decimals(self):
        fees = StandardFees(car_hourly_rate=33.333, grace_minutes=0)
        self.assertEqual(fees.compute_fee(FakeTicket("car", 180)), 100.0)

    def test_open_ticket_raises_parking_lot_error(self):
        with self.assertRaises(ParkingLotError):
            self.fees.compute_fee(FakeTicket("car", None))

    def test_unknown_vehicle_type_raises_parking_lot_error(self):
        with self.assertRaises(ParkingLotError):
            self.fees.compute_fee(FakeTicket("truck", 60))

    def test_non_ticket_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.fees.compute_fee("not a ticket")

    def test_negative_rate_rejected(self):
        with self.assertRaises(ValueError):
            StandardFees(car_hourly_rate=-1)

    def test_bad_types_rejected(self):
        for bad in ("50", None, True):
            with self.assertRaises(ValueError):
                StandardFees(motorcycle_hourly_rate=bad)
        with self.assertRaises(ValueError):
            StandardFees(grace_minutes=1.5)

    def test_properties_are_read_only(self):
        with self.assertRaises(AttributeError):
            self.fees.car_hourly_rate = 999
        with self.assertRaises(AttributeError):
            self.fees.grace_minutes = 999
        self.assertEqual(self.fees.car_hourly_rate, 50.0)

    def test_equality_and_hash(self):
        a, b = StandardFees(50, 20, 15), StandardFees(50, 20, 15)
        self.assertEqual(a, b)
        self.assertEqual(hash(a), hash(b))
        self.assertNotEqual(a, StandardFees(60, 20, 15))

    def test_str(self):
        self.assertIn("grace=15", str(self.fees))


if __name__ == "__main__":
    unittest.main()
