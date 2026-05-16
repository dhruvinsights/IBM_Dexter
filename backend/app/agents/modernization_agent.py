"""Modernization Agent for IBM Ecosystem Modernization."""

from __future__ import annotations

import logging
from typing import Any

from app.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class ModernizationAgent(BaseAgent):
    """
    Specialized agent for IBM ecosystem modernization recommendations.
    
    This agent focuses on identifying legacy IBM technologies and providing
    guidance for modernizing to cloud-native patterns, including WebSphere
    to Liberty migration, mainframe modernization, and containerization.
    """

    agent_name = "modernization-agent"
    category = "ibm-modernization"

    def __init__(self) -> None:
        """Initialize the modernization agent with detection patterns."""
        self.legacy_patterns = {
            "WebSphere Traditional": {
                "patterns": ["was.install", "websphere.xml", "ibm-web-ext.xml"],
                "modern_alternative": "WebSphere Liberty",
                "priority": "high",
            },
            "WebSphere MQ": {
                "patterns": ["com.ibm.mq", "wmq", "mqseries"],
                "modern_alternative": "IBM MQ on Cloud / Event Streams",
                "priority": "medium",
            },
            "Db2 Legacy": {
                "patterns": ["db2 v9", "db2 v10"],
                "modern_alternative": "Db2 on Cloud / Db2 Warehouse",
                "priority": "medium",
            },
            "CICS": {
                "patterns": ["cics", "cobol"],
                "modern_alternative": "CICS TS for z/OS Cloud / Microservices",
                "priority": "high",
            },
            "IMS": {
                "patterns": ["ims db", "ims tm"],
                "modern_alternative": "IMS on Cloud / Modern Data Layer",
                "priority": "high",
            },
        }

    async def analyze(
        self,
        pull_request: dict[str, Any],
        diffs: list[dict[str, Any]],
        context: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Analyze PR for modernization opportunities.
        
        Args:
            pull_request: PR metadata
            diffs: Code changes
            context: Additional context
            
        Returns:
            Structured findings with modernization recommendations
        """
        findings: list[dict[str, Any]] = []
        
        # Detect legacy technologies
        legacy_findings = await self._detect_legacy_technologies(diffs)
        findings.extend(legacy_findings)
        
        # Check for cloud-native patterns
        cloud_native_findings = await self._check_cloud_native_patterns(diffs)
        findings.extend(cloud_native_findings)
        
        # Check for containerization opportunities
        container_findings = await self._check_containerization(diffs)
        findings.extend(container_findings)
        
        # Check for microservices patterns
        microservices_findings = await self._check_microservices_patterns(diffs)
        findings.extend(microservices_findings)
        
        summary = self._generate_summary(findings)
        
        return self.format_result(
            summary=summary,
            findings=findings,
            metadata={
                "total_opportunities": len(findings),
                "high_priority": len([f for f in findings if f.get("priority") == "high"]),
                "legacy_technologies_detected": len(legacy_findings),
            },
        )

    async def _detect_legacy_technologies(
        self,
        diffs: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Detect legacy IBM technologies in code."""
        findings = []
        
        for diff in diffs:
            file_path = diff.get("path", "")
            content = diff.get("content", "").lower()
            
            for tech_name, tech_info in self.legacy_patterns.items():
                for pattern in tech_info["patterns"]:
                    if pattern.lower() in content:
                        findings.append({
                            "type": "legacy_technology",
                            "severity": "medium",
                            "priority": tech_info["priority"],
                            "file": file_path,
                            "legacy_technology": tech_name,
                            "modern_alternative": tech_info["modern_alternative"],
                            "message": f"Legacy {tech_name} detected",
                            "description": f"Consider modernizing from {tech_name} to {tech_info['modern_alternative']}",
                            "remediation": self._get_migration_guidance(tech_name),
                            "benefits": [
                                "Cloud-native deployment",
                                "Improved scalability",
                                "Reduced operational costs",
                                "Better developer experience",
                            ],
                        })
                        break  # Only report once per technology per file
        
        return findings

    async def _check_cloud_native_patterns(
        self,
        diffs: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Check for cloud-native pattern adoption."""
        findings = []
        
        for diff in diffs:
            file_path = diff.get("path", "")
            content = diff.get("content", "")
            
            # Check for 12-factor app principles
            if "config" in file_path.lower():
                if "environment" not in content.lower() and "env" not in content.lower():
                    findings.append({
                        "type": "cloud_native_opportunity",
                        "severity": "low",
                        "priority": "medium",
                        "file": file_path,
                        "message": "Configuration not externalized",
                        "description": "12-factor app principle: Store config in environment",
                        "remediation": "Use environment variables for configuration",
                        "pattern": "12-factor-config",
                    })
            
            # Check for health checks
            if "server" in file_path.lower() or "main" in file_path.lower():
                if "health" not in content.lower() and "readiness" not in content.lower():
                    findings.append({
                        "type": "cloud_native_opportunity",
                        "severity": "low",
                        "priority": "medium",
                        "file": file_path,
                        "message": "Missing health check endpoints",
                        "description": "Cloud-native apps should expose health/readiness endpoints",
                        "remediation": "Add /health and /ready endpoints for Kubernetes",
                        "pattern": "health-checks",
                    })
            
            # Check for stateless design
            if "session" in content.lower() and "state" in content.lower():
                if "redis" not in content.lower() and "cache" not in content.lower():
                    findings.append({
                        "type": "cloud_native_opportunity",
                        "severity": "medium",
                        "priority": "high",
                        "file": file_path,
                        "message": "Potential stateful session management",
                        "description": "Cloud-native apps should be stateless",
                        "remediation": "Use external session store (Redis, etc.) or JWT tokens",
                        "pattern": "stateless-design",
                    })
        
        return findings

    async def _check_containerization(
        self,
        diffs: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Check for containerization opportunities."""
        findings = []
        
        has_dockerfile = any(diff.get("path", "").lower() == "dockerfile" for diff in diffs)
        has_compose = any("docker-compose" in diff.get("path", "").lower() for diff in diffs)
        
        if not has_dockerfile:
            findings.append({
                "type": "containerization_opportunity",
                "severity": "low",
                "priority": "medium",
                "message": "No Dockerfile found",
                "description": "Containerization enables consistent deployments",
                "remediation": "Create a Dockerfile for containerized deployment",
                "benefits": [
                    "Consistent environments",
                    "Easy deployment to OpenShift/Kubernetes",
                    "Better resource utilization",
                ],
            })
        
        for diff in diffs:
            file_path = diff.get("path", "")
            content = diff.get("content", "")
            
            # Check Dockerfile best practices
            if file_path.lower() == "dockerfile":
                if "FROM" in content and "latest" in content:
                    findings.append({
                        "type": "containerization_improvement",
                        "severity": "medium",
                        "priority": "medium",
                        "file": file_path,
                        "message": "Using 'latest' tag in Dockerfile",
                        "description": "Using 'latest' tag can lead to inconsistent builds",
                        "remediation": "Pin to specific version tags",
                        "pattern": "dockerfile-best-practices",
                    })
                
                if "USER root" in content or "USER 0" in content:
                    findings.append({
                        "type": "containerization_improvement",
                        "severity": "high",
                        "priority": "high",
                        "file": file_path,
                        "message": "Running container as root",
                        "description": "Security best practice: avoid running as root",
                        "remediation": "Create and use a non-root user",
                        "pattern": "dockerfile-security",
                    })
        
        return findings

    async def _check_microservices_patterns(
        self,
        diffs: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Check for microservices architecture patterns."""
        findings = []
        
        for diff in diffs:
            file_path = diff.get("path", "")
            content = diff.get("content", "")
            
            # Check for service discovery
            if "service" in file_path.lower():
                if "http://" in content and "localhost" not in content:
                    if "discovery" not in content.lower() and "consul" not in content.lower():
                        findings.append({
                            "type": "microservices_pattern",
                            "severity": "medium",
                            "priority": "medium",
                            "file": file_path,
                            "message": "Hardcoded service URLs",
                            "description": "Microservices should use service discovery",
                            "remediation": "Use Kubernetes service discovery or Consul",
                            "pattern": "service-discovery",
                        })
            
            # Check for circuit breaker pattern
            if "http" in content.lower() and "request" in content.lower():
                if "retry" not in content.lower() and "circuit" not in content.lower():
                    findings.append({
                        "type": "microservices_pattern",
                        "severity": "low",
                        "priority": "low",
                        "file": file_path,
                        "message": "Missing resilience patterns",
                        "description": "Microservices should implement circuit breakers and retries",
                        "remediation": "Add circuit breaker pattern (e.g., using resilience4j)",
                        "pattern": "circuit-breaker",
                    })
            
            # Check for API gateway pattern
            if "route" in content.lower() or "endpoint" in content.lower():
                if len([d for d in diffs if "route" in d.get("content", "").lower()]) > 10:
                    findings.append({
                        "type": "microservices_pattern",
                        "severity": "low",
                        "priority": "low",
                        "file": file_path,
                        "message": "Many routes in single service",
                        "description": "Consider using API Gateway pattern",
                        "remediation": "Implement API Gateway for routing and cross-cutting concerns",
                        "pattern": "api-gateway",
                    })
        
        return findings

    def _get_migration_guidance(self, legacy_tech: str) -> str:
        """Get specific migration guidance for legacy technology."""
        guidance = {
            "WebSphere Traditional": (
                "1. Assess application for Liberty compatibility\n"
                "2. Use IBM Transformation Advisor\n"
                "3. Migrate to WebSphere Liberty\n"
                "4. Containerize with OpenShift\n"
                "5. Implement cloud-native patterns"
            ),
            "WebSphere MQ": (
                "1. Evaluate message patterns and volumes\n"
                "2. Consider IBM MQ on Cloud for managed service\n"
                "3. For event-driven: migrate to Event Streams (Kafka)\n"
                "4. Update client libraries to latest versions\n"
                "5. Implement monitoring and observability"
            ),
            "Db2 Legacy": (
                "1. Assess database schema and queries\n"
                "2. Upgrade to latest Db2 version\n"
                "3. Consider Db2 on Cloud for managed service\n"
                "4. Optimize for cloud deployment\n"
                "5. Implement connection pooling and caching"
            ),
            "CICS": (
                "1. Analyze CICS transactions and programs\n"
                "2. Consider CICS TS for z/OS Cloud\n"
                "3. Evaluate microservices decomposition\n"
                "4. Use IBM CICS Transaction Gateway for integration\n"
                "5. Modernize UI with modern frameworks"
            ),
            "IMS": (
                "1. Assess IMS database and transaction workloads\n"
                "2. Consider IMS on Cloud\n"
                "3. Evaluate data migration to modern databases\n"
                "4. Implement API layer for IMS access\n"
                "5. Plan phased migration strategy"
            ),
        }
        
        return guidance.get(legacy_tech, "Consult IBM modernization documentation")

    def _generate_summary(self, findings: list[dict[str, Any]]) -> str:
        """Generate a summary of modernization findings."""
        if not findings:
            return "No modernization opportunities identified"
        
        legacy_count = len([f for f in findings if f.get("type") == "legacy_technology"])
        cloud_native_count = len([f for f in findings if f.get("type") == "cloud_native_opportunity"])
        high_priority = len([f for f in findings if f.get("priority") == "high"])
        
        summary_parts = [f"Found {len(findings)} modernization opportunity(ies)"]
        
        if legacy_count > 0:
            summary_parts.append(f"{legacy_count} legacy technology(ies) detected")
        
        if cloud_native_count > 0:
            summary_parts.append(f"{cloud_native_count} cloud-native improvement(s) suggested")
        
        if high_priority > 0:
            summary_parts.append(f"{high_priority} high-priority item(s)")
        
        return ". ".join(summary_parts)

# Made with Bob