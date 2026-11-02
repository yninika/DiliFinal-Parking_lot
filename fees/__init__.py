# Author: Ana Lynica B. Ferolino (module: fees)
"""Fees module for the Parking Lot Management System.

Implements the IFees contract. Imports only from `contracts` and the
standard library, and works with ANY ticket that follows ITicket.
"""

import math

from contracts import IFees, ITicket, ParkingLotError


def _check_rate(name, value):
    """Raise ValueError unless value is a finite, non-negative real number."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a number")
    if not math.isfinite(value) or value < 0:
        raise ValueError(f"{name} must be a finite number >= 0")


class StandardFees(IFees):
    """Hourly parking fees with a free grace period.

    Rules:
      * Time within the grace period (inclusive) is free (0.0).
      * Beyond the grace period, every started hour is charged, with a
        minimum of 1 hour (61 minutes = 2 hours).
      * Cars and motorcycles each have their own hourly rate (pesos).
    """

    def __init__(self, car_hourly_rate: float = 50.0,
                 motorcycle_hourly_rate: float = 20.0,
                 grace_minutes: int = 15):
        """Create a fee schedule.

        Raises ValueError if a rate is not a finite number >= 0, or if
        grace_minutes is not an int >= 0.
        """
        _check_rate("car_hourly_rate", car_hourly_rate)
        _check_rate("motorcycle_hourly_rate", motorcycle_hourly_rate)
        if (isinstance(grace_minutes, bool)
                or not isinstance(grace_minutes, int)
                or grace_minutes < 0):
            raise ValueError("grace_minutes must be an int >= 0")
        self._car_rate = float(car_hourly_rate)
        self._motorcycle_rate = float(motorcycle_hourly_rate)
        self._grace_minutes = grace_minutes

    @property
    def car_hourly_rate(self) -> float:
        """Hourly rate for cars, in pesos (read-only)."""
        return self._car_rate

    @property
    def motorcycle_hourly_rate(self) -> float:
        """Hourly rate for motorcycles, in pesos (read-only)."""
        return self._motorcycle_rate

    @property
    def grace_minutes(self) -> int:
        """Free minutes at the start of every stay (read-only)."""
        return self._grace_minutes

    def rate_for(self, vehicle_type: str) -> float:
        """Return the hourly rate for 'car' or 'motorcycle'.

        Raises ParkingLotError for any other vehicle type.
        """
        rates = {"car": self._car_rate, "motorcycle": self._motorcycle_rate}
        if not isinstance(vehicle_type, str) or vehicle_type not in rates:
            raise ParkingLotError(
                f"No rate defined for vehicle type: {vehicle_type!r}")
        return rates[vehicle_type]

    def compute_fee(self, ticket: ITicket) -> float:
        """Return the fee in pesos for a closed ticket, rounded to 2 decimals.

        Raises ValueError if ticket is not an ITicket.
        Raises ParkingLotError if the ticket is still open or its
        vehicle type has no rate.
        """
        if not isinstance(ticket, ITicket):
            raise ValueError("ticket must implement ITicket")
        if ticket.exit_time is None:
            raise ParkingLotError(
                "Cannot compute a fee for a ticket that is still open")
        rate = self.rate_for(ticket.vehicle.vehicle_type)
        seconds = (ticket.exit_time - ticket.entry_time).total_seconds()
        if seconds <= self._grace_minutes * 60:
            return 0.0
        hours = max(1, math.ceil(seconds / 3600))
        return round(hours * rate, 2)

    def __str__(self) -> str:
        return (f"StandardFees(car=P{self._car_rate:.2f}/h, "
                f"motorcycle=P{self._motorcycle_rate:.2f}/h, "
                f"grace={self._grace_minutes} min)")

    def __eq__(self, other) -> bool:
        """Two schedules are equal if rates and grace period match."""
        if not isinstance(other, StandardFees):
            return NotImplemented
        return ((self._car_rate, self._motorcycle_rate, self._grace_minutes)
                == (other._car_rate, other._motorcycle_rate,
                    other._grace_minutes))

    def __hash__(self) -> int:
        """Hash consistent with __eq__."""
        return hash((self._car_rate, self._motorcycle_rate,
                     self._grace_minutes))
