# Author: Felicity Jen S Aranjuez (tests for vehicle module)

"""Unit tests for the vehicle module."""

import unittest

from vehicle import Car, Motorcycle, VehicleRegistry
from contracts import ParkingLotError


class TestVehicle(unittest.TestCase):
    """Test the vehicle classes and vehicle registry."""

    def setUp(self):
        """Create a fresh registry before each test."""
        self.registry = VehicleRegistry()

    def test_car_properties(self):
        """A car should have the correct type and plate number."""
        car = Car("abc-123")

        self.assertEqual(car.vehicle_plate, "ABC-123")
        self.assertEqual(car.vehicle_type, "car")

    def test_motorcycle_properties(self):
        """A motorcycle should have the correct type and plate number."""
        motorcycle = Motorcycle("xyz-789")

        self.assertEqual(motorcycle.vehicle_plate, "XYZ-789")
        self.assertEqual(motorcycle.vehicle_type, "motorcycle")

    def test_empty_plate_is_rejected(self):
        """A vehicle should not accept an empty plate number."""
        with self.assertRaises(ValueError):
            Car("   ")

    def test_non_string_plate_is_rejected(self):
        """A vehicle should reject a plate number that is not a string."""
        with self.assertRaises(ValueError):
            Car(12345)

    def test_register_vehicle(self):
        """A valid vehicle should be added to the registry."""
        car = Car("ABC-123")

        self.registry.register(car)

        self.assertEqual(self.registry.vehicle_count, 1)
        self.assertIs(self.registry.find("ABC-123"), car)

    def test_duplicate_plate_is_rejected(self):
        """Two registered vehicles cannot have the same plate number."""
        first_car = Car("ABC-123")
        second_car = Car("ABC-123")

        self.registry.register(first_car)

        with self.assertRaises(ParkingLotError):
            self.registry.register(second_car)

    def test_unregister_vehicle(self):
        """A registered vehicle should be removable from the registry."""
        car = Car("ABC-123")
        self.registry.register(car)

        removed_vehicle = self.registry.unregister("ABC-123")

        self.assertIs(removed_vehicle, car)
        self.assertEqual(self.registry.vehicle_count, 0)

    def test_unregister_unknown_vehicle(self):
        """An unknown vehicle cannot be removed."""
        with self.assertRaises(ParkingLotError):
            self.registry.unregister("UNKNOWN-123")

    def test_vehicle_collection_is_immutable(self):
        """The returned vehicle collection should be a tuple."""
        self.registry.register(Car("ABC-123"))

        vehicles = self.registry.vehicles

        self.assertIsInstance(vehicles, tuple)

        with self.assertRaises(AttributeError):
            vehicles.append(Car("XYZ-789"))

    def test_car_and_motorcycle_are_both_vehicles(self):
        """Different vehicle types should work through the same contract."""
        vehicles = [
            Car("ABC-123"),
            Motorcycle("XYZ-789")
        ]

        for vehicle in vehicles:
            self.registry.register(vehicle)

        self.assertEqual(self.registry.vehicle_count, 2)


if __name__ == "__main__":
    unittest.main()
