# Author: James Ryan Cagas (module: ticket)
"""

from shared_contracts import ISlot, IVehicle, ParkingLotError


class ParkingSlot(ISlot):
    """
    Concrete implementation of a parking slot.

    Handles vehicle assignment, removal, and compatibility checking.
    """

    def __init__(self, slot_number: int, slot_type: str, level: int):
        if slot_number <= 0:
            raise ValueError("Slot number must be positive.")

        if slot_type not in ("small", "regular"):
            raise ValueError("Slot type must be 'small' or 'regular'.")

        if level <= 0:
            raise ValueError("Level must be positive.")

        self._slot_number = slot_number
        self._slot_type = slot_type
        self._level = level
        self._assigned_vehicle = None

    @property
    def slot_number(self) -> int:
        return self._slot_number

    @property
    def slot_type(self) -> str:
        return self._slot_type

    @property
    def level(self) -> int:
        return self._level

    @property
    def is_available(self) -> bool:
        return self._assigned_vehicle is None

    @property
    def assigned_vehicle(self) -> IVehicle | None:
        return self._assigned_vehicle

    def can_fit(self, vehicle: IVehicle) -> bool:
        """
        Check whether a vehicle can fit in this slot.

        Small slots: motorcycles only.
        Regular slots: cars and motorcycles.
        """

        if vehicle is None:
            return False

        if vehicle.vehicle_type == "motorcycle":
            return True

        if vehicle.vehicle_type == "car":
            return self._slot_type == "regular"

        return False

    def assign_vehicle(self, vehicle: IVehicle) -> None:
        """Assign a vehicle to the parking slot."""

        if not self.is_available:
            raise ParkingLotError(
                f"Slot {self._slot_number} is already occupied."
            )

        if not self.can_fit(vehicle):
            raise ParkingLotError(
                f"Vehicle cannot fit in slot {self._slot_number}."
            )

        self._assigned_vehicle = vehicle

    def remove_vehicle(self) -> IVehicle:
        """Remove and return the assigned vehicle."""

        if self.is_available:
            raise ParkingLotError(
                f"Slot {self._slot_number} is already empty."
            )

        vehicle = self._assigned_vehicle
        self._assigned_vehicle = None

        return vehicle

