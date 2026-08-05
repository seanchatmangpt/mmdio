"""구동 (Actuation) & 디스패치 (Dispatch) - High-Speed Action Execution & Causal Receipt Store in Korean."""

import json
from enum import Enum
from pathlib import Path
import blake3
import dspy

# Constants
STORE_PATH = Path("/Users/sac/turbo-fieldfare/kcj-mustar/scratch/mu_star_store/receipts.jsonl")

FILE_MODE_APPEND = "a"
ENCODING_UTF8 = "utf-8"
DEFAULT_APM_LEVEL = 100000

RECEIPT_KEY_PLAN_ID = "plan_id"
RECEIPT_KEY_RECEIPT = "receipt"
RECEIPT_KEY_STATUS = "status"

STATUS_DISPATCHED = "DISPATCHED"
DISPATCH_HASH_TEMPLATE = "DISPATCH:{0}:{1}:{2}"

ERROR_VERIFICATION_FAILED = "검증 실패: 디스패치거부"
MESSAGE_DISPATCH_COMPLETE = "실시간 구동 명령 디스패치 완료: [{0}]"


class APIResponseKey(Enum):
    """Korean API response dictionary keys."""
    SUCCESS = "성공"
    MESSAGE = "메시지"
    DISPATCH_ID = "디스패치ID"
    RECEIPT = "영수증"
    APM = "APM"


class 실시간디스패치Signature(dspy.Signature):
    """검증된 계획을 바탕으로 초고속 구동 디스패치 명령을 생성함."""
    검증계획_ko = dspy.InputField(desc="검증 완료된 실행 계획")
    구동명령_ko = dspy.OutputField(desc="즉시 실행 가능한 디스패치 명령어")


def append_causal_receipt(plan_id: str, receipt_hash: str, status: str) -> None:
    """Store causal receipt into persistent mu_star_store JSONL log."""
    STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    record = {
        RECEIPT_KEY_PLAN_ID: plan_id,
        RECEIPT_KEY_RECEIPT: receipt_hash,
        RECEIPT_KEY_STATUS: status
    }
    with open(STORE_PATH, FILE_MODE_APPEND, encoding=ENCODING_UTF8) as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def 디스패치실행(plan_id: str, verified: bool, apm_level: int = DEFAULT_APM_LEVEL) -> dict[str, str | bool | int]:
    """Execute high-speed action dispatch in Korean and append causal receipt."""
    if not verified:
        return {APIResponseKey.SUCCESS.value: False, APIResponseKey.MESSAGE.value: ERROR_VERIFICATION_FAILED, APIResponseKey.APM.value: 0}

    hasher = blake3.blake3()
    hasher.update(DISPATCH_HASH_TEMPLATE.format(plan_id, verified, apm_level).encode(ENCODING_UTF8))
    receipt_hash = hasher.hexdigest()

    append_causal_receipt(plan_id=plan_id, receipt_hash=receipt_hash, status=STATUS_DISPATCHED)

    return {
        APIResponseKey.SUCCESS.value: True,
        APIResponseKey.DISPATCH_ID.value: plan_id,
        APIResponseKey.MESSAGE.value: MESSAGE_DISPATCH_COMPLETE.format(plan_id),
        APIResponseKey.APM.value: apm_level,
        APIResponseKey.RECEIPT.value: receipt_hash
    }
