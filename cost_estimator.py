"""
Cost Estimator Module
Calculates project costs using a COCOMO-based estimation model
while keeping the existing output structure compatible with the app.
"""

from typing import Dict, List
from dataclasses import dataclass, field
import math
from datetime import datetime, timedelta

from feature_extractor import ExtractedFeatures
from config import (
    DEVELOPMENT_PHASES,
    DEFAULT_BUFFER_PERCENTAGE,
    COCOMO_COST_PER_PERSON_MONTH,
    COCOMO_COEFFICIENTS,
    COCOMO_EAF_FACTORS
)


@dataclass
class CostBreakdown:
    """Detailed cost breakdown"""
    base_cost: float = 0.0
    feature_cost: float = 0.0
    complexity_cost: float = 0.0
    platform_cost: float = 0.0
    ui_cost: float = 0.0
    integration_cost: float = 0.0
    testing_cost: float = 0.0
    project_management_cost: float = 0.0
    buffer_cost: float = 0.0
    total_cost: float = 0.0

    feature_breakdown: List[Dict] = field(default_factory=list)
    integration_breakdown: List[Dict] = field(default_factory=list)
    phase_breakdown: Dict[str, float] = field(default_factory=dict)

    complexity_multiplier: float = 1.0
    platform_multiplier: float = 1.0
    ui_multiplier: float = 1.0

    cost_per_feature: float = 0.0
    cost_per_module: float = 0.0


@dataclass
class TimelineEstimate:
    """Timeline estimation"""
    total_weeks: int = 0
    total_days: int = 0
    total_months: float = 0.0
    phases: Dict[str, int] = field(default_factory=dict)
    milestones: List[Dict] = field(default_factory=list)
    estimated_start: str = ""
    estimated_end: str = ""


@dataclass
class ProjectEstimate:
    """Complete project estimate"""
    cost: CostBreakdown = field(default_factory=CostBreakdown)
    timeline: TimelineEstimate = field(default_factory=TimelineEstimate)

    total_cost_inr: float = 0.0
    total_cost_formatted: str = ""
    timeline_weeks: int = 0

    estimation_confidence: float = 0.0
    risk_level: str = "medium"
    risk_factors: List[str] = field(default_factory=list)

    # COCOMO-specific fields
    estimated_kloc: float = 0.0
    effort_person_months: float = 0.0
    cocomo_mode: str = "organic"
    effort_adjustment_factor: float = 1.0


class CostEstimator:
    """
    COCOMO-based cost estimator.
    """

    def __init__(
        self,
        cost_per_person_month: float = COCOMO_COST_PER_PERSON_MONTH,
        buffer_percentage: float = DEFAULT_BUFFER_PERCENTAGE
    ):
        self.cost_per_person_month = cost_per_person_month
        self.buffer_percentage = buffer_percentage

    def estimate(self, features: ExtractedFeatures) -> ProjectEstimate:
        result = ProjectEstimate()

        kloc = kloc = max(min(self._estimate_kloc(features) / 1000.0, 25.0), 3.0)  
        mode = self._determine_cocomo_mode(features)
        eaf = self._calculate_eaf(features)
        eaf = min(max(eaf, 0.9), 1.2)
        effort_pm = self._calculate_effort_person_months(kloc, mode, eaf)

        result.estimated_kloc = kloc
        result.cocomo_mode = mode
        result.effort_adjustment_factor = eaf
        result.effort_person_months = effort_pm

        result.cost = self._calculate_cost(features, kloc, mode, eaf, effort_pm)
        result.timeline = self._calculate_timeline(features, mode, effort_pm)

        result.total_cost_inr = result.cost.total_cost
        result.total_cost_formatted = self._format_inr(result.cost.total_cost)
        result.timeline_weeks = result.timeline.total_weeks
        result.estimation_confidence = features.extraction_confidence

        risk_info = self._assess_risks(features, kloc, eaf)
        result.risk_level = risk_info["level"]
        result.risk_factors = risk_info["factors"]

        return result

    def _estimate_kloc(self, features: ExtractedFeatures) -> float:
        feature_count = max(len(features.features), 5)
        module_count = max(len(features.modules), 1)
        integration_count = len(features.integrations)

        complexity_weights = {
            "low": 0.8,
            "medium": 1.2,
            "high": 1.8,
            "very_high": 2.5
        }

        platform_weights = {
            "web": 1.0,
            "mobile_android": 1.1,
            "mobile_ios": 1.1,
            "mobile_both": 1.4,
            "web_and_mobile": 1.6,
            "desktop": 1.0,
            "cross_platform": 1.5
        }

        ui_weights = {
            "basic": 0.9,
            "standard": 1.0,
            "advanced": 1.15,
            "premium": 1.3,
            "custom": 1.45
        }

        complexity_factor = complexity_weights.get(features.complexity, 1.2)
        platform_factor = platform_weights.get(features.platform, 1.0)
        ui_factor = ui_weights.get(features.ui_complexity, 1.0)

        estimated_loc = (
            feature_count * 250 +
            module_count * 500 +
            integration_count * 800
        )

        estimated_loc *= complexity_factor
        estimated_loc *= platform_factor
        estimated_loc *= ui_factor

        return max(estimated_loc / 1000.0, 2.0)

    def _determine_cocomo_mode(self, features: ExtractedFeatures) -> str:
        if (
            features.complexity == "very_high"
            or features.estimated_scope == "enterprise"
            or "ai_ml_integration" in features.integrations
            or "blockchain" in features.integrations
        ):
            return "embedded"

        if (
            features.complexity == "high"
            or features.platform in ["web_and_mobile", "cross_platform", "mobile_both"]
            or len(features.integrations) >= 4
        ):
            return "semi_detached"

        return "organic"

    def _calculate_eaf(self, features: ExtractedFeatures) -> float:
        eaf = 1.0

        reliability_level = "nominal"
        if "payment_gateway" in features.integrations or "authentication_oauth" in features.integrations:
            reliability_level = "high"
        if features.complexity == "very_high":
            reliability_level = "very_high"
        eaf *= COCOMO_EAF_FACTORS["required_reliability"][reliability_level]

        product_complexity_level = "nominal"
        if features.complexity == "high":
            product_complexity_level = "high"
        elif features.complexity == "very_high":
            product_complexity_level = "very_high"
        elif features.complexity == "low":
            product_complexity_level = "low"
        eaf *= COCOMO_EAF_FACTORS["product_complexity"][product_complexity_level]

        platform_level = "nominal"
        if features.platform in ["web_and_mobile", "cross_platform", "mobile_both"]:
            platform_level = "high"
        if features.platform == "cross_platform":
            platform_level = "very_high"
        eaf *= COCOMO_EAF_FACTORS["platform_complexity"][platform_level]

        eaf *= COCOMO_EAF_FACTORS["team_experience"]["nominal"]

        return eaf

    def _calculate_effort_person_months(self, kloc: float, mode: str, eaf: float) -> float:
        coeff = COCOMO_COEFFICIENTS[mode]
        return coeff["a"] * (kloc ** coeff["b"]) * eaf

    def _calculate_schedule_months(self, effort_pm: float, mode: str) -> float:
        coeff = COCOMO_COEFFICIENTS[mode]
        return coeff["c"] * (effort_pm ** coeff["d"])

    def _calculate_cost(
        self,
        features: ExtractedFeatures,
        kloc: float,
        mode: str,
        eaf: float,
        effort_pm: float
    ) -> CostBreakdown:
        breakdown = CostBreakdown()

        core_dev_cost = effort_pm * self.cost_per_person_month

        feature_count = max(len(features.features), 1)
        module_count = max(len(features.modules), 1)

        breakdown.base_cost = core_dev_cost

        breakdown.feature_cost = core_dev_cost * 0.45
        breakdown.platform_cost = core_dev_cost * self._platform_cost_share(features)
        breakdown.ui_cost = core_dev_cost * self._ui_cost_share(features)
        breakdown.integration_cost = core_dev_cost * self._integration_cost_share(features)

        subtotal = (
            breakdown.feature_cost
            + breakdown.platform_cost
            + breakdown.ui_cost
            + breakdown.integration_cost
        )

        breakdown.testing_cost = subtotal * 0.20
        breakdown.project_management_cost = subtotal * 0.10
        breakdown.buffer_cost = subtotal * (self.buffer_percentage / 100.0)

        breakdown.total_cost = (
            subtotal
            + breakdown.testing_cost
            + breakdown.project_management_cost
            + breakdown.buffer_cost
        )

        breakdown.complexity_cost = max(core_dev_cost - subtotal, 0)
        breakdown.complexity_multiplier = eaf
        breakdown.platform_multiplier = 1.0 + self._platform_cost_share(features)
        breakdown.ui_multiplier = 1.0 + self._ui_cost_share(features)

        breakdown.cost_per_feature = breakdown.total_cost / feature_count
        breakdown.cost_per_module = breakdown.total_cost / module_count

        per_feature_cost = breakdown.feature_cost / feature_count
        if features.features:
            for feature in features.features:
                breakdown.feature_breakdown.append({
                    "description": feature.get("description", "")[:60],
                    "complexity": feature.get("complexity", "medium"),
                    "cost": per_feature_cost
                })

        if features.integrations:
            per_integration_cost = breakdown.integration_cost / len(features.integrations)
            for integration in features.integrations:
                breakdown.integration_breakdown.append({
                    "name": integration.replace("_", " ").title(),
                    "cost": per_integration_cost
                })

        for phase, percentage in DEVELOPMENT_PHASES.items():
            breakdown.phase_breakdown[phase] = breakdown.total_cost * percentage

        return breakdown

    def _calculate_timeline(
        self,
        features: ExtractedFeatures,
        mode: str,
        effort_pm: float
    ) -> TimelineEstimate:
        timeline = TimelineEstimate()

        schedule_months = self._calculate_schedule_months(effort_pm, mode)
        total_weeks = max(4, math.ceil(schedule_months * 4.33))

        timeline.total_weeks = total_weeks
        timeline.total_days = total_weeks * 5
        timeline.total_months = schedule_months

        phases = {}
        allocated = 0
        phase_items = list(DEVELOPMENT_PHASES.items())

        for i, (phase, pct) in enumerate(phase_items):
            if i < len(phase_items) - 1:
                weeks = max(1, round(total_weeks * pct))
                phases[phase] = weeks
                allocated += weeks
            else:
                phases[phase] = max(1, total_weeks - allocated)

        timeline.phases = phases

        phase_names = {
            "requirement_analysis": "Requirements Sign-off",
            "design": "Design Approval",
            "development": "Development Complete",
            "testing": "QA Sign-off",
            "deployment": "Go Live",
            "buffer": "Project Closure"
        }

        current_week = 0
        for phase, weeks in phases.items():
            current_week += weeks
            timeline.milestones.append({
                "name": phase_names.get(phase, phase.replace("_", " ").title()),
                "week": current_week,
                "description": f"Complete by week {current_week}"
            })

        start_date = datetime.now()
        end_date = start_date + timedelta(weeks=total_weeks)
        timeline.estimated_start = start_date.strftime("%Y-%m-%d")
        timeline.estimated_end = end_date.strftime("%Y-%m-%d")

        return timeline

    def _platform_cost_share(self, features: ExtractedFeatures) -> float:
        mapping = {
            "web": 0.05,
            "mobile_android": 0.08,
            "mobile_ios": 0.08,
            "mobile_both": 0.14,
            "web_and_mobile": 0.18,
            "desktop": 0.06,
            "cross_platform": 0.16
        }
        return mapping.get(features.platform, 0.05)

    def _ui_cost_share(self, features: ExtractedFeatures) -> float:
        mapping = {
            "basic": 0.04,
            "standard": 0.08,
            "advanced": 0.12,
            "premium": 0.18,
            "custom": 0.22
        }
        return mapping.get(features.ui_complexity, 0.08)

    def _integration_cost_share(self, features: ExtractedFeatures) -> float:
        if not features.integrations:
            return 0.05
        return min(0.08 + (0.03 * len(features.integrations)), 0.30)

    def _assess_risks(self, features: ExtractedFeatures, kloc: float, eaf: float) -> Dict:
        risk_score = 0
        risk_factors = []

        if kloc > 50:
            risk_score += 3
            risk_factors.append(f"Large estimated codebase ({kloc:.1f} KLOC)")
        elif kloc > 20:
            risk_score += 2
            risk_factors.append(f"Moderate-to-large estimated codebase ({kloc:.1f} KLOC)")

        if features.complexity in ["high", "very_high"]:
            risk_score += 3
            risk_factors.append(f"High complexity level: {features.complexity}")

        if features.platform in ["web_and_mobile", "cross_platform", "mobile_both"]:
            risk_score += 2
            risk_factors.append("Multi-platform development increases effort")

        if len(features.integrations) > 4:
            risk_score += 2
            risk_factors.append(f"Multiple third-party integrations ({len(features.integrations)})")

        if eaf > 1.15:
            risk_score += 2
            risk_factors.append(f"High effort adjustment factor ({eaf:.2f})")

        if "ai_ml_integration" in features.integrations:
            risk_score += 2
            risk_factors.append("AI/ML integration adds uncertainty")

        if "blockchain" in features.integrations:
            risk_score += 2
            risk_factors.append("Blockchain integration adds technical risk")

        if risk_score >= 8:
            level = "high"
        elif risk_score >= 4:
            level = "medium"
        else:
            level = "low"

        return {
            "level": level,
            "score": risk_score,
            "factors": risk_factors
        }

    def _format_inr(self, amount: float) -> str:
        if amount >= 10000000:
            return f"₹{amount/10000000:.2f} Cr"
        elif amount >= 100000:
            return f"₹{amount/100000:.2f} L"
        else:
            return f"₹{amount:,.0f}"


def estimate_cost(
    features: ExtractedFeatures,
    cost_per_person_month: float = COCOMO_COST_PER_PERSON_MONTH,
    buffer_percentage: float = DEFAULT_BUFFER_PERCENTAGE
) -> ProjectEstimate:
    estimator = CostEstimator(
        cost_per_person_month=cost_per_person_month,
        buffer_percentage=buffer_percentage
    )
    return estimator.estimate(features)