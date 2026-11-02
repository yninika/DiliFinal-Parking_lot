import unittest

# Removed external imports since these classes are already defined in the notebook session
# from slot import ParkingSlot
# from shared_contracts import IVehicle, ParkingLotError

# Mock vehicle for testing
class TestVehicle(IVehicle):

    def __init__(self, plate, vehicle_type):
        self._plate = plate
        self._vehicle_type = vehicle_type

    @property
    def vehicle_plate(self):
        return self._plate

    @property
    def vehicle_type(self):
        return self._vehicle_type


class TestParkingSlot(unittest.TestCase):

    def setUp(self):
        self.small_slot = ParkingSlot(1, "small", 1)
        self.regular_slot = ParkingSlot(2, "regular", 1)

        self.car = TestVehicle("ABC123", "car")
        self.motorcycle = TestVehicle("XYZ789", "motorcycle")

    # Test slot initialization
    def test_slot_initialization(self):
        self.assertEqual(self.small_slot.slot_number, 1)
        self.assertEqual(self.small_slot.slot_type, "small")
        self.assertEqual(self.small_slot.level, 1)
        self.assertTrue(self.small_slot.is_available)

    # Test invalid slot number
    def test_invalid_slot_number(self):
        with self.assertRaises(ValueError):
            ParkingSlot(0, "small", 1)

    # Test invalid slot type
    def test_invalid_slot_type(self):
        with self.assertRaises(ValueError):
            ParkingSlot(1, "large", 1)

    # Test invalid level
    def test_invalid_level(self):
        with self.assertRaises(ValueError):
            ParkingSlot(1, "small", 0)

    # Test motorcycle fits in small slot
    def test_motorcycle_fits_small_slot(self):
        self.assertTrue(
            self.small_slot.can_fit(self.motorcycle)
        )

    # Test car cannot fit in small slot
    def test_car_cannot_fit_small_slot(self):
        self.assertFalse(
            self.small_slot.can_fit(self.car)
        )

    # Test car fits in regular slot
    def test_car_fits_regular_slot(self):
        self.assertTrue(
            self.regular_slot.can_fit(self.car)
        )

    # Test motorcycle fits in regular slot
    def test_motorcycle_fits_regular_slot(self):
        self.assertTrue(
            self.regular_slot.can_fit(self.motorcycle)
        )

    # Test assigning a vehicle
    def test_assign_vehicle(self):
        self.small_slot.assign_vehicle(self.motorcycle)

        self.assertFalse(self.small_slot.is_available)
        self.assertEqual(
            self.small_slot.assigned_vehicle,
            self.motorcycle
        )

    # Test assigning vehicle to occupied slot
    def test_assign_to_occupied_slot(self):
        self.small_slot.assign_vehicle(self.motorcycle)

        with self.assertRaises(ParkingLotError):
            self.small_slot.assign_vehicle(self.motorcycle)

    # Test assigning incompatible vehicle
    def test_assign_incompatible_vehicle(self):
        with self.assertRaises(ParkingLotError):
            self.small_slot.assign_vehicle(self.car)

        self.assertTrue(self.small_slot.is_available)

    # Test removing vehicle
    def test_remove_vehicle(self):
        self.small_slot.assign_vehicle(self.motorcycle)

        removed_vehicle = self.small_slot.remove_vehicle()

        self.assertEqual(removed_vehicle, self.motorcycle)
        self.assertTrue(self.small_slot.is_available)
        self.assertIsNone(self.small_slot.assigned_vehicle)

    # Test removing vehicle from empty slot
    def test_remove_from_empty_slot(self):
        with self.assertRaises(ParkingLotError):
            self.small_slot.remove_vehicle()

    # Test unknown vehicle type
    def test_unknown_vehicle_type(self):
        unknown_vehicle = TestVehicle("UNK123", "truck")

        self.assertFalse(
            self.small_slot.can_fit(unknown_vehicle)
        )


if __name__ == "__main__":
    # Added argv and exit arguments to support running unittest inside Colab notebooks
    unittest.main(argv=['first-arg-is-ignored'], exit=False)

