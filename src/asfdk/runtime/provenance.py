"""Mandatory content-bound ingress classification and synthesis gating."""
from __future__ import annotations

import hashlib
import hmac
import secrets
from collections.abc import Iterable
from typing import Any, Optional

from .crypto import canonical_json, sha256
from .errors import PolicyDenied
from .models import Provenance, SynthesizedContent


def content_digest(content: Any) -> str:
    try:
        return sha256(canonical_json(content))
    except (TypeError, ValueError) as err:
        raise PolicyDenied("DENY_UNCLASSIFIED_INGRESS", "Ingress must be JSON serializable") from err


class IngressClassifier:
    _known = {"public_external", "private", "restricted", "unknown_taint"}

    def __init__(self) -> None:
        self._attestation_key = secrets.token_bytes(32)

    def _attest(self, provenance: Provenance) -> str:
        message = (
            f"{provenance.classification}\0{provenance.source_id}\0"
            f"{provenance.no_derived_egress}\0{provenance.content_hash}"
        ).encode()
        return hmac.new(self._attestation_key, message, hashlib.sha256).hexdigest()

    def verify(self, provenance: Provenance) -> bool:
        return bool(provenance.attestation) and hmac.compare_digest(
            self._attest(provenance), provenance.attestation,
        )

    def classify(self, content: Any, *, source_id: str,
                 classification: Optional[str] = None) -> tuple[Any, Provenance]:
        if not source_id:
            raise PolicyDenied("DENY_UNCLASSIFIED_INGRESS", "Ingress source is required")
        label = "unknown_taint" if classification is None else classification
        if label not in self._known:
            raise PolicyDenied("DENY_UNCLASSIFIED_INGRESS", "Ingress classification is invalid")
        provenance = Provenance(
            classification=label, source_id=source_id,
            no_derived_egress=label != "public_external", content_hash=content_digest(content),
        )
        return content, Provenance(**{**provenance.__dict__, "attestation": self._attest(provenance)})

    def derive(self, content: Any, provenance: Iterable[Provenance]) -> SynthesizedContent:
        contributors = tuple(provenance)
        if not contributors or any(not self.verify(item) for item in contributors):
            raise PolicyDenied("DENY_COMPOSITE_EGRESS", "Valid classified contributors are required")
        digest = content_digest(content)
        synthesis = SynthesizedContent(content_hash=digest, provenance=contributors)
        evidence = canonical_json({
            "content_hash": digest, "contributors": [item.attestation for item in contributors],
        })
        attestation = hmac.new(self._attestation_key, evidence, hashlib.sha256).hexdigest()
        return SynthesizedContent(**{**synthesis.__dict__, "attestation": attestation})

    def verify_derivation(self, content: Any, synthesis: SynthesizedContent) -> bool:
        if content_digest(content) != synthesis.content_hash:
            return False
        expected = self.derive(content, synthesis.provenance)
        return hmac.compare_digest(expected.attestation, synthesis.attestation)


class CompositeSynthesisGate:
    """Bind every payload to direct ingress or an attested derived lineage."""

    _private_destinations = {
        "agent:private_context", "user:private_response", "user:direct_support_stream",
    }

    def __init__(self, classifier: IngressClassifier) -> None:
        self._classifier = classifier

    def authorize(self, destination: str, payload: Any, provenance: Iterable[Provenance],
                  synthesis: Optional[SynthesizedContent] = None) -> None:
        contributors = tuple(provenance)
        if not contributors or any(not self._classifier.verify(item) for item in contributors):
            raise PolicyDenied("DENY_COMPOSITE_EGRESS", "Ingress provenance attestation is invalid")
        if synthesis is not None:
            if contributors != synthesis.provenance or not self._classifier.verify_derivation(payload, synthesis):
                raise PolicyDenied("DENY_COMPOSITE_EGRESS", "Derived payload lineage is invalid")
        restricted = [item for item in contributors if item.no_derived_egress]
        if restricted and destination not in self._private_destinations:
            raise PolicyDenied(
                "DENY_COMPOSITE_EGRESS",
                "Restricted ingress cannot contribute to this outbound destination",
                details={"source_ids": [item.source_id for item in restricted]},
            )


__all__ = ["CompositeSynthesisGate", "IngressClassifier", "content_digest"]
