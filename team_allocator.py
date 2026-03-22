"""
Team Allocator Module
Determines optimal team composition based on project requirements.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
import math

from feature_extractor import ExtractedFeatures
from cost_estimator import ProjectEstimate
from config import TEAM_ROLES


@dataclass
class TeamMember:
    """Data class for team member allocation"""
    role: str
    count: int
    weekly_rate: float
    total_weeks: int
    total_cost: float
    responsibilities: List[str] = field(default_factory=list)


@dataclass
class TeamAllocation:
    """Complete team allocation result"""
    total_team_size: int = 0
    team_members: List[TeamMember] = field(default_factory=list)
    total_team_cost: float = 0.0
    
    # Role-wise breakdown
    developers: int = 0
    designers: int = 0
    testers: int = 0
    managers: int = 0
    specialists: int = 0
    
    # Skills required
    required_skills: List[str] = field(default_factory=list)
    
    # Recommendations
    recommendations: List[str] = field(default_factory=list)


class TeamAllocator:
    """
    Determines optimal team composition based on project parameters.
    """
    
    def __init__(self):
        """Initialize the team allocator"""
        self.roles = TEAM_ROLES
    
    def allocate(self, features: ExtractedFeatures, 
                 estimate: ProjectEstimate) -> TeamAllocation:
        """
        Determine team composition based on project requirements.
        
        Args:
            features: Extracted features from the document
            estimate: Project cost and timeline estimate
            
        Returns:
            TeamAllocation with complete team breakdown
        """
        result = TeamAllocation()
        
        num_features = len(features.features)
        num_modules = len(features.modules)
        total_weeks = estimate.timeline_weeks
        
        # Calculate team members
        members = []
        
        # Project Manager
        if num_features >= 10 or total_weeks >= 8:
            pm = self._allocate_role(
                'Project Manager',
                count=1,
                rate=40000,
                weeks=total_weeks,
                responsibilities=[
                    'Project planning and scheduling',
                    'Stakeholder communication',
                    'Risk management',
                    'Resource coordination'
                ]
            )
            members.append(pm)
            result.managers += 1
        
        # Tech Lead
        if num_features >= 15 or features.complexity in ['high', 'very_high']:
            tech_lead = self._allocate_role(
                'Tech Lead',
                count=1,
                rate=50000,
                weeks=total_weeks,
                responsibilities=[
                    'Technical architecture',
                    'Code reviews',
                    'Technical decision making',
                    'Team mentoring'
                ]
            )
            members.append(tech_lead)
            result.developers += 1
        
        # Senior Developers
        senior_dev_count = math.ceil(num_features / 8)
        senior_dev_count = max(1, min(senior_dev_count, 5))
        
        if features.complexity in ['high', 'very_high']:
            senior_dev_count = math.ceil(senior_dev_count * 1.5)
        
        senior_devs = self._allocate_role(
            'Senior Developer',
            count=senior_dev_count,
            rate=35000,
            weeks=int(total_weeks * 0.8),  # Development phase
            responsibilities=[
                'Core feature development',
                'Complex implementations',
                'Integration work',
                'Code architecture'
            ]
        )
        members.append(senior_devs)
        result.developers += senior_dev_count
        
        # Junior Developers
        junior_dev_count = math.ceil(num_features / 5) - senior_dev_count
        junior_dev_count = max(0, min(junior_dev_count, 4))
        
        if junior_dev_count > 0:
            junior_devs = self._allocate_role(
                'Junior Developer',
                count=junior_dev_count,
                rate=20000,
                weeks=int(total_weeks * 0.7),
                responsibilities=[
                    'Basic feature implementation',
                    'Bug fixes',
                    'Unit testing',
                    'Documentation'
                ]
            )
            members.append(junior_devs)
            result.developers += junior_dev_count
        
        # UI/UX Designer
        if features.ui_complexity in ['standard', 'advanced', 'premium', 'custom']:
            designer_count = 1
            if features.ui_complexity in ['premium', 'custom']:
                designer_count = 2
            
            designers = self._allocate_role(
                'UI/UX Designer',
                count=designer_count,
                rate=30000,
                weeks=int(total_weeks * 0.4),  # Design phase + support
                responsibilities=[
                    'UI/UX design',
                    'Wireframes and prototypes',
                    'Design system creation',
                    'User research'
                ]
            )
            members.append(designers)
            result.designers += designer_count
        
        # QA Engineers
        qa_count = max(1, math.ceil((result.developers) * 0.4))
        
        qa_engineers = self._allocate_role(
            'QA Engineer',
            count=qa_count,
            rate=25000,
            weeks=int(total_weeks * 0.5),  # Testing phases
            responsibilities=[
                'Test planning',
                'Manual testing',
                'Automated testing',
                'Bug reporting'
            ]
        )
        members.append(qa_engineers)
        result.testers += qa_count
        
        # DevOps Engineer (for complex projects)
        if (features.complexity in ['high', 'very_high'] or 
            features.platform in ['web_and_mobile', 'cross_platform'] or
            len(features.integrations) > 3):
            devops = self._allocate_role(
                'DevOps Engineer',
                count=1,
                rate=35000,
                weeks=int(total_weeks * 0.3),
                responsibilities=[
                    'CI/CD setup',
                    'Cloud infrastructure',
                    'Deployment automation',
                    'Monitoring setup'
                ]
            )
            members.append(devops)
            result.specialists += 1
        
        # Business Analyst (for enterprise projects)
        if features.estimated_scope == 'enterprise' or num_features > 25:
            ba = self._allocate_role(
                'Business Analyst',
                count=1,
                rate=35000,
                weeks=int(total_weeks * 0.4),
                responsibilities=[
                    'Requirement analysis',
                    'Documentation',
                    'Stakeholder coordination',
                    'Process mapping'
                ]
            )
            members.append(ba)
            result.specialists += 1
        
        # Calculate totals
        result.team_members = members
        result.total_team_size = sum(m.count for m in members)
        result.total_team_cost = sum(m.total_cost for m in members)
        
        # Determine required skills
        result.required_skills = self._determine_skills(features)
        
        # Add recommendations
        result.recommendations = self._generate_recommendations(features, result)
        
        return result
    
    def _allocate_role(self, role: str, count: int, rate: float,
                       weeks: int, responsibilities: List[str]) -> TeamMember:
        """
        Create a team member allocation.
        """
        return TeamMember(
            role=role,
            count=count,
            weekly_rate=rate,
            total_weeks=weeks,
            total_cost=count * rate * weeks,
            responsibilities=responsibilities
        )
    
    def _determine_skills(self, features: ExtractedFeatures) -> List[str]:
        """
        Determine required technical skills based on features.
        """
        skills = set()
        
        # Platform-based skills
        platform_skills = {
            'web': ['HTML/CSS', 'JavaScript', 'React/Angular/Vue', 'Node.js/Python/PHP'],
            'mobile_android': ['Kotlin', 'Android SDK', 'Java'],
            'mobile_ios': ['Swift', 'iOS SDK', 'Xcode'],
            'mobile_both': ['React Native', 'Flutter', 'Dart'],
            'web_and_mobile': ['Full Stack', 'React Native', 'REST APIs'],
            'cross_platform': ['Flutter', 'React Native', 'Cross-platform Development']
        }
        
        if features.platform in platform_skills:
            skills.update(platform_skills[features.platform])
        
        # Integration-based skills
        integration_skills = {
            'payment_gateway': ['Payment Integration', 'Razorpay/Stripe SDK'],
            'ai_ml_integration': ['Python', 'TensorFlow/PyTorch', 'Machine Learning'],
            'blockchain': ['Solidity', 'Web3.js', 'Smart Contracts'],
            'video_streaming': ['WebRTC', 'HLS/DASH', 'Media Servers'],
            'chat_realtime': ['WebSockets', 'Socket.io', 'Real-time Communication']
        }
        
        for integration in features.integrations:
            if integration in integration_skills:
                skills.update(integration_skills[integration])
        
        # Add common skills
        skills.update(['Git', 'Agile/Scrum', 'REST APIs', 'SQL/NoSQL'])
        
        # Complexity-based skills
        if features.complexity in ['high', 'very_high']:
            skills.update(['System Design', 'Microservices', 'Docker', 'CI/CD'])
        
        return sorted(list(skills))
    
    def _generate_recommendations(self, features: ExtractedFeatures,
                                   allocation: TeamAllocation) -> List[str]:
        """
        Generate team allocation recommendations.
        """
        recommendations = []
        
        # Team size recommendations
        if allocation.total_team_size > 10:
            recommendations.append(
                "Consider splitting the project into smaller teams with clear ownership"
            )
        
        # Developer to QA ratio
        if allocation.testers < allocation.developers * 0.3:
            recommendations.append(
                "Consider adding more QA resources for thorough testing coverage"
            )
        
        # UI complexity recommendation
        if features.ui_complexity in ['premium', 'custom'] and allocation.designers < 2:
            recommendations.append(
                "Complex UI requirements may need additional design resources"
            )
        
        # Integration recommendation
        if len(features.integrations) > 3:
            recommendations.append(
                "Multiple integrations may require dedicated integration specialists"
            )
        
        # Complexity recommendation
        if features.complexity == 'very_high':
            recommendations.append(
                "High complexity project - consider involving solution architects"
            )
        
        return recommendations


def allocate_team(features: ExtractedFeatures, 
                  estimate: ProjectEstimate) -> TeamAllocation:
    """
    Convenience function for team allocation.
    """
    allocator = TeamAllocator()
    return allocator.allocate(features, estimate)