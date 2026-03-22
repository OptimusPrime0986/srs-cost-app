"""
Suggestion Engine Module
Provides intelligent suggestions for cost reduction and risk mitigation.
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass, field

from feature_extractor import ExtractedFeatures
from cost_estimator import ProjectEstimate
from team_allocator import TeamAllocation
from config import COST_REDUCTION_SUGGESTIONS


@dataclass
class Suggestion:
    """Data class for a single suggestion"""
    category: str
    title: str
    description: str
    potential_saving: float = 0.0
    potential_saving_formatted: str = ""
    priority: str = "medium"  # low, medium, high
    implementation_effort: str = "medium"


@dataclass
class ProjectSuggestions:
    """Complete suggestions for the project"""
    cost_reduction: List[Suggestion] = field(default_factory=list)
    risk_mitigation: List[Suggestion] = field(default_factory=list)
    timeline_optimization: List[Suggestion] = field(default_factory=list)
    quality_improvement: List[Suggestion] = field(default_factory=list)
    
    # High complexity sections
    complexity_warnings: List[Dict] = field(default_factory=list)
    
    # Total potential savings
    total_potential_savings: float = 0.0
    total_potential_savings_formatted: str = ""


class SuggestionEngine:
    """
    Generates intelligent suggestions based on project analysis.
    """
    
    def __init__(self):
        """Initialize the suggestion engine"""
        pass
    
    def generate(self, features: ExtractedFeatures,
                 estimate: ProjectEstimate,
                 team: TeamAllocation) -> ProjectSuggestions:
        """
        Generate suggestions based on project analysis.
        
        Args:
            features: Extracted features
            estimate: Cost estimate
            team: Team allocation
            
        Returns:
            ProjectSuggestions with all recommendations
        """
        result = ProjectSuggestions()
        total_cost = estimate.total_cost_inr
        
        # Generate cost reduction suggestions
        result.cost_reduction = self._generate_cost_suggestions(
            features, estimate, total_cost
        )
        
        # Generate risk mitigation suggestions
        result.risk_mitigation = self._generate_risk_suggestions(
            features, estimate
        )
        
        # Generate timeline optimization suggestions
        result.timeline_optimization = self._generate_timeline_suggestions(
            features, estimate, team
        )
        
        # Generate quality improvement suggestions
        result.quality_improvement = self._generate_quality_suggestions(
            features, team
        )
        
        # Highlight complexity warnings
        result.complexity_warnings = self._generate_complexity_warnings(features)
        
        # Calculate total potential savings
        result.total_potential_savings = sum(
            s.potential_saving for s in result.cost_reduction
        )
        
        if result.total_potential_savings >= 10000000:
            result.total_potential_savings_formatted = (
                f"₹{result.total_potential_savings/10000000:.2f} Cr"
            )
        elif result.total_potential_savings >= 100000:
            result.total_potential_savings_formatted = (
                f"₹{result.total_potential_savings/100000:.2f} L"
            )
        else:
            result.total_potential_savings_formatted = (
                f"₹{result.total_potential_savings:,.0f}"
            )
        
        return result
    
    def _generate_cost_suggestions(self, features: ExtractedFeatures,
                                   estimate: ProjectEstimate,
                                   total_cost: float) -> List[Suggestion]:
        """
        Generate cost reduction suggestions.
        """
        suggestions = []
        
        # Platform optimization
        if features.platform in ['web_and_mobile', 'mobile_both']:
            saving = total_cost * 0.20
            suggestions.append(Suggestion(
                category='Platform',
                title='Cross-Platform Framework',
                description=(
                    'Consider using cross-platform frameworks like Flutter or '
                    'React Native instead of native development for both platforms. '
                    'This can reduce development time and costs by 20-30%.'
                ),
                potential_saving=saving,
                potential_saving_formatted=self._format_inr(saving),
                priority='high',
                implementation_effort='medium'
            ))
        
        # UI complexity optimization
        if features.ui_complexity in ['premium', 'custom']:
            saving = total_cost * 0.15
            suggestions.append(Suggestion(
                category='Design',
                title='UI Component Libraries',
                description=(
                    'Leverage pre-built UI component libraries (Material-UI, '
                    'Ant Design, etc.) instead of fully custom designs. '
                    'This maintains quality while reducing design and development time.'
                ),
                potential_saving=saving,
                potential_saving_formatted=self._format_inr(saving),
                priority='medium',
                implementation_effort='low'
            ))
        
        # Integration optimization
        if len(features.integrations) > 4:
            saving = total_cost * 0.10
            suggestions.append(Suggestion(
                category='Integration',
                title='Phased Integration Approach',
                description=(
                    f'The project requires {len(features.integrations)} integrations. '
                    'Consider implementing essential integrations in MVP and '
                    'adding others in subsequent phases to reduce initial costs.'
                ),
                potential_saving=saving,
                potential_saving_formatted=self._format_inr(saving),
                priority='high',
                implementation_effort='low'
            ))
        
        # Feature prioritization
        num_features = len(features.features)
        if num_features > 20:
            saving = total_cost * 0.25
            suggestions.append(Suggestion(
                category='Scope',
                title='MVP-First Approach',
                description=(
                    f'With {num_features} features, consider implementing a '
                    'Minimum Viable Product (MVP) first with core features only. '
                    'This allows faster time-to-market and iterative improvement '
                    'based on user feedback.'
                ),
                potential_saving=saving,
                potential_saving_formatted=self._format_inr(saving),
                priority='high',
                implementation_effort='medium'
            ))
        
        # Offshore/hybrid team suggestion
        if total_cost > 2000000:
            saving = total_cost * 0.15
            suggestions.append(Suggestion(
                category='Team',
                title='Hybrid Team Model',
                description=(
                    'Consider a hybrid team model with a mix of onshore and '
                    'offshore resources. This can provide cost benefits while '
                    'maintaining quality through proper coordination.'
                ),
                potential_saving=saving,
                potential_saving_formatted=self._format_inr(saving),
                priority='medium',
                implementation_effort='high'
            ))
        
        # Cloud cost optimization
        if 'cloud_storage' in features.integrations or features.complexity in ['high', 'very_high']:
            saving = total_cost * 0.05
            suggestions.append(Suggestion(
                category='Infrastructure',
                title='Cloud Cost Optimization',
                description=(
                    'Implement cloud cost optimization strategies: use reserved '
                    'instances, auto-scaling, right-sizing, and spot instances '
                    'for non-critical workloads.'
                ),
                potential_saving=saving,
                potential_saving_formatted=self._format_inr(saving),
                priority='low',
                implementation_effort='medium'
            ))
        
        return suggestions
    
    def _generate_risk_suggestions(self, features: ExtractedFeatures,
                                   estimate: ProjectEstimate) -> List[Suggestion]:
        """
        Generate risk mitigation suggestions.
        """
        suggestions = []
        
        # Complexity risk
        if features.complexity in ['high', 'very_high']:
            suggestions.append(Suggestion(
                category='Technical Risk',
                title='Proof of Concept (POC)',
                description=(
                    'High complexity features identified. Create POCs for complex '
                    'components before full development to validate technical '
                    'feasibility and reduce implementation risks.'
                ),
                priority='high',
                implementation_effort='medium'
            ))
        
        # Integration risk
        complex_integrations = ['ai_ml_integration', 'blockchain', 'video_streaming']
        risky_integrations = [i for i in features.integrations if i in complex_integrations]
        
        if risky_integrations:
            suggestions.append(Suggestion(
                category='Integration Risk',
                title='Integration Testing Strategy',
                description=(
                    f'Complex integrations detected: {", ".join(risky_integrations)}. '
                    'Implement a robust integration testing strategy with mock '
                    'services and sandbox environments early in the development cycle.'
                ),
                priority='high',
                implementation_effort='medium'
            ))
        
        # Third-party dependency risk
        if len(features.integrations) > 3:
            suggestions.append(Suggestion(
                category='Dependency Risk',
                title='Vendor Risk Assessment',
                description=(
                    'Multiple third-party dependencies identified. Document backup '
                    'options for critical integrations and establish SLAs with vendors.'
                ),
                priority='medium',
                implementation_effort='low'
            ))
        
        # Scale risk
        if features.estimated_scope in ['large', 'enterprise']:
            suggestions.append(Suggestion(
                category='Scale Risk',
                title='Performance Architecture Review',
                description=(
                    'For large-scale projects, conduct early architecture reviews '
                    'focusing on scalability, performance, and reliability. '
                    'Consider load testing from early stages.'
                ),
                priority='high',
                implementation_effort='medium'
            ))
        
        return suggestions
    
    def _generate_timeline_suggestions(self, features: ExtractedFeatures,
                                       estimate: ProjectEstimate,
                                       team: TeamAllocation) -> List[Suggestion]:
        """
        Generate timeline optimization suggestions.
        """
        suggestions = []
        
        # Parallel development
        if len(features.modules) > 3:
            suggestions.append(Suggestion(
                category='Development',
                title='Parallel Development Streams',
                description=(
                    f'{len(features.modules)} modules identified. Organize '
                    'development into parallel streams with clear interfaces '
                    'to reduce overall timeline.'
                ),
                priority='high',
                implementation_effort='medium'
            ))
        
        # Automated testing
        if estimate.timeline_weeks > 12:
            suggestions.append(Suggestion(
                category='Testing',
                title='Automated Testing from Day 1',
                description=(
                    'Implement automated testing (unit, integration) from the '
                    'beginning. This reduces regression testing time and enables '
                    'faster release cycles.'
                ),
                priority='high',
                implementation_effort='medium'
            ))
        
        # CI/CD
        if features.complexity in ['medium', 'high', 'very_high']:
            suggestions.append(Suggestion(
                category='DevOps',
                title='CI/CD Pipeline Setup',
                description=(
                    'Set up Continuous Integration/Deployment pipelines early. '
                    'This automates build, test, and deployment processes, '
                    'reducing manual effort and human errors.'
                ),
                priority='medium',
                implementation_effort='medium'
            ))
        
        # Design-Development overlap
        suggestions.append(Suggestion(
            category='Process',
            title='Design-Development Overlap',
            description=(
                'Start development of core features while design for secondary '
                'features is in progress. This parallel approach can reduce '
                'overall timeline by 15-20%.'
            ),
            priority='medium',
            implementation_effort='low'
        ))
        
        return suggestions
    
    def _generate_quality_suggestions(self, features: ExtractedFeatures,
                                      team: TeamAllocation) -> List[Suggestion]:
        """
        Generate quality improvement suggestions.
        """
        suggestions = []
        
        # Code review process
        suggestions.append(Suggestion(
            category='Code Quality',
            title='Mandatory Code Reviews',
            description=(
                'Implement mandatory code reviews for all changes. Use tools '
                'like GitHub/GitLab merge requests with required approvals.'
            ),
            priority='high',
            implementation_effort='low'
        ))
        
        # Documentation
        if len(features.features) > 10:
            suggestions.append(Suggestion(
                category='Documentation',
                title='Comprehensive API Documentation',
                description=(
                    'Maintain up-to-date API documentation using tools like '
                    'Swagger/OpenAPI. This improves maintainability and '
                    'facilitates future integrations.'
                ),
                priority='medium',
                implementation_effort='medium'
            ))
        
        # Security
        if 'authentication_oauth' in features.integrations or 'payment_gateway' in features.integrations:
            suggestions.append(Suggestion(
                category='Security',
                title='Security Audit',
                description=(
                    'Given the sensitive integrations (authentication/payments), '
                    'plan for security audits and penetration testing before launch.'
                ),
                priority='high',
                implementation_effort='medium'
            ))
        
        # Performance monitoring
        if features.complexity in ['high', 'very_high']:
            suggestions.append(Suggestion(
                category='Monitoring',
                title='APM Implementation',
                description=(
                    'Implement Application Performance Monitoring (APM) tools '
                    'like New Relic, Datadog, or open-source alternatives '
                    'for production monitoring.'
                ),
                priority='medium',
                implementation_effort='medium'
            ))
        
        return suggestions
    
    def _generate_complexity_warnings(self, features: ExtractedFeatures) -> List[Dict]:
        """
        Generate warnings for high complexity sections.
        """
        warnings = []
        
        for i, section in enumerate(features.high_complexity_sections[:5]):
            warnings.append({
                'id': i + 1,
                'text': section,
                'reason': 'Contains complex technical requirements',
                'recommendation': 'Consider breaking down into smaller components'
            })
        
        # Add warnings based on complexity factors
        for factor in features.complexity_factors[:5]:
            warnings.append({
                'id': len(warnings) + 1,
                'text': f'Complexity factor: {factor}',
                'reason': 'May increase development time and cost',
                'recommendation': 'Ensure proper expertise is available'
            })
        
        return warnings
    
    def _format_inr(self, amount: float) -> str:
        """Format amount in Indian Rupee format"""
        if amount >= 10000000:
            return f"₹{amount/10000000:.2f} Cr"
        elif amount >= 100000:
            return f"₹{amount/100000:.2f} L"
        else:
            return f"₹{amount:,.0f}"


def generate_suggestions(features: ExtractedFeatures,
                         estimate: ProjectEstimate,
                         team: TeamAllocation) -> ProjectSuggestions:
    """
    Convenience function for generating suggestions.
    """
    engine = SuggestionEngine()
    return engine.generate(features, estimate, team)