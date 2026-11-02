# Author: Gian Sicat (module: ticket)


"""
Ticket module for the parking lot system.

Handles ticket creation, entry times, and exit times.
"""

from datetime import datetime
from contracts import ITicket, IVehicle, ISlot, ParkingLotError


class Ticket(ITicket):
    """Represents a parking ticket for a vehicle occupying a slot."""

    def __init__(self, ticket_number: int, vehicle: IVehicle, slot: ISlot, entry_time: datetime = None):
        if not isinstance(ticket_number, int) or ticket_number <= 0:
            raise ValueError("Ticket number must be a positive integer.")
        if not isinstance(vehicle, IVehicle):
            raise ValueError("Vehicle must implement IVehicle contract.")
        if not isinstance(slot, ISlot):
            raise ValueError("Slot must implement ISlot contract.")
        if slot.assigned_vehicle != vehicle:
            raise ParkingLotError("Cannot issue ticket: slot is not assigned to this vehicle.")

        self._ticket_number = ticket_number
        self._vehicle = vehicle
        self._slot = slot

        if entry_time is None:
            self._entry_time = datetime.now()
        else:
            if not isinstance(entry_time, datetime):
                raise ValueError("Entry time must be a datetime object.")
            self._entry_time = entry_time

        self._exit_time = None

    @property
    def ticket_number(self) -> int:
        return self._ticket_number

    @property
    def vehicle(self) -> IVehicle:
        return self._vehicle

    @property
    def slot(self) -> ISlot:
        return self._slot

    @property
    def entry_time(self) -> datetime:
        return self._entry_time

    @property
    def exit_time(self) -> datetime | None:
        return self._exit_time

    def close(self, exit_time: datetime) -> None:
        """Closes the parking ticket by recording the exit time."""
        if self._exit_time is not None:
            raise ParkingLotError("This ticket is already closed.")
        if not isinstance(exit_time, datetime):
            raise ValueError("Exit time must be a datetime object.")
        if exit_time < self._entry_time:
            raise ValueError("Exit time cannot be earlier than the entry time.")

        self._exit_time = exit_time

    def __str__(self) -> str:
        status = "Closed" if self._exit_time else "Open"
        return f"Ticket #{self._ticket_number} for {self._vehicle.vehicle_plate} ({status})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, ITicket):
            return False
        return self._ticket_number == other.ticket_number

