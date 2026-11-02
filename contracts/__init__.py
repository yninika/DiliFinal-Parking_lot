"""Shared contracts for the Parking Lot Management System.

This module defines the abstract base classes (ABCs) that establish
how the five project modules communicate with one another.

Modules should depend on these contracts instead of importing
concrete classes from other team members' modules.
"""

from abc import ABC, abstractmethod
from datetime import datetime

#==============
# SHARED CUSTOM EXCEPTION
#===============

class ParkingLotError(Exception):
    """
    Exception raised when a parking lot business rule is violated.

    Examples include attempting to park in an occupied slot,
    attempting to remove a vehicle from an empty slot, or trying
    to calculate a fee for a ticket that is still open.
    """
    pass

#==============
# VEHICLE MODULE
#===============

class IVehicle(ABC):
    """
    Contract for vehicles that use the parking lot.

    Concrete vehicle classes must provide their plate number
    and vehicle type.
    """

    @property
    @abstractmethod
    def vehicle_plate(self) -> str:
        """Return the unique plate number of the vehicle."""
        pass

    @property
    @abstractmethod
    def vehicle_type(self) -> str:
        """
        Return the type of vehicle.

        Expected values are 'car' or 'motorcycle'.
        """
        pass

#==============
# SLOT MODULE
#===============

class ISlot(ABC):
    """
    Contract for parking slots in the parking lot.

    Concrete slot classes must provide information about the slot,
    determine whether a vehicle fits, and support vehicle assignment
    and removal.
    """

    @property
    @abstractmethod
    def slot_number(self) -> int:
        """Return the unique positive number of the slot."""
        pass

    @property
    @abstractmethod
    def slot_type(self) -> str:
        """
        Return the size or type of the parking slot.

        Examples include 'small' and 'regular'.
        """
        pass

    @property
    @abstractmethod
    def level(self) -> int:
        """Return the floor or level where the parking slot is located."""
        pass

    @property
    @abstractmethod
    def is_available(self) -> bool:
        """Return True if the slot is empty and available for parking."""
        pass

    @abstractmethod
    def can_fit(self, vehicle: IVehicle) -> bool:
        """
        Check whether the given vehicle can fit in this parking slot.

        Return True if the vehicle fits; otherwise, return False.
        """
        pass

    @property
    @abstractmethod
    def assigned_vehicle(self) -> IVehicle | None:
        """
        Return the vehicle currently occupying the slot.

        Return None if no vehicle is assigned to the slot.
        """
        pass

    @abstractmethod
    def assign_vehicle(self, vehicle: IVehicle) -> None:
        """
        Assign a vehicle to this parking slot.

        Raise ParkingLotError if the slot is already occupied
        or if the vehicle does not fit.
        """
        pass

    @abstractmethod
    def remove_vehicle(self) -> IVehicle:
        """
        Remove and return the vehicle occupying this slot.

        Raise ParkingLotError if the slot is already empty.
        """
        pass

#==============
# TICKET MODULE
#===============

class ITicket(ABC):
    """
    Contract for parking tickets.

    A ticket stores information about a vehicle's parking session,
    including its assigned slot, entry time, and exit time.
    """

    @property
    @abstractmethod
    def ticket_number(self) -> int:
        """Return the unique positive number assigned to the ticket."""
        pass

    @property
    @abstractmethod
    def vehicle(self) -> IVehicle:
        """Return the vehicle associated with this parking ticket."""
        pass

    @property
    @abstractmethod
    def slot(self) -> ISlot:
        """Return the parking slot assigned to this ticket."""
        pass

    @property
    @abstractmethod
    def entry_time(self) -> datetime:
        """Return the date and time when the vehicle entered the parking lot."""
        pass

    @property
    @abstractmethod
    def exit_time(self) -> datetime | None:
        """
        Return the date and time when the vehicle exited.

        Return None if the parking ticket is still open.
        """
        pass

    @abstractmethod
    def close(self, exit_time: datetime) -> None:
        """
        Record the vehicle's exit time and close the ticket.

        Raise ParkingLotError if the ticket is already closed.
        Raise ValueError if the exit time is earlier than the entry time.
        """
        pass

#==============
# FEES MODULE
#===============

class IFees(ABC):
    """
    Contract for calculating parking fees.

    Concrete fee classes must provide hourly rates for cars
    and motorcycles and calculate the fee for a completed ticket.
    """

    @property
    @abstractmethod
    def car_hourly_rate(self) -> float:
        """Return the hourly parking rate for cars in pesos."""
        pass

    @property
    @abstractmethod
    def motorcycle_hourly_rate(self) -> float:
        """Return the hourly parking rate for motorcycles in pesos."""
        pass

    @abstractmethod
    def compute_fee(self, ticket: ITicket) -> float:
        """
        Calculate the parking fee for a completed parking ticket.

        Use the vehicle type and parking duration to determine
        the amount charged.

        Return the fee rounded to two decimal places.

        Raise ParkingLotError if the ticket is still open.
        """
        pass

#==============
# LOT MANAGER MODULE
#===============

class ILotManager(ABC):
    """
    Contract for managing the parking lot.

    Concrete lot manager classes must support parking vehicles,
    releasing vehicles, and providing information about the slots
    and active parking tickets.
    """

    @abstractmethod
    def park_vehicle(self, vehicle: IVehicle) -> ITicket:
        """
        Park a vehicle in a suitable available slot.

        Assign the vehicle to the slot, create a parking ticket,
        and return the newly created ticket.

        Raise ParkingLotError if no suitable slot is available.
        """
        pass

    @abstractmethod
    def release_vehicle(self, ticket_number: int,
                        exit_time: datetime) -> float:
        """
        Release a vehicle from its assigned parking slot.

        Close the corresponding ticket, release the slot,
        calculate the parking fee, and return the fee in pesos.

        Raise ParkingLotError if the ticket number cannot be found
        or the ticket cannot be released.
        """
        pass

    @property
    @abstractmethod
    def slots(self) -> tuple[ISlot, ...]:
        """
        Return all parking slots managed by the lot manager.

        Return the slots as an immutable tuple so callers cannot
        directly modify the manager's slot collection.
        """
        pass

    @property
    @abstractmethod
    def active_ticket_count(self) -> int:
        """Return the number of currently active parking tickets that are still open."""
        pass
