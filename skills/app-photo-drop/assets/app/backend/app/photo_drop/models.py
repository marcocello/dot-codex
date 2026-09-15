from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True)
class Session:
    id: str
    token: str
    state: str
    event_name: str
    destination: Path
    guest_url: str
    created_at: datetime
    expires_at: datetime
    ended_at: datetime | None
    end_reason: str | None

    def admin_payload(self) -> dict[str, object]:
        return {
            "id": self.id,
            "state": self.state,
            "event_name": self.event_name,
            "guest_url": self.guest_url,
            "destination": str(self.destination),
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "end_reason": self.end_reason,
        }
