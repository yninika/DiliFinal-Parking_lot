# Author: Felicity Jen S Aranjuez (module: vehicle)

"""
Vehicle module for the Parking Lot Management System.

This module defines vehicles and manages vehicle registration.
It follows the IVehicle contract from contracts.py.
"""

from abc import ABC, abstractmethod
from contracts import IVehicle, ParkingLotError

# ========================
# BASE VEHICLE CLASS
# ========================

class Vehicle(IVehicle, ABC):
    """
    Base class for all vehicles using the parking lot.

    Stores and validates a vehicle's plate number.
    Specific vehicle types must implement the vehicle_type property.
    """

    def __init__(self, vehicle_plate: str):
        """
        Initialize a vehicle with a plate number.
        The plate number must be a non-empty string.

        Args:
            vehicle_plate: The vehicle's plate number.

        Raises:
            ValueError: If the plate number is not a string
                        or contains only whitespace.
        """
        if not isinstance(vehicle_plate, str):
            raise ValueError("Vehicle plate must be a string.")

        vehicle_plate = vehicle_plate.strip().upper()

        if not vehicle_plate:
            raise ValueError("Vehicle plate cannot be empty.")

        self._vehicle_plate = vehicle_plate

    @property
    def vehicle_plate(self) -> str:
        """Return the vehicle's plate number."""
        return self._vehicle_plate

    @property
    @abstractmethod
    def vehicle_type(self) -> str:
        """Return the specific type of vehicle."""
        pass

    def __str__(self) -> str:
        """Return a readable description of the vehicle."""
        return f"{self.vehicle_type}: {self.vehicle_plate}"

    def __eq__(self, other) -> bool:
        """
        Check whether two vehicles have the same type and plate number.

        Args:
            other: Another object to compare with.

        Returns:
            True if both vehicles have the same type and plate.
        """
        if not isinstance(other, IVehicle):
            return NotImplemented

        return (
            self.vehicle_plate == other.vehicle_plate
            and self.vehicle_type == other.vehicle_type
        )

    def __hash__(self) -> int:
        """Return a hash based on the vehicle type and plate number."""
        return hash((self.vehicle_type, self.vehicle_plate))

# ================
# CAR CLASS
# ================

class Car(Vehicle):
    """Represent a car using the parking lot."""

    @property
    def vehicle_type(self) -> str:
        """Return 'car' as the vehicle type."""
        return "car"

# ====================
# MOTORCYCLE CLASS
# ====================

class Motorcycle(Vehicle):
    """Represent a motorcycle using the parking lot."""

    @property
    def vehicle_type(self) -> str:
        """Return 'motorcycle' as the vehicle type."""
        return "motorcycle"

# =====================
# VEHICLE REGISTRY
# =====================

class VehicleRegistry:
    """
    Manage the registration of vehicles in the parking lot.

    The registry keeps track of registered vehicles and prevents
    duplicate plate numbers.
    """

    def __init__(self):
        """Create an empty vehicle registry."""
        self._vehicles = {}

    @property
    def vehicles(self) -> tuple[IVehicle, ...]:
        """
        Return all registered vehicles as an immutable tuple.

        A tuple prevents callers from directly changing the
        registry's internal collection.
        """
        return tuple(self._vehicles.values())

    @property
    def vehicle_count(self) -> int:
        """Return the total number of registered vehicles."""
        return len(self._vehicles)

    def register(self, vehicle: IVehicle) -> None:
        """
        Register a vehicle in the registry.

        Args:
            vehicle: An object that follows the IVehicle contract.

        Raises:
            TypeError: If the supplied object does not implement IVehicle.
            ParkingLotError: If a vehicle with the same plate is
                             already registered.
        """
        if not isinstance(vehicle, IVehicle):
            raise TypeError("Vehicle must implement the IVehicle contract.")

        plate = vehicle.vehicle_plate

        if plate in self._vehicles:
            raise ParkingLotError(
                f"A vehicle with plate {plate} is already registered."
            )

        self._vehicles[plate] = vehicle

    def unregister(self, vehicle_plate: str) -> IVehicle:
        """
        Remove and return a registered vehicle using its plate number.

        Args:
            vehicle_plate: The plate number of the vehicle to remove.

        Returns:
            The vehicle that was removed.

        Raises:
            ValueError: If the plate number is not a valid string.
            ParkingLotError: If the plate number is not registered.
        """
        if not isinstance(vehicle_plate, str) or not vehicle_plate.strip():
            raise ValueError("A valid vehicle plate must be provided.")

        plate = vehicle_plate.strip().upper()

        if plate not in self._vehicles:
            raise ParkingLotError(
                f"No registered vehicle found with plate {plate}."
            )

        return self._vehicles.pop(plate)

    def find(self, vehicle_plate: str) -> IVehicle | None:
        """
        Find a registered vehicle using its plate number.

        Args:
            vehicle_plate: The plate number to search for.

        Returns:
            The matching vehicle, or None if it is not registered.

        Raises:
            ValueError: If the plate number is not a valid string.
        """
        if not isinstance(vehicle_plate, str) or not vehicle_plate.strip():
            raise ValueError("A valid vehicle plate must be provided.")

        plate = vehicle_plate.strip().upper()
        return self._vehicles.get(plate)

    def __len__(self) -> int:
        """Return the number of vehicles in the registry."""
        return self.vehicle_count

    def __contains__(self, vehicle_plate: str) -> bool:
        """Check whether a plate number exists in the registry."""
        if not isinstance(vehicle_plate, str):
            return False

        return vehicle_plate.strip().upper() in self._vehicles
