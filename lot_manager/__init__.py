# Author: Cassandra Nicole Mier (module: lot_manager)

"""
Lot manager module for the Parking Lot Management System.

This module assigns vehicles to suitable parking slots, creates
parking tickets, tracks active parking sessions, and releases
vehicles when they exit.
"""

from datetime import datetime
from typing import Callable, Iterable

from contracts import (
    ILotManager,
    ISlot,
    IVehicle,
    ITicket,
    IFees,
    ParkingLotError,
)

class LotManager(ILotManager):
    """
    Manage parking slots and active parking sessions.

    The manager receives parking slots, a fee calculator, and a
    ticket factory through its constructor. This allows it to work
    with any objects that follow the project contracts.
    """

    def __init__(
        self,
        slots: Iterable[ISlot],
        fee_calculator: IFees,
        ticket_factory: Callable[[int, IVehicle, ISlot, datetime], ITicket],
    ):
        """
        Initialize the parking lot manager.

        Args:
            slots: The parking slots managed by this lot.
            fee_calculator: An object implementing the IFees contract.
            ticket_factory: A function that creates an ITicket.
                It must accept ticket number, vehicle, slot, and
                entry time, in that order.

        Raises:
            ValueError: If the slots are invalid or empty.
            TypeError: If the fee calculator or ticket factory is invalid.
        """
        try:
            slot_list = tuple(slots)
        except TypeError:
            raise ValueError("Slots must be an iterable of parking slots.")

        if not slot_list:
            raise ValueError("The parking lot must have at least one slot.")

        if not all(isinstance(slot, ISlot) for slot in slot_list):
            raise ValueError("Every item must implement the ISlot contract.")

        if not isinstance(fee_calculator, IFees):
            raise TypeError("Fee calculator must implement the IFees contract.")

        if not callable(ticket_factory):
            raise TypeError("Ticket factory must be callable.")

        slot_numbers = [slot.slot_number for slot in slot_list]

        if any(
            not isinstance(number, int)
            or isinstance(number, bool)
            or number <= 0
            for number in slot_numbers
        ):
            raise ValueError("Every slot must have a positive integer number.")

        if len(slot_numbers) != len(set(slot_numbers)):
            raise ValueError("Parking slot numbers must be unique.")

        self._slots = slot_list
        self._fee_calculator = fee_calculator
        self._ticket_factory = ticket_factory

        self._active_tickets = {}
        self._next_ticket_number = 1

    @property
    def slots(self) -> tuple[ISlot, ...]:
        """Return all parking slots as an immutable tuple."""
        return self._slots

    @property
    def active_ticket_count(self) -> int:
        """Return the number of currently active parking tickets."""
        return len(self._active_tickets)

    @property
    def active_tickets(self) -> tuple[ITicket, ...]:
        """Return the active tickets as an immutable tuple."""
        return tuple(self._active_tickets.values())

    def park_vehicle(self, vehicle: IVehicle) -> ITicket:
        """
        Assign a vehicle to a suitable available slot and create a ticket.

        Args:
            vehicle: An object implementing the IVehicle contract.

        Returns:
            The newly created parking ticket.

        Raises:
            TypeError: If the vehicle does not implement IVehicle.
            ParkingLotError: If the vehicle is already parked or
                             no suitable available slot exists.
        """
        if not isinstance(vehicle, IVehicle):
            raise TypeError("Vehicle must implement the IVehicle contract.")

        # Business rule 1: A vehicle cannot be parked twice.
        for ticket in self._active_tickets.values():
            if ticket.vehicle.vehicle_plate == vehicle.vehicle_plate:
                raise ParkingLotError(
                    f"Vehicle {vehicle.vehicle_plate} is already parked."
                )

        # Find the first available slot that can fit the vehicle.
        suitable_slot = None

        for slot in self._slots:
            if slot.is_available and slot.can_fit(vehicle):
                suitable_slot = slot
                break

        # Business rule 2: A vehicle must have a suitable available slot.
        if suitable_slot is None:
            raise ParkingLotError(
                f"No suitable parking slot is available for "
                f"vehicle {vehicle.vehicle_plate}."
            )

        entry_time = datetime.now()
        ticket_number = self._next_ticket_number

        # Assign the vehicle before creating its ticket.
        suitable_slot.assign_vehicle(vehicle)

        try:
            ticket = self._ticket_factory(
                ticket_number,
                vehicle,
                suitable_slot,
                entry_time,
            )

            if not isinstance(ticket, ITicket):
                raise TypeError(
                    "The ticket factory must return an ITicket object."
                )

            if ticket.ticket_number != ticket_number:
                raise ValueError(
                    "The created ticket must use the assigned ticket number."
                )

            if ticket.vehicle is not vehicle or ticket.slot is not suitable_slot:
                raise ValueError(
                    "The ticket must reference the assigned vehicle and slot."
                )

        except Exception:
            # Undo the slot assignment if ticket creation fails.
            suitable_slot.remove_vehicle()
            raise

        self._active_tickets[ticket_number] = ticket
        self._next_ticket_number += 1

        return ticket

    def release_vehicle(
        self,
        ticket_number: int,
        exit_time: datetime,
    ) -> float:
        """
        Release a parked vehicle and calculate its parking fee.

        Args:
            ticket_number: The number of the active parking ticket.
            exit_time: The date and time when the vehicle exits.

        Returns:
            The parking fee in pesos.

        Raises:
            ValueError: If the ticket number or exit time is invalid.
            ParkingLotError: If the ticket cannot be found or released.
        """
        if (
            not isinstance(ticket_number, int)
            or isinstance(ticket_number, bool)
            or ticket_number <= 0
        ):
            raise ValueError("Ticket number must be a positive integer.")

        if not isinstance(exit_time, datetime):
            raise ValueError("Exit time must be a datetime object.")

        # Business rule 3: Only an active ticket can be released.
        if ticket_number not in self._active_tickets:
            raise ParkingLotError(
                f"No active parking ticket found with number {ticket_number}."
            )

        ticket = self._active_tickets[ticket_number]
        assigned_slot = ticket.slot

        # Make sure the ticket's vehicle is still in its assigned slot.
        if assigned_slot.assigned_vehicle is not ticket.vehicle:
            raise ParkingLotError(
                "The ticket's vehicle is not in its assigned parking slot."
            )

        # Close the ticket before calculating its fee.
        ticket.close(exit_time)

        fee = self._fee_calculator.compute_fee(ticket)

        # Remove the vehicle and mark the ticket as no longer active.
        assigned_slot.remove_vehicle()
        del self._active_tickets[ticket_number]

        return fee

    def __len__(self) -> int:
        """Return the number of active parking tickets."""
        return self.active_ticket_count

    def __str__(self) -> str:
        """Return a readable summary of the parking lot."""
        available_count = sum(
            1 for slot in self._slots if slot.is_available
        )

        return (
            f"Parking Lot: {available_count}/{len(self._slots)} "
            f"slots available, {self.active_ticket_count} "
            f"active ticket(s)"
        )
