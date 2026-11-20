"""Signed charters, token hashes, and RFC 9449 DPoP proofs."""
from __future__ import annotations

import base64
import hashlib
import json
import time
import uuid
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ec import (
    ECDSA,
    SECP256R1,
    EllipticCurvePublicNumbers,
)
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

from .errors import PolicyDenied


def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def jwk_thumbprint(jwk: Mapping[str, str]) -> str:
    if jwk.get("kty") == "EC" and jwk.get("crv") == "P-256":
        material = {"crv": jwk["crv"], "kty": "EC", "x": jwk["x"], "y": jwk["y"]}
    elif jwk.get("kty") == "OKP" and jwk.get("crv") == "Ed25519":
        material = {"crv": "Ed25519", "kty": "OKP", "x": jwk["x"]}
    else:
        raise PolicyDenied("DENY_UNVERIFIED_PRINCIPAL", "Unsupported public key")
    return b64url(hashlib.sha256(canonical_json(material)).digest())


def _public_key(jwk: Mapping[str, str]) -> Any:
    try:
        if jwk.get("kty") == "EC" and jwk.get("crv") == "P-256":
            x = int.from_bytes(_b64decode(jwk["x"]), "big")
            y = int.from_bytes(_b64decode(jwk["y"]), "big")
            return EllipticCurvePublicNumbers(x, y, SECP256R1()).public_key()
        if jwk.get("kty") == "OKP" and jwk.get("crv") == "Ed25519":
            return Ed25519PublicKey.from_public_bytes(_b64decode(jwk["x"]))
    except Exception as err:
        raise PolicyDenied("DENY_UNVERIFIED_PRINCIPAL", "Malformed public key") from err
    raise PolicyDenied("DENY_UNVERIFIED_PRINCIPAL", "Unsupported public key")


def public_jwk(public_key: Any) -> Dict[str, str]:
    if hasattr(public_key, "public_numbers"):
        numbers = public_key.public_numbers()
        return {
            "kty": "EC", "crv": "P-256",
            "x": b64url(numbers.x.to_bytes(32, "big")),
            "y": b64url(numbers.y.to_bytes(32, "big")),
        }
    return {
        "kty": "OKP", "crv": "Ed25519",
        "x": b64url(public_key.public_bytes(Encoding.Raw, PublicFormat.Raw)),
    }


def verify_charter(manifest: Mapping[str, Any], trusted_keys: Mapping[str, str]) -> Dict[str, Any]:
    """Verify a pinned Ed25519-signed agent charter without trusting self-assertion."""
    try:
        agent_id = manifest["agent_id"]
        capabilities = manifest["capabilities"]
        jwk = manifest["public_key"]
        signature = _b64decode(manifest["signature"])
        if not isinstance(agent_id, str) or not isinstance(capabilities, list):
            raise TypeError("invalid fields")
        if not all(isinstance(item, str) and item for item in capabilities):
            raise ValueError("invalid capabilities")
        if trusted_keys.get(agent_id) != jwk_thumbprint(jwk):
            raise PolicyDenied("DENY_UNVERIFIED_PRINCIPAL", "Charter key is not pinned")
        payload = {key: value for key, value in manifest.items() if key != "signature"}
        _public_key(jwk).verify(signature, canonical_json(payload))
    except PolicyDenied:
        raise
    except (KeyError, ValueError, TypeError, InvalidSignature) as err:
        raise PolicyDenied("DENY_UNVERIFIED_PRINCIPAL", "Invalid agent charter") from err
    return {"agent_id": agent_id, "capabilities": frozenset(capabilities)}


def load_and_verify_charter(path: str, trusted_keys: Mapping[str, str]) -> Dict[str, Any]:
    try:
        manifest = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as err:
        raise PolicyDenied("DENY_UNVERIFIED_PRINCIPAL", "Agent charter cannot be loaded") from err
    if not isinstance(manifest, dict):
        raise PolicyDenied("DENY_UNVERIFIED_PRINCIPAL", "Agent charter must be an object")
    return verify_charter(manifest, trusted_keys)


def dpop_proof(private_key: Any, method: str, url: str, access_token: str,
               *, now: Optional[float] = None, jti: Optional[str] = None) -> str:
    """Create an ES256 DPoP proof; intended for adapters and ephemeral-key tests."""
    header = {"typ": "dpop+jwt", "alg": "ES256", "jwk": public_jwk(private_key.public_key())}
    payload = {
        "htu": url.split("?", 1)[0].split("#", 1)[0], "htm": method.upper(),
        "iat": int(time.time() if now is None else now), "jti": jti or str(uuid.uuid4()),
        "ath": b64url(hashlib.sha256(access_token.encode("ascii")).digest()),
    }
    signing_input = b64url(canonical_json(header)) + "." + b64url(canonical_json(payload))
    signature = private_key.sign(signing_input.encode("ascii"), ECDSA(SHA256()))
    return signing_input + "." + b64url(signature)


def decode_dpop(proof: str) -> Tuple[Dict[str, Any], Dict[str, Any], bytes, bytes]:
    try:
        encoded_header, encoded_payload, encoded_signature = proof.split(".")
        header = json.loads(_b64decode(encoded_header))
        payload = json.loads(_b64decode(encoded_payload))
        return header, payload, _b64decode(encoded_signature), (encoded_header + "." + encoded_payload).encode("ascii")
    except Exception as err:
        raise PolicyDenied("DPOP_INVALID", "Malformed DPoP proof") from err


def verify_dpop_signature(header: Mapping[str, Any], signing_input: bytes, signature: bytes) -> None:
    if header.get("typ") != "dpop+jwt" or header.get("alg") != "ES256":
        raise PolicyDenied("DPOP_INVALID", "Invalid DPoP header")
    try:
        jwk = header["jwk"]
        if jwk.get("kty") != "EC" or jwk.get("crv") != "P-256":
            raise ValueError("wrong key")
        _public_key(jwk).verify(signature, signing_input, ECDSA(SHA256()))
    except PolicyDenied:
        raise
    except Exception as err:
        raise PolicyDenied("DPOP_INVALID", "Invalid DPoP signature") from err


__all__ = [
    "b64url", "canonical_json", "decode_dpop", "dpop_proof", "jwk_thumbprint",
    "load_and_verify_charter", "public_jwk", "sha256", "verify_charter",
    "verify_dpop_signature",
]
