"""Infrastructure Agent for OpenShift and Kubernetes Configuration Review."""

from __future__ import annotations

import logging
from typing import Any

from app.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class InfrastructureAgent(BaseAgent):
    """
    Specialized agent for infrastructure-as-code review.
    
    This agent focuses on OpenShift, Kubernetes, and IBM Cloud
    infrastructure configurations, ensuring best practices for
    deployment, security, and resource management.
    """

    agent_name = "infrastructure-agent"
    category = "infrastructure"

    def __init__(self) -> None:
        """Initialize the infrastructure agent."""
        self.k8s_resource_types = [
            "Deployment", "StatefulSet", "DaemonSet", "Pod",
            "Service", "Ingress", "Route", "ConfigMap", "Secret",
            "PersistentVolumeClaim", "NetworkPolicy",
        ]

    async def analyze(
        self,
        pull_request: dict[str, Any],
        diffs: list[dict[str, Any]],
        context: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Analyze PR for infrastructure configuration issues.
        
        Args:
            pull_request: PR metadata
            diffs: Code changes
            context: Additional context
            
        Returns:
            Structured findings with infrastructure recommendations
        """
        findings: list[dict[str, Any]] = []
        
        # Check Kubernetes/OpenShift manifests
        k8s_findings = await self._check_kubernetes_manifests(diffs)
        findings.extend(k8s_findings)
        
        # Check Helm charts
        helm_findings = await self._check_helm_charts(diffs)
        findings.extend(helm_findings)
        
        # Check Terraform/IaC
        iac_findings = await self._check_infrastructure_as_code(diffs)
        findings.extend(iac_findings)
        
        # Check OpenShift specific
        openshift_findings = await self._check_openshift_specific(diffs)
        findings.extend(openshift_findings)
        
        summary = self._generate_summary(findings)
        
        return self.format_result(
            summary=summary,
            findings=findings,
            metadata={
                "total_issues": len(findings),
                "security_issues": len([f for f in findings if f.get("category") == "security"]),
                "resource_issues": len([f for f in findings if f.get("category") == "resources"]),
            },
        )

    async def _check_kubernetes_manifests(
        self,
        diffs: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Check Kubernetes manifest files."""
        findings = []
        
        for diff in diffs:
            file_path = diff.get("path", "")
            content = diff.get("content", "")
            
            # Check if it's a K8s manifest
            if not (file_path.endswith((".yaml", ".yml")) and "kind:" in content):
                continue
            
            # Check for resource limits
            if "Deployment" in content or "StatefulSet" in content or "Pod" in content:
                if "resources:" not in content:
                    findings.append({
                        "type": "kubernetes_best_practice",
                        "category": "resources",
                        "severity": "high",
                        "file": file_path,
                        "message": "Missing resource limits and requests",
                        "description": "Containers should define resource limits and requests",
                        "remediation": "Add resources.limits and resources.requests to container spec",
                        "example": "resources:\n  limits:\n    cpu: 500m\n    memory: 512Mi\n  requests:\n    cpu: 250m\n    memory: 256Mi",
                    })
                
                # Check for liveness and readiness probes
                if "livenessProbe:" not in content:
                    findings.append({
                        "type": "kubernetes_best_practice",
                        "category": "reliability",
                        "severity": "medium",
                        "file": file_path,
                        "message": "Missing liveness probe",
                        "description": "Containers should have liveness probes for health monitoring",
                        "remediation": "Add livenessProbe to container spec",
                    })
                
                if "readinessProbe:" not in content:
                    findings.append({
                        "type": "kubernetes_best_practice",
                        "category": "reliability",
                        "severity": "medium",
                        "file": file_path,
                        "message": "Missing readiness probe",
                        "description": "Containers should have readiness probes for traffic management",
                        "remediation": "Add readinessProbe to container spec",
                    })
            
            # Check for security context
            if "securityContext:" not in content:
                findings.append({
                    "type": "kubernetes_security",
                    "category": "security",
                    "severity": "high",
                    "file": file_path,
                    "message": "Missing security context",
                    "description": "Pods should define security context for least privilege",
                    "remediation": "Add securityContext with runAsNonRoot, readOnlyRootFilesystem, etc.",
                    "example": "securityContext:\n  runAsNonRoot: true\n  runAsUser: 1000\n  readOnlyRootFilesystem: true",
                })
            
            # Check for privileged containers
            if "privileged: true" in content:
                findings.append({
                    "type": "kubernetes_security",
                    "category": "security",
                    "severity": "critical",
                    "file": file_path,
                    "message": "Privileged container detected",
                    "description": "Privileged containers have full host access and should be avoided",
                    "remediation": "Remove privileged: true or justify with security review",
                })
            
            # Check for host network/PID/IPC
            if any(x in content for x in ["hostNetwork: true", "hostPID: true", "hostIPC: true"]):
                findings.append({
                    "type": "kubernetes_security",
                    "category": "security",
                    "severity": "high",
                    "file": file_path,
                    "message": "Host namespace sharing detected",
                    "description": "Sharing host namespaces reduces isolation and security",
                    "remediation": "Avoid hostNetwork, hostPID, and hostIPC unless absolutely necessary",
                })
            
            # Check for image pull policy
            if "image:" in content and "imagePullPolicy:" not in content:
                findings.append({
                    "type": "kubernetes_best_practice",
                    "category": "reliability",
                    "severity": "low",
                    "file": file_path,
                    "message": "Missing imagePullPolicy",
                    "description": "Explicit imagePullPolicy ensures consistent behavior",
                    "remediation": "Add imagePullPolicy: Always or IfNotPresent",
                })
            
            # Check for latest tag
            if 'image:' in content and ':latest' in content:
                findings.append({
                    "type": "kubernetes_best_practice",
                    "category": "reliability",
                    "severity": "medium",
                    "file": file_path,
                    "message": "Using 'latest' image tag",
                    "description": "Using 'latest' tag can lead to inconsistent deployments",
                    "remediation": "Use specific version tags for images",
                })
        
        return findings

    async def _check_helm_charts(
        self,
        diffs: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Check Helm chart configurations."""
        findings = []
        
        for diff in diffs:
            file_path = diff.get("path", "")
            content = diff.get("content", "")
            
            # Check Chart.yaml
            if file_path.endswith("Chart.yaml"):
                if "version:" not in content:
                    findings.append({
                        "type": "helm_best_practice",
                        "category": "versioning",
                        "severity": "high",
                        "file": file_path,
                        "message": "Missing chart version",
                        "description": "Helm charts must have a version",
                        "remediation": "Add version field to Chart.yaml",
                    })
                
                if "appVersion:" not in content:
                    findings.append({
                        "type": "helm_best_practice",
                        "category": "versioning",
                        "severity": "medium",
                        "file": file_path,
                        "message": "Missing app version",
                        "description": "Chart should specify application version",
                        "remediation": "Add appVersion field to Chart.yaml",
                    })
            
            # Check values.yaml
            if file_path.endswith("values.yaml"):
                if "resources:" in content and "limits:" not in content:
                    findings.append({
                        "type": "helm_best_practice",
                        "category": "resources",
                        "severity": "medium",
                        "file": file_path,
                        "message": "Default values missing resource limits",
                        "description": "Helm values should include default resource limits",
                        "remediation": "Add default resource limits to values.yaml",
                    })
        
        return findings

    async def _check_infrastructure_as_code(
        self,
        diffs: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Check Terraform and other IaC files."""
        findings = []
        
        for diff in diffs:
            file_path = diff.get("path", "")
            content = diff.get("content", "")
            
            # Check Terraform files
            if file_path.endswith(".tf"):
                # Check for hardcoded credentials
                if any(keyword in content.lower() for keyword in ["password", "secret", "api_key"]):
                    if "=" in content and "var." not in content:
                        findings.append({
                            "type": "iac_security",
                            "category": "security",
                            "severity": "critical",
                            "file": file_path,
                            "message": "Potential hardcoded credentials in Terraform",
                            "description": "Credentials should never be hardcoded in IaC",
                            "remediation": "Use Terraform variables or secrets management",
                        })
                
                # Check for state backend configuration
                if "terraform {" in content and "backend" not in content:
                    findings.append({
                        "type": "iac_best_practice",
                        "category": "state_management",
                        "severity": "high",
                        "file": file_path,
                        "message": "Missing remote state backend",
                        "description": "Terraform should use remote state for team collaboration",
                        "remediation": "Configure remote backend (S3, IBM Cloud Object Storage, etc.)",
                    })
                
                # Check for resource tagging
                if "resource " in content and "tags" not in content:
                    findings.append({
                        "type": "iac_best_practice",
                        "category": "resource_management",
                        "severity": "low",
                        "file": file_path,
                        "message": "Resources missing tags",
                        "description": "Resources should be tagged for cost tracking and management",
                        "remediation": "Add tags to resources (environment, owner, project, etc.)",
                    })
        
        return findings

    async def _check_openshift_specific(
        self,
        diffs: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Check OpenShift-specific configurations."""
        findings = []
        
        for diff in diffs:
            file_path = diff.get("path", "")
            content = diff.get("content", "")
            
            # Check for OpenShift Routes
            if "kind: Route" in content:
                if "tls:" not in content:
                    findings.append({
                        "type": "openshift_security",
                        "category": "security",
                        "severity": "high",
                        "file": file_path,
                        "message": "Route without TLS configuration",
                        "description": "OpenShift Routes should use TLS for secure communication",
                        "remediation": "Add TLS configuration to Route",
                        "example": "tls:\n  termination: edge\n  insecureEdgeTerminationPolicy: Redirect",
                    })
            
            # Check for DeploymentConfig (legacy)
            if "kind: DeploymentConfig" in content:
                findings.append({
                    "type": "openshift_modernization",
                    "category": "modernization",
                    "severity": "low",
                    "file": file_path,
                    "message": "Using DeploymentConfig (legacy)",
                    "description": "DeploymentConfig is OpenShift-specific, consider using Deployment",
                    "remediation": "Migrate to standard Kubernetes Deployment for portability",
                })
            
            # Check for BuildConfig
            if "kind: BuildConfig" in content:
                if "strategy:" in content and "dockerStrategy:" in content:
                    if "FROM" not in content and "dockerfile:" not in content:
                        findings.append({
                            "type": "openshift_best_practice",
                            "category": "build",
                            "severity": "medium",
                            "file": file_path,
                            "message": "BuildConfig missing Dockerfile reference",
                            "description": "Docker strategy should reference a Dockerfile",
                            "remediation": "Add dockerfilePath or inline Dockerfile",
                        })
            
            # Check for SecurityContextConstraints
            if "kind: SecurityContextConstraints" in content:
                if "allowPrivilegedContainer: true" in content:
                    findings.append({
                        "type": "openshift_security",
                        "category": "security",
                        "severity": "critical",
                        "file": file_path,
                        "message": "SCC allows privileged containers",
                        "description": "Allowing privileged containers is a security risk",
                        "remediation": "Restrict privileged container access or justify with security review",
                    })
        
        return findings

    def _generate_summary(self, findings: list[dict[str, Any]]) -> str:
        """Generate a summary of infrastructure findings."""
        if not findings:
            return "No infrastructure configuration issues detected"
        
        by_category = {}
        for finding in findings:
            category = finding.get("category", "other")
            by_category[category] = by_category.get(category, 0) + 1
        
        critical = len([f for f in findings if f.get("severity") == "critical"])
        high = len([f for f in findings if f.get("severity") == "high"])
        
        summary_parts = [f"Found {len(findings)} infrastructure issue(s)"]
        
        if critical > 0:
            summary_parts.append(f"{critical} critical issue(s)")
        if high > 0:
            summary_parts.append(f"{high} high severity issue(s)")
        
        category_summary = ", ".join(f"{count} {cat}" for cat, count in by_category.items())
        summary_parts.append(f"Categories: {category_summary}")
        
        return ". ".join(summary_parts)

# Made with Bob