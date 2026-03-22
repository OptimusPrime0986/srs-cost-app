"""
Cost Estimator Module
Calculates project costs based on extracted features and parameters.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
import math

from feature_extractor import ExtractedFeatures
from config import (
    BASE_COST_PER_FEATURE, COMPLEXITY_MULTIPLIERS, PLATFORM_MULTIPLIERS,
    UI_COMPLEXITY_MULTIPLIERS, INTEGRATION_COSTS, DEVELOPMENT_PHASES
)


@dataclass
class CostBreakdown:
    """Data class for detailed cost breakdown"""
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
    
    # Breakdown details
    feature_breakdown: List[Dict] = field(default_factory=list)
    integration_breakdown: List[Dict] = field(default_factory=list)
    phase_breakdown: Dict[str, float] = field(default_factory=dict)
    
    # Multipliers applied
    complexity_multiplier: float = 1.0
    platform_multiplier: float = 1.0
    ui_multiplier: float = 1.0
    
    # Summary
    cost_per_feature: float = 0.0
    cost_per_module: float = 0.0


@dataclass
class TimelineEstimate:
    """Data class for timeline estimation"""
    total_weeks: int = 0
    total_days: int = 0
    total_months: float = 0.0
    
    # Phase-wise breakdown
    phases: Dict[str, int] = field(default_factory=dict)
    
    # Milestones
    milestones: List[Dict] = field(default_factory=list)
    
    # Start and end date estimation (from today)
    estimated_start: str = ""
    estimated_end: str = ""


@dataclass
class ProjectEstimate:
    """Complete project estimation result"""
    cost: CostBreakdown = field(default_factory=CostBreakdown)
    timeline: TimelineEstimate = field(default_factory=TimelineEstimate)
    
    # Summary
    total_cost_inr: float = 0.0
    total_cost_formatted: str = ""
    timeline_weeks: int = 0
    
    # Confidence
    estimation_confidence: float = 0.0
    
    # Risk assessment
    risk_level: str = "medium"
    risk_factors: List[str] = field(default_factory=list)


class CostEstimator:
    """
    Main cost estimation class implementing the modular cost formula.
    """
    
    def __init__(self):
        """Initialize the cost estimator"""
        self.base_cost_per_feature = BASE_COST_PER_FEATURE
    
    def estimate(self, features: ExtractedFeatures) -> ProjectEstimate:
        """
        Calculate complete project estimation.
        
        Args:
            features: ExtractedFeatures object from feature extractor
            
        Returns:
            ProjectEstimate with cost, timeline, and other details
        """
        result = ProjectEstimate()
        
        # Calculate cost breakdown
        result.cost = self._calculate_cost(features)
        
        # Calculate timeline
        result.timeline = self._calculate_timeline(features, result.cost)
        
        # Set summary values
        result.total_cost_inr = result.cost.total_cost
        result.total_cost_formatted = self._format_inr(result.cost.total_cost)
        result.timeline_weeks = result.timeline.total_weeks
        
        # Calculate estimation confidence
        result.estimation_confidence = features.extraction_confidence
        
        # Assess risks
        risk_info = self._assess_risks(features)
        result.risk_level = risk_info['level']
        result.risk_factors = risk_info['factors']
        
        return result
    
    def _calculate_cost(self, features: ExtractedFeatures) -> CostBreakdown:
        """
        Calculate detailed cost breakdown.
        
        Formula: 
        Base Cost = Number of Features × Base Rate × Complexity Multiplier
        Adjusted Cost = Base Cost × Platform Multiplier × UI Multiplier
        Total = Adjusted Cost + Integration Costs + Testing + PM + Buffer
        """
        breakdown = CostBreakdown()
        
        # Get multipliers
        complexity_mult = COMPLEXITY_MULTIPLIERS.get(
            features.complexity, COMPLEXITY_MULTIPLIERS['medium']
        )
        platform_mult = PLATFORM_MULTIPLIERS.get(
            features.platform, PLATFORM_MULTIPLIERS['web']
        )
        ui_mult = UI_COMPLEXITY_MULTIPLIERS.get(
            features.ui_complexity, UI_COMPLEXITY_MULTIPLIERS['standard']
        )
        
        breakdown.complexity_multiplier = complexity_mult
        breakdown.platform_multiplier = platform_mult
        breakdown.ui_multiplier = ui_mult
        
        # Calculate feature cost
        num_features = len(features.features)
        if num_features == 0:
            num_features = 5  # Minimum assumption
        
        # Base cost per feature
        feature_costs = []
        for feature in features.features:
            feature_complexity = feature.get('complexity', 'medium')
            feature_mult = COMPLEXITY_MULTIPLIERS.get(feature_complexity, 1.5)
            feature_cost = self.base_cost_per_feature * feature_mult
            feature_costs.append({
                'description': feature['description'][:50],
                'complexity': feature_complexity,
                'cost': feature_cost
            })
        
        breakdown.feature_breakdown = feature_costs
        breakdown.feature_cost = sum(f['cost'] for f in feature_costs)
        
        if breakdown.feature_cost == 0:
            breakdown.feature_cost = num_features * self.base_cost_per_feature * complexity_mult
        
        # Apply platform multiplier
        breakdown.platform_cost = breakdown.feature_cost * (platform_mult - 1)
        
        # Apply UI multiplier
        breakdown.ui_cost = breakdown.feature_cost * (ui_mult - 1)
        
        # Calculate integration costs
        integration_breakdown = []
        for integration in features.integrations:
            if integration in INTEGRATION_COSTS:
                cost = INTEGRATION_COSTS[integration]
                integration_breakdown.append({
                    'name': integration.replace('_', ' ').title(),
                    'cost': cost
                })
        
        breakdown.integration_breakdown = integration_breakdown
        breakdown.integration_cost = sum(i['cost'] for i in integration_breakdown)
        
        # Calculate subtotal
        subtotal = (
            breakdown.feature_cost +
            breakdown.platform_cost +
            breakdown.ui_cost +
            breakdown.integration_cost
        )
        
        # Testing cost (20% of development)
        breakdown.testing_cost = subtotal * 0.20
        
        # Project management cost (10% of total)
        breakdown.project_management_cost = subtotal * 0.10
        
        # Buffer (10% for unforeseen issues)
        breakdown.buffer_cost = subtotal * 0.10
        
        # Calculate total
        breakdown.total_cost = (
            subtotal +
            breakdown.testing_cost +
            breakdown.project_management_cost +
            breakdown.buffer_cost
        )
        
        # Calculate base cost (before additions)
        breakdown.base_cost = breakdown.feature_cost
        
        # Calculate complexity cost (difference from base)
        breakdown.complexity_cost = breakdown.feature_cost * (complexity_mult - 1)
        
        # Calculate averages
        breakdown.cost_per_feature = breakdown.total_cost / max(num_features, 1)
        breakdown.cost_per_module = breakdown.total_cost / max(len(features.modules), 1)
        
        # Phase-wise breakdown
        for phase, percentage in DEVELOPMENT_PHASES.items():
            breakdown.phase_breakdown[phase] = breakdown.total_cost * percentage
        
        return breakdown
    
    def _calculate_timeline(self, features: ExtractedFeatures, 
                           cost: CostBreakdown) -> TimelineEstimate:
        """
        Calculate project timeline based on features and cost.
        """
        timeline = TimelineEstimate()
        
        # Base calculation: 1 week per 2-3 features, adjusted by complexity
        num_features = len(features.features)
        if num_features == 0:
            num_features = 5
        
        # Complexity adjustment
        complexity_time_mult = {
            'low': 0.8,
            'medium': 1.0,
            'high': 1.5,
            'very_high': 2.0
        }
        
        time_mult = complexity_time_mult.get(features.complexity, 1.0)
        
        # Platform adjustment
        platform_time_mult = {
            'web': 1.0,
            'mobile_android': 1.1,
            'mobile_ios': 1.1,
            'mobile_both': 1.5,
            'web_and_mobile': 1.8,
            'desktop': 1.0,
            'cross_platform': 1.6
        }
        
        platform_mult = platform_time_mult.get(features.platform, 1.0)
        
        # Base weeks calculation
        base_weeks = math.ceil(num_features / 2.5)
        
        # Apply multipliers
        total_weeks = math.ceil(base_weeks * time_mult * platform_mult)
        
        # Add integration time
        integration_weeks = len(features.integrations) * 0.5
        total_weeks += math.ceil(integration_weeks)
        
        # Minimum project duration
        total_weeks = max(total_weeks, 4)
        
        # Maximum cap based on scope
        scope_max_weeks = {
            'small': 12,
            'medium': 24,
            'large': 48,
            'enterprise': 72
        }
        max_weeks = scope_max_weeks.get(features.estimated_scope, 48)
        total_weeks = min(total_weeks, max_weeks)
        
        timeline.total_weeks = total_weeks
        timeline.total_days = total_weeks * 5  # Working days
        timeline.total_months = total_weeks / 4.33
        
        # Calculate phase durations
        for phase, percentage in DEVELOPMENT_PHASES.items():
            phase_weeks = math.ceil(total_weeks * percentage)
            timeline.phases[phase] = max(phase_weeks, 1)
        
        # Create milestones
        current_week = 0
        milestones = []
        
        phase_names = {
            'requirement_analysis': 'Requirements Sign-off',
            'design': 'Design Approval',
            'development': 'Development Complete',
            'testing': 'QA Sign-off',
            'deployment': 'Go Live',
            'buffer': 'Project Closure'
        }
        
        for phase, weeks in timeline.phases.items():
            current_week += weeks
            milestones.append({
                'name': phase_names.get(phase, phase.replace('_', ' ').title()),
                'week': current_week,
                'description': f'Complete by week {current_week}'
            })
        
        timeline.milestones = milestones
        
        # Calculate dates
        from datetime import datetime, timedelta
        start_date = datetime.now()
        end_date = start_date + timedelta(weeks=total_weeks)
        
        timeline.estimated_start = start_date.strftime('%Y-%m-%d')
        timeline.estimated_end = end_date.strftime('%Y-%m-%d')
        
        return timeline
    
    def _assess_risks(self, features: ExtractedFeatures) -> Dict:
        """
        Assess project risks based on extracted features.
        """
        risk_score = 0
        risk_factors = []
        
        # Feature count risk
        num_features = len(features.features)
        if num_features > 30:
            risk_score += 3
            risk_factors.append(f"Large number of features ({num_features})")
        elif num_features > 15:
            risk_score += 1
        
        # Complexity risk
        if features.complexity in ['high', 'very_high']:
            risk_score += 3
            risk_factors.append(f"High complexity level: {features.complexity}")
        
        # Multi-platform risk
        if features.platform in ['web_and_mobile', 'cross_platform', 'mobile_both']:
            risk_score += 2
            risk_factors.append("Multi-platform development increases complexity")
        
        # Integration risk
        num_integrations = len(features.integrations)
        if num_integrations > 5:
            risk_score += 2
            risk_factors.append(f"Multiple third-party integrations ({num_integrations})")
        
        # Complex integrations
        high_risk_integrations = ['ai_ml_integration', 'blockchain', 'video_streaming']
        for integration in features.integrations:
            if integration in high_risk_integrations:
                risk_score += 2
                risk_factors.append(f"Complex integration: {integration}")
        
        # UI complexity risk
        if features.ui_complexity in ['premium', 'custom']:
            risk_score += 1
            risk_factors.append("Complex UI requirements")
        
        # Determine risk level
        if risk_score >= 8:
            level = 'high'
        elif risk_score >= 4:
            level = 'medium'
        else:
            level = 'low'
        
        return {
            'level': level,
            'score': risk_score,
            'factors': risk_factors
        }
    
    def _format_inr(self, amount: float) -> str:
        """Format amount in Indian Rupee format"""
        if amount >= 10000000:  # 1 Crore
            return f"₹{amount/10000000:.2f} Cr"
        elif amount >= 100000:  # 1 Lakh
            return f"₹{amount/100000:.2f} L"
        else:
            return f"₹{amount:,.0f}"


def estimate_cost(features: ExtractedFeatures) -> ProjectEstimate:
    """
    Convenience function for estimating project cost.
    """
    estimator = CostEstimator()
    return estimator.estimate(features)