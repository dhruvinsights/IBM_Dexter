"""IBM Ecosystem Service for IBM Product Intelligence."""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ibm_ecosystem_context import (
    IBMBestPracticeViolation,
    IBMEcosystemContext,
    IBMProductDetection,
)

logger = logging.getLogger(__name__)


class IBMEcosystemService:
    """
    Service for managing IBM ecosystem intelligence.
    
    This service enables Dexter to detect IBM products, provide
    product-specific recommendations, and enforce IBM best practices.
    """

    # IBM product detection patterns
    PRODUCT_PATTERNS = {
        "OpenShift": [
            r"openshift",
            r"oc\s+(?:login|project|apply)",
            r"kind:\s*(?:Route|DeploymentConfig|BuildConfig)",
        ],
        "WebSphere": [
            r"websphere",
            r"was\.install",
            r"com\.ibm\.websphere",
        ],
        "Liberty": [
            r"liberty",
            r"server\.xml",
            r"com\.ibm\.ws",
        ],
        "Db2": [
            r"db2",
            r"jdbc:db2:",
            r"com\.ibm\.db2",
        ],
        "MQ": [
            r"ibm\.mq",
            r"wmq",
            r"com\.ibm\.mq",
        ],
        "Watsonx": [
            r"watsonx",
            r"watson\.ai",
            r"ibm\.watson",
        ],
        "Cloud Pak": [
            r"cloudpak",
            r"cp4[a-z]",
        ],
    }

    async def create_product_context(
        self,
        db: AsyncSession,
        product_name: str,
        product_family: str,
        product_type: str,
        version: str,
        version_family: str,
        recommended_configurations: dict[str, Any] | None = None,
        best_practices: list[dict[str, Any]] | None = None,
        known_issues: list[dict[str, Any]] | None = None,
        migration_paths: dict[str, Any] | None = None,
        is_latest_version: bool = False,
        is_supported: bool = True,
    ) -> IBMEcosystemContext:
        """
        Create or update IBM product context.
        
        Args:
            db: Database session
            product_name: IBM product name
            product_family: Product family
            product_type: Product type
            version: Product version
            version_family: Version family
            recommended_configurations: Recommended configs
            best_practices: Best practices list
            known_issues: Known issues list
            migration_paths: Migration paths
            is_latest_version: Whether this is latest version
            is_supported: Whether version is supported
            
        Returns:
            Created IBMEcosystemContext instance
        """
        context = IBMEcosystemContext(
            product_name=product_name,
            product_family=product_family,
            product_type=product_type,
            version=version,
            version_family=version_family,
            is_latest_version=is_latest_version,
            is_supported=is_supported,
            recommended_configurations=recommended_configurations or {},
            best_practices=best_practices or [],
            known_issues=known_issues or [],
            migration_paths=migration_paths or {},
        )
        
        db.add(context)
        await db.commit()
        await db.refresh(context)
        
        logger.info(
            "Created IBM product context: %s %s",
            product_name,
            version,
        )
        
        return context

    async def get_product_context(
        self,
        db: AsyncSession,
        product_name: str,
        version: Optional[str] = None,
    ) -> Optional[IBMEcosystemContext]:
        """
        Get IBM product context.
        
        Args:
            db: Database session
            product_name: Product name
            version: Specific version (optional)
            
        Returns:
            IBMEcosystemContext instance or None
        """
        query = select(IBMEcosystemContext).where(
            IBMEcosystemContext.product_name == product_name
        )
        
        if version:
            query = query.where(IBMEcosystemContext.version == version)
        else:
            # Get latest version if not specified
            query = query.where(IBMEcosystemContext.is_latest_version == True)
        
        query = query.where(IBMEcosystemContext.is_active == True)
        
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def detect_ibm_products(
        self,
        db: AsyncSession,
        repository_id: int,
        files: list[dict[str, Any]],
    ) -> list[IBMProductDetection]:
        """
        Detect IBM products in repository files.
        
        Args:
            db: Database session
            repository_id: Repository to scan
            files: List of file dictionaries with 'path' and 'content'
            
        Returns:
            List of detected IBM products
        """
        detections = []
        detected_products = {}
        
        for file_info in files:
            file_path = file_info.get("path", "")
            content = file_info.get("content", "")
            
            for product_name, patterns in self.PRODUCT_PATTERNS.items():
                for pattern in patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        if product_name not in detected_products:
                            detected_products[product_name] = {
                                "files": [],
                                "evidence": [],
                            }
                        
                        detected_products[product_name]["files"].append(file_path)
                        detected_products[product_name]["evidence"].append({
                            "pattern": pattern,
                            "file": file_path,
                        })
        
        # Create detection records
        for product_name, detection_info in detected_products.items():
            detection = await self._create_or_update_detection(
                db=db,
                repository_id=repository_id,
                product_name=product_name,
                detected_files=detection_info["files"],
                evidence=detection_info["evidence"],
            )
            detections.append(detection)
        
        logger.info(
            "Detected %d IBM products in repository %d",
            len(detections),
            repository_id,
        )
        
        return detections

    async def _create_or_update_detection(
        self,
        db: AsyncSession,
        repository_id: int,
        product_name: str,
        detected_files: list[str],
        evidence: list[dict[str, Any]],
    ) -> IBMProductDetection:
        """Create or update product detection record."""
        # Check if detection exists
        query = select(IBMProductDetection).where(
            and_(
                IBMProductDetection.repository_id == repository_id,
                IBMProductDetection.product_name == product_name,
                IBMProductDetection.is_active == True,
            )
        )
        result = await db.execute(query)
        detection = result.scalar_one_or_none()
        
        if detection:
            # Update existing detection
            detection.detected_in_files = list(set(detection.detected_in_files + detected_files))
            detection.detection_evidence = {
                "patterns": evidence,
                "confidence": 0.9,
            }
        else:
            # Create new detection
            detection = IBMProductDetection(
                repository_id=repository_id,
                product_name=product_name,
                detection_method="code_pattern",
                detection_confidence=0.9,
                detected_in_files=detected_files,
                detection_evidence={"patterns": evidence},
            )
            db.add(detection)
        
        await db.commit()
        await db.refresh(detection)
        
        return detection

    async def get_repository_products(
        self,
        db: AsyncSession,
        repository_id: int,
        is_active: bool = True,
    ) -> list[IBMProductDetection]:
        """
        Get all IBM products detected in a repository.
        
        Args:
            db: Database session
            repository_id: Repository ID
            is_active: Filter by active status
            
        Returns:
            List of IBMProductDetection instances
        """
        query = select(IBMProductDetection).where(
            IBMProductDetection.repository_id == repository_id
        )
        
        if is_active is not None:
            query = query.where(IBMProductDetection.is_active == is_active)
        
        result = await db.execute(query)
        return list(result.scalars().all())

    async def record_best_practice_violation(
        self,
        db: AsyncSession,
        repository_id: int,
        product_name: str,
        violation_type: str,
        best_practice_id: str,
        best_practice_title: str,
        violation_description: str,
        file_path: str,
        remediation_guidance: str,
        severity: str = "medium",
        pull_request_id: Optional[int] = None,
        review_id: Optional[int] = None,
        line_number: Optional[int] = None,
        code_snippet: Optional[str] = None,
    ) -> IBMBestPracticeViolation:
        """
        Record an IBM best practice violation.
        
        Args:
            db: Database session
            repository_id: Repository where violation occurred
            product_name: IBM product related to violation
            violation_type: Type of violation
            best_practice_id: ID of violated best practice
            best_practice_title: Title of best practice
            violation_description: Description of violation
            file_path: File where violation was found
            remediation_guidance: How to fix
            severity: Severity level
            pull_request_id: PR where detected
            review_id: Review where detected
            line_number: Line number
            code_snippet: Code snippet
            
        Returns:
            Created IBMBestPracticeViolation instance
        """
        violation = IBMBestPracticeViolation(
            repository_id=repository_id,
            pull_request_id=pull_request_id,
            review_id=review_id,
            product_name=product_name,
            violation_type=violation_type,
            best_practice_id=best_practice_id,
            best_practice_title=best_practice_title,
            violation_description=violation_description,
            file_path=file_path,
            line_number=line_number,
            code_snippet=code_snippet,
            severity=severity,
            remediation_guidance=remediation_guidance,
        )
        
        db.add(violation)
        await db.commit()
        await db.refresh(violation)
        
        logger.info(
            "Recorded IBM best practice violation: %s in %s",
            best_practice_title,
            file_path,
        )
        
        return violation

    async def get_best_practice_violations(
        self,
        db: AsyncSession,
        repository_id: Optional[int] = None,
        product_name: Optional[str] = None,
        status: str = "open",
        severity: Optional[str] = None,
        limit: int = 100,
    ) -> List[IBMBestPracticeViolation]:
        """
        Get IBM best practice violations.
        
        Args:
            db: Database session
            repository_id: Filter by repository
            product_name: Filter by product
            status: Filter by status
            severity: Filter by severity
            limit: Maximum results
            
        Returns:
            List of IBMBestPracticeViolation instances
        """
        query = select(IBMBestPracticeViolation)
        
        conditions = []
        if repository_id:
            conditions.append(IBMBestPracticeViolation.repository_id == repository_id)
        if product_name:
            conditions.append(IBMBestPracticeViolation.product_name == product_name)
        if status:
            conditions.append(IBMBestPracticeViolation.status == status)
        if severity:
            conditions.append(IBMBestPracticeViolation.severity == severity)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(desc(IBMBestPracticeViolation.created_at)).limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_modernization_recommendations(
        self,
        db: AsyncSession,
        repository_id: int,
    ) -> dict[str, Any]:
        """
        Get modernization recommendations for a repository.
        
        Args:
            db: Database session
            repository_id: Repository to analyze
            
        Returns:
            Dictionary with modernization recommendations
        """
        # Get detected products
        products = await self.get_repository_products(db, repository_id)
        
        recommendations = {
            "repository_id": repository_id,
            "detected_products": [],
            "modernization_opportunities": [],
            "priority_actions": [],
        }
        
        for product in products:
            product_info = {
                "product_name": product.product_name,
                "is_legacy": product.is_legacy,
                "needs_modernization": product.needs_modernization,
                "priority": product.modernization_priority,
            }
            
            recommendations["detected_products"].append(product_info)
            
            if product.needs_modernization:
                # Get product context for migration paths
                context = await self.get_product_context(
                    db=db,
                    product_name=product.product_name,
                )
                
                if context and context.migration_paths:
                    recommendations["modernization_opportunities"].append({
                        "product": product.product_name,
                        "current_version": product.detected_version,
                        "migration_paths": context.migration_paths,
                        "priority": product.modernization_priority,
                    })
                
                if product.modernization_priority in ["critical", "high"]:
                    recommendations["priority_actions"].extend(product.recommendations)
        
        return recommendations

    async def validate_configuration(
        self,
        db: AsyncSession,
        product_name: str,
        configuration: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Validate IBM product configuration against best practices.
        
        Args:
            db: Database session
            product_name: IBM product name
            configuration: Configuration to validate
            
        Returns:
            Validation results dictionary
        """
        context = await self.get_product_context(db, product_name)
        
        if not context:
            return {
                "valid": False,
                "error": f"No context found for product: {product_name}",
            }
        
        validation_results = {
            "product": product_name,
            "valid": True,
            "warnings": [],
            "errors": [],
            "recommendations": [],
        }
        
        # Check against recommended configurations
        recommended = context.recommended_configurations
        for key, recommended_value in recommended.items():
            if key in configuration:
                actual_value = configuration[key]
                if actual_value != recommended_value:
                    validation_results["warnings"].append({
                        "setting": key,
                        "actual": actual_value,
                        "recommended": recommended_value,
                        "message": f"Configuration differs from recommended value",
                    })
        
        # Check security configurations
        security_configs = context.security_configurations
        for key, required_value in security_configs.items():
            if key not in configuration:
                validation_results["errors"].append({
                    "setting": key,
                    "message": f"Required security setting missing",
                    "required_value": required_value,
                })
                validation_results["valid"] = False
        
        # Add best practices as recommendations
        for practice in context.best_practices:
            validation_results["recommendations"].append({
                "title": practice.get("title"),
                "description": practice.get("description"),
                "category": practice.get("category"),
            })
        
        return validation_results

    async def get_product_intelligence(
        self,
        db: AsyncSession,
        repository_id: int,
    ) -> dict[str, Any]:
        """
        Get comprehensive IBM product intelligence for a repository.
        
        Args:
            db: Database session
            repository_id: Repository to analyze
            
        Returns:
            Intelligence summary dictionary
        """
        # Get detected products
        products = await self.get_repository_products(db, repository_id)
        
        # Get violations
        violations = await self.get_best_practice_violations(
            db=db,
            repository_id=repository_id,
            status="open",
        )
        
        # Get modernization recommendations
        modernization = await self.get_modernization_recommendations(
            db=db,
            repository_id=repository_id,
        )
        
        intelligence = {
            "repository_id": repository_id,
            "detected_products": [
                {
                    "name": p.product_name,
                    "version": p.detected_version,
                    "is_legacy": p.is_legacy,
                    "needs_modernization": p.needs_modernization,
                    "files": p.detected_in_files,
                }
                for p in products
            ],
            "open_violations": len(violations),
            "violations_by_severity": {},
            "violations_by_product": {},
            "modernization": modernization,
        }
        
        # Aggregate violations
        for violation in violations:
            # By severity
            severity = violation.severity
            intelligence["violations_by_severity"][severity] = (
                intelligence["violations_by_severity"].get(severity, 0) + 1
            )
            
            # By product
            product = violation.product_name
            intelligence["violations_by_product"][product] = (
                intelligence["violations_by_product"].get(product, 0) + 1
            )
        
        return intelligence

# Made with Bob