"""Governance Agent for Enterprise Policy Enforcement."""

from __future__ import annotations

import logging
from typing import Any

from app.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class GovernanceAgent(BaseAgent):
    """
    Specialized agent for enforcing enterprise governance policies.
    
    This agent checks code changes against organizational policies,
    compliance requirements, and internal standards. It focuses on
    enterprise-level governance rather than general code quality.
    """

    agent_name = "governance-agent"
    category = "enterprise-governance"

    def __init__(self) -> None:
        """Initialize the governance agent with policy rules."""
        self.policy_checks = [
            self._check_internal_standards,
            self._check_compliance_requirements,
            self._check_audit_requirements,
            self._check_data_governance,
            self._check_api_governance,
        ]

    async def analyze(
        self,
        pull_request: dict[str, Any],
        diffs: list[dict[str, Any]],
        context: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Analyze PR for governance policy violations.
        
        Args:
            pull_request: PR metadata
            diffs: Code changes
            context: Additional context (organizational policies, etc.)
            
        Returns:
            Structured findings with policy violations
        """
        findings: list[dict[str, Any]] = []
        
        # Run all policy checks
        for check in self.policy_checks:
            check_findings = await check(pull_request, diffs, context or [])
            findings.extend(check_findings)
        
        summary = self._generate_summary(findings)
        
        return self.format_result(
            summary=summary,
            findings=findings,
            metadata={
                "total_violations": len(findings),
                "blocking_violations": len([f for f in findings if f.get("enforcement") == "blocking"]),
                "policies_checked": len(self.policy_checks),
            },
        )

    async def _check_internal_standards(
        self,
        pull_request: dict[str, Any],
        diffs: list[dict[str, Any]],
        context: list[str],
    ) -> list[dict[str, Any]]:
        """Check against internal organizational standards."""
        findings = []
        
        for diff in diffs:
            file_path = diff.get("path", "")
            content = diff.get("content", "")
            
            # Check for hardcoded credentials (internal standard)
            if any(keyword in content.lower() for keyword in ["password", "api_key", "secret"]):
                if "=" in content and not content.strip().startswith("#"):
                    findings.append({
                        "type": "internal_standard_violation",
                        "severity": "high",
                        "enforcement": "error",
                        "file": file_path,
                        "message": "Potential hardcoded credentials detected",
                        "description": "Internal standards prohibit hardcoded credentials in source code",
                        "remediation": "Use environment variables or secure credential management",
                        "policy": "INTERNAL-SEC-001",
                    })
            
            # Check for proper error handling (internal standard)
            if "try:" in content and "except:" in content:
                if "except:" in content and "pass" in content:
                    findings.append({
                        "type": "internal_standard_violation",
                        "severity": "medium",
                        "enforcement": "warning",
                        "file": file_path,
                        "message": "Empty exception handler detected",
                        "description": "Internal standards require proper error handling and logging",
                        "remediation": "Add appropriate error handling and logging",
                        "policy": "INTERNAL-CODE-002",
                    })
            
            # Check for TODO/FIXME in production code
            if any(marker in content.upper() for marker in ["TODO", "FIXME", "HACK"]):
                if "production" in file_path.lower() or "prod" in file_path.lower():
                    findings.append({
                        "type": "internal_standard_violation",
                        "severity": "low",
                        "enforcement": "warning",
                        "file": file_path,
                        "message": "TODO/FIXME markers in production code",
                        "description": "Production code should not contain unresolved TODO/FIXME markers",
                        "remediation": "Resolve or remove TODO/FIXME markers before merging",
                        "policy": "INTERNAL-QUAL-003",
                    })
        
        return findings

    async def _check_compliance_requirements(
        self,
        pull_request: dict[str, Any],
        diffs: list[dict[str, Any]],
        context: list[str],
    ) -> list[dict[str, Any]]:
        """Check compliance with regulatory requirements."""
        findings = []
        
        for diff in diffs:
            file_path = diff.get("path", "")
            content = diff.get("content", "")
            
            # Check for PII handling
            pii_keywords = ["ssn", "social_security", "credit_card", "passport", "driver_license"]
            if any(keyword in content.lower() for keyword in pii_keywords):
                findings.append({
                    "type": "compliance_requirement",
                    "severity": "critical",
                    "enforcement": "blocking",
                    "file": file_path,
                    "message": "Potential PII handling detected",
                    "description": "Code handling PII must comply with data protection regulations",
                    "remediation": "Ensure proper encryption, access controls, and audit logging",
                    "policy": "COMPLIANCE-GDPR-001",
                    "frameworks": ["GDPR", "CCPA", "HIPAA"],
                })
            
            # Check for audit logging requirements
            if "delete" in content.lower() or "remove" in content.lower():
                if "audit" not in content.lower() and "log" not in content.lower():
                    findings.append({
                        "type": "compliance_requirement",
                        "severity": "high",
                        "enforcement": "error",
                        "file": file_path,
                        "message": "Deletion operation without audit logging",
                        "description": "Compliance requires audit trails for data modifications",
                        "remediation": "Add audit logging for deletion operations",
                        "policy": "COMPLIANCE-AUDIT-002",
                        "frameworks": ["SOC2", "ISO27001"],
                    })
        
        return findings

    async def _check_audit_requirements(
        self,
        pull_request: dict[str, Any],
        diffs: list[dict[str, Any]],
        context: list[str],
    ) -> list[dict[str, Any]]:
        """Check audit trail requirements."""
        findings = []
        
        for diff in diffs:
            file_path = diff.get("path", "")
            content = diff.get("content", "")
            
            # Check for database schema changes
            if "migration" in file_path.lower() or "schema" in file_path.lower():
                findings.append({
                    "type": "audit_requirement",
                    "severity": "medium",
                    "enforcement": "warning",
                    "file": file_path,
                    "message": "Database schema change detected",
                    "description": "Schema changes require documentation and approval",
                    "remediation": "Ensure schema change is documented and approved by DBA team",
                    "policy": "AUDIT-DB-001",
                })
            
            # Check for configuration changes
            if file_path.endswith((".yaml", ".yml", ".json", ".xml", ".properties")):
                if "config" in file_path.lower() or "settings" in file_path.lower():
                    findings.append({
                        "type": "audit_requirement",
                        "severity": "low",
                        "enforcement": "info",
                        "file": file_path,
                        "message": "Configuration file modified",
                        "description": "Configuration changes should be tracked in audit log",
                        "remediation": "Document configuration change rationale",
                        "policy": "AUDIT-CONFIG-002",
                    })
        
        return findings

    async def _check_data_governance(
        self,
        pull_request: dict[str, Any],
        diffs: list[dict[str, Any]],
        context: list[str],
    ) -> list[dict[str, Any]]:
        """Check data governance policies."""
        findings = []
        
        for diff in diffs:
            file_path = diff.get("path", "")
            content = diff.get("content", "")
            
            # Check for data retention policies
            if "delete" in content.lower() or "purge" in content.lower():
                if "retention" not in content.lower():
                    findings.append({
                        "type": "data_governance",
                        "severity": "medium",
                        "enforcement": "warning",
                        "file": file_path,
                        "message": "Data deletion without retention policy check",
                        "description": "Data governance requires retention policy compliance",
                        "remediation": "Verify data retention policy before deletion",
                        "policy": "DATA-GOV-001",
                    })
            
            # Check for data classification
            if "export" in content.lower() or "download" in content.lower():
                findings.append({
                    "type": "data_governance",
                    "severity": "medium",
                    "enforcement": "warning",
                    "file": file_path,
                    "message": "Data export operation detected",
                    "description": "Data exports must respect classification and access controls",
                    "remediation": "Ensure proper data classification and authorization checks",
                    "policy": "DATA-GOV-002",
                })
        
        return findings

    async def _check_api_governance(
        self,
        pull_request: dict[str, Any],
        diffs: list[dict[str, Any]],
        context: list[str],
    ) -> list[dict[str, Any]]:
        """Check API governance policies."""
        findings = []
        
        for diff in diffs:
            file_path = diff.get("path", "")
            content = diff.get("content", "")
            
            # Check for API versioning
            if "api" in file_path.lower() or "@app.route" in content or "@router" in content:
                if "/v1/" not in content and "/v2/" not in content and "version" not in content.lower():
                    findings.append({
                        "type": "api_governance",
                        "severity": "medium",
                        "enforcement": "warning",
                        "file": file_path,
                        "message": "API endpoint without versioning",
                        "description": "API governance requires versioned endpoints",
                        "remediation": "Add version prefix to API endpoints (e.g., /v1/)",
                        "policy": "API-GOV-001",
                    })
            
            # Check for API documentation
            if "@app.route" in content or "@router" in content:
                if '"""' not in content and "'''" not in content:
                    findings.append({
                        "type": "api_governance",
                        "severity": "low",
                        "enforcement": "info",
                        "file": file_path,
                        "message": "API endpoint without documentation",
                        "description": "API governance requires endpoint documentation",
                        "remediation": "Add docstring with endpoint description and parameters",
                        "policy": "API-GOV-002",
                    })
        
        return findings

    def _generate_summary(self, findings: list[dict[str, Any]]) -> str:
        """Generate a summary of governance findings."""
        if not findings:
            return "No governance policy violations detected"
        
        by_severity = {}
        for finding in findings:
            severity = finding.get("severity", "unknown")
            by_severity[severity] = by_severity.get(severity, 0) + 1
        
        blocking = len([f for f in findings if f.get("enforcement") == "blocking"])
        
        summary_parts = [f"Found {len(findings)} governance policy violation(s)"]
        
        if blocking > 0:
            summary_parts.append(f"{blocking} blocking violation(s) must be resolved")
        
        severity_summary = ", ".join(f"{count} {severity}" for severity, count in by_severity.items())
        summary_parts.append(f"Severity breakdown: {severity_summary}")
        
        return ". ".join(summary_parts)

# Made with Bob