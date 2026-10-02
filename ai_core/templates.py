"""Document type templates and section blueprints.

Add new document types by extending DOCUMENT_TEMPLATES and the DocumentType enum.
"""

from typing import Dict, List

from backend.models.schemas import DocumentType


# Section blueprints guide the AI toward consistent structure per document type.
DOCUMENT_TEMPLATES: Dict[DocumentType, Dict[str, object]] = {
    DocumentType.EMPLOYMENT_CONTRACT: {
        "title": "Employment Contract",
        "sections": [
            "Parties",
            "Position and Duties",
            "Compensation and Benefits",
            "Working Hours and Location",
            "Confidentiality",
            "Termination",
            "Governing Law",
            "Signatures",
        ],
        "description": "Agreement between employer and employee defining role, pay, and terms.",
    },
    DocumentType.NDA: {
        "title": "Non-Disclosure Agreement (NDA)",
        "sections": [
            "Parties",
            "Definition of Confidential Information",
            "Obligations of Receiving Party",
            "Exclusions",
            "Term and Duration",
            "Remedies",
            "Governing Law",
            "Signatures",
        ],
        "description": "Agreement protecting confidential information shared between parties.",
    },
    DocumentType.LEASE_AGREEMENT: {
        "title": "Lease Agreement",
        "sections": [
            "Parties",
            "Property Description",
            "Lease Term",
            "Rent and Deposits",
            "Use of Premises",
            "Maintenance and Repairs",
            "Termination",
            "Governing Law",
            "Signatures",
        ],
        "description": "Agreement between landlord and tenant for property rental.",
    },
    DocumentType.FREELANCE_AGREEMENT: {
        "title": "Freelance Agreement",
        "sections": [
            "Parties",
            "Scope of Work",
            "Deliverables and Timeline",
            "Fees and Payment",
            "Intellectual Property",
            "Confidentiality",
            "Termination",
            "Governing Law",
            "Signatures",
        ],
        "description": "Agreement for independent contractor / freelance services.",
    },
    DocumentType.SERVICE_AGREEMENT: {
        "title": "Service Agreement",
        "sections": [
            "Parties",
            "Services Description",
            "Service Levels",
            "Fees and Invoicing",
            "Client Obligations",
            "Limitation of Liability",
            "Termination",
            "Governing Law",
            "Signatures",
        ],
        "description": "Agreement defining professional or business services to be provided.",
    },
    DocumentType.OFFER_LETTER: {
        "title": "Offer Letter",
        "sections": [
            "Recipient",
            "Position Offered",
            "Compensation",
            "Start Date",
            "Conditions of Offer",
            "Acceptance",
            "Signatures",
        ],
        "description": "Formal employment offer letter outlining role and compensation.",
    },
    DocumentType.PARTNERSHIP_AGREEMENT: {
        "title": "Partnership Agreement",
        "sections": [
            "Parties",
            "Partnership Purpose",
            "Capital Contributions",
            "Profit and Loss Sharing",
            "Management and Decisions",
            "Admission and Withdrawal",
            "Dissolution",
            "Governing Law",
            "Signatures",
        ],
        "description": "Agreement governing partnership structure, contributions, and profits.",
    },
    DocumentType.GENERAL_AGREEMENT: {
        "title": "General Agreement",
        "sections": [
            "Parties",
            "Purpose",
            "Terms and Conditions",
            "Obligations",
            "Payment (if applicable)",
            "Termination",
            "Governing Law",
            "Signatures",
        ],
        "description": "Flexible general-purpose agreement template.",
    },
}


def get_template(document_type: DocumentType) -> Dict[str, object]:
    """Return template metadata for a document type."""
    if document_type not in DOCUMENT_TEMPLATES:
        raise ValueError(f"Unsupported document type: {document_type}")
    return DOCUMENT_TEMPLATES[document_type]


def list_document_types() -> List[str]:
    """Return human-readable document type names."""
    return [dt.value for dt in DocumentType]


def list_section_headings(document_type: DocumentType) -> List[str]:
    """Return recommended section headings for a document type."""
    template = get_template(document_type)
    return list(template["sections"])  # type: ignore[arg-type]
