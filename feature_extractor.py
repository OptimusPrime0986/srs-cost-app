"""
Feature Extractor Module
Uses NLP techniques to extract features, complexity, integrations, and other
project parameters from parsed SRS documents.
"""

import re
from typing import Dict, List, Tuple, Set, Optional
from dataclasses import dataclass, field
from collections import Counter
import logging

# NLP Libraries
try:
    import nltk
    from nltk.tokenize import sent_tokenize, word_tokenize
    from nltk.corpus import stopwords
    from nltk.stem import WordNetLemmatizer
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

from document_parser import ParsedDocument
from config import (
    FEATURE_KEYWORDS, COMPLEXITY_INDICATORS, PLATFORM_KEYWORDS,
    UI_KEYWORDS, INTEGRATION_KEYWORDS, MODULE_PATTERNS
)

logger = logging.getLogger(__name__)


@dataclass
class ExtractedFeatures:
    """Data class to hold extracted feature information"""
    features: List[Dict] = field(default_factory=list)
    modules: List[str] = field(default_factory=list)
    complexity: str = "medium"
    complexity_score: float = 0.0
    complexity_factors: List[str] = field(default_factory=list)
    platform: str = "web"
    platform_details: Dict = field(default_factory=dict)
    ui_complexity: str = "standard"
    ui_details: List[str] = field(default_factory=list)
    integrations: List[str] = field(default_factory=list)
    integration_details: Dict[str, List[str]] = field(default_factory=dict)
    estimated_scope: str = "medium"
    key_technologies: List[str] = field(default_factory=list)
    user_roles: List[str] = field(default_factory=list)
    security_requirements: List[str] = field(default_factory=list)
    performance_requirements: List[str] = field(default_factory=list)
    high_complexity_sections: List[str] = field(default_factory=list)
    extraction_confidence: float = 0.0


class NLPProcessor:
    """
    NLP Processing utilities for text analysis.
    """
    
    def __init__(self):
        """Initialize NLP components"""
        self.nltk_available = NLTK_AVAILABLE
        self.sklearn_available = SKLEARN_AVAILABLE
        
        if NLTK_AVAILABLE:
            try:
                # Download required NLTK data
                nltk.download('punkt', quiet=True)
                nltk.download('stopwords', quiet=True)
                nltk.download('wordnet', quiet=True)
                nltk.download('averaged_perceptron_tagger', quiet=True)
                
                self.stop_words = set(stopwords.words('english'))
                self.lemmatizer = WordNetLemmatizer()
            except Exception as e:
                logger.warning(f"NLTK initialization warning: {e}")
                self.nltk_available = False
    
    def tokenize_sentences(self, text: str) -> List[str]:
        """Tokenize text into sentences"""
        if self.nltk_available:
            try:
                return sent_tokenize(text)
            except:
                pass
        # Fallback: simple sentence splitting
        return re.split(r'[.!?]+', text)
    
    def tokenize_words(self, text: str) -> List[str]:
        """Tokenize text into words"""
        if self.nltk_available:
            try:
                return word_tokenize(text.lower())
            except:
                pass
        # Fallback: simple word splitting
        return re.findall(r'\b\w+\b', text.lower())
    
    def extract_keywords(self, text: str, top_n: int = 20) -> List[Tuple[str, float]]:
        """Extract keywords using TF-IDF if available"""
        if not self.sklearn_available:
            # Fallback: simple word frequency
            words = self.tokenize_words(text)
            if self.nltk_available:
                words = [w for w in words if w not in self.stop_words and len(w) > 2]
            word_freq = Counter(words)
            return word_freq.most_common(top_n)
        
        try:
            # Use TF-IDF for keyword extraction
            sentences = self.tokenize_sentences(text)
            if len(sentences) < 2:
                sentences = [text]
            
            vectorizer = TfidfVectorizer(
                max_features=100,
                stop_words='english',
                ngram_range=(1, 2)
            )
            tfidf_matrix = vectorizer.fit_transform(sentences)
            
            # Get feature names and their scores
            feature_names = vectorizer.get_feature_names_out()
            scores = tfidf_matrix.sum(axis=0).A1
            
            keyword_scores = list(zip(feature_names, scores))
            keyword_scores.sort(key=lambda x: x[1], reverse=True)
            
            return keyword_scores[:top_n]
            
        except Exception as e:
            logger.warning(f"TF-IDF extraction failed: {e}")
            return []
    
    def lemmatize(self, word: str) -> str:
        """Lemmatize a word"""
        if self.nltk_available:
            try:
                return self.lemmatizer.lemmatize(word.lower())
            except:
                pass
        return word.lower()


class FeatureExtractor:
    """
    Main feature extraction class that analyzes SRS documents and extracts
    features, complexity, integrations, and other project parameters.
    """
    
    def __init__(self):
        """Initialize the feature extractor"""
        self.nlp = NLPProcessor()
        logger.info("FeatureExtractor initialized")
    
    def extract(self, parsed_doc: ParsedDocument) -> ExtractedFeatures:
        """
        Main extraction method that processes a parsed document.
        
        Args:
            parsed_doc: ParsedDocument object from document parser
            
        Returns:
            ExtractedFeatures object with all extracted information
        """
        result = ExtractedFeatures()
        text = parsed_doc.raw_text.lower()
        original_text = parsed_doc.raw_text
        
        # Extract features
        result.features = self._extract_features(original_text, parsed_doc)
        
        # Extract modules
        result.modules = self._extract_modules(original_text, parsed_doc)
        
        # Determine complexity
        complexity_info = self._determine_complexity(text, result.features)
        result.complexity = complexity_info['level']
        result.complexity_score = complexity_info['score']
        result.complexity_factors = complexity_info['factors']
        result.high_complexity_sections = complexity_info['high_complexity_sections']
        
        # Detect platform
        platform_info = self._detect_platform(text)
        result.platform = platform_info['platform']
        result.platform_details = platform_info
        
        # Determine UI complexity
        ui_info = self._determine_ui_complexity(text)
        result.ui_complexity = ui_info['level']
        result.ui_details = ui_info['details']
        
        # Extract integrations
        integration_info = self._extract_integrations(text)
        result.integrations = list(integration_info.keys())
        result.integration_details = integration_info
        
        # Estimate scope
        result.estimated_scope = self._estimate_scope(result)
        
        # Extract additional information
        result.key_technologies = self._extract_technologies(text)
        result.user_roles = self._extract_user_roles(text)
        result.security_requirements = self._extract_security_requirements(original_text)
        result.performance_requirements = self._extract_performance_requirements(original_text)
        
        # Calculate extraction confidence
        result.extraction_confidence = self._calculate_confidence(result, parsed_doc)
        
        return result
    
    def _extract_features(self, text: str, parsed_doc: ParsedDocument) -> List[Dict]:
        """
        Extract features from the document text.
        """
        features = []
        seen_features = set()
        
        # Get sentences
        sentences = self.nlp.tokenize_sentences(text)
        
        # Feature extraction patterns
        feature_patterns = [
            r'(?i)(?:the\s+)?system\s+(?:shall|should|must|will)\s+(.+?)(?:\.|$)',
            r'(?i)(?:the\s+)?(?:application|software|app)\s+(?:shall|should|must|will)\s+(.+?)(?:\.|$)',
            r'(?i)user\s+(?:shall|should|can|will|must)\s+(?:be\s+able\s+to\s+)?(.+?)(?:\.|$)',
            r'(?i)(?:ability|feature|functionality)\s+to\s+(.+?)(?:\.|$)',
            r'(?i)(?:provide|enable|allow|support)\s+(.+?)(?:\.|$)',
            r'(?i)(?:FR|REQ|UC)[-_]?\d+[.:]\s*(.+?)(?:\.|$)',
        ]
        
        # Extract from sentences
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 10:
                continue
            
            for pattern in feature_patterns:
                matches = re.findall(pattern, sentence)
                for match in matches:
                    feature_text = match.strip()
                    if len(feature_text) > 10 and feature_text not in seen_features:
                        feature = {
                            'description': feature_text[:200],  # Limit length
                            'source': 'pattern_match',
                            'complexity': self._estimate_feature_complexity(feature_text)
                        }
                        features.append(feature)
                        seen_features.add(feature_text)
        
        # Extract from bullet points
        for bullet in parsed_doc.bullet_points:
            if len(bullet) > 10 and bullet not in seen_features:
                # Check if it looks like a feature
                if any(kw in bullet.lower() for kw in FEATURE_KEYWORDS):
                    feature = {
                        'description': bullet[:200],
                        'source': 'bullet_point',
                        'complexity': self._estimate_feature_complexity(bullet)
                    }
                    features.append(feature)
                    seen_features.add(bullet)
        
        # If we found too few features, try keyword-based extraction
        if len(features) < 5:
            additional = self._extract_features_by_keywords(text, seen_features)
            features.extend(additional)
        
        logger.info(f"Extracted {len(features)} features")
        return features
    
    def _extract_features_by_keywords(self, text: str, seen: Set[str]) -> List[Dict]:
        """
        Extract features based on keyword presence in sentences.
        """
        features = []
        sentences = self.nlp.tokenize_sentences(text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 15 or len(sentence) > 300:
                continue
            
            sentence_lower = sentence.lower()
            
            # Check for feature-indicating keywords
            keyword_count = sum(1 for kw in FEATURE_KEYWORDS if kw in sentence_lower)
            
            if keyword_count >= 2 and sentence not in seen:
                feature = {
                    'description': sentence[:200],
                    'source': 'keyword_extraction',
                    'complexity': self._estimate_feature_complexity(sentence)
                }
                features.append(feature)
                seen.add(sentence)
        
        return features[:20]  # Limit additional features
    
    def _estimate_feature_complexity(self, feature_text: str) -> str:
        """
        Estimate complexity of a single feature.
        """
        text_lower = feature_text.lower()
        
        # Check for high complexity indicators
        for indicator in COMPLEXITY_INDICATORS['high']:
            if indicator in text_lower:
                return 'high'
        
        # Check for medium complexity indicators
        for indicator in COMPLEXITY_INDICATORS['medium']:
            if indicator in text_lower:
                return 'medium'
        
        return 'low'
    
    def _extract_modules(self, text: str, parsed_doc: ParsedDocument) -> List[str]:
        """
        Extract modules from the document.
        """
        modules = set()
        
        # Extract from module patterns
        for pattern in MODULE_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                module_name = match.strip()
                if len(module_name) > 2 and len(module_name) < 50:
                    modules.add(module_name.title())
        
        # Extract from headings
        for heading in parsed_doc.headings:
            if any(kw in heading.lower() for kw in ['module', 'management', 'system', 'portal']):
                modules.add(heading.title())
        
        # Common module keywords
        module_keywords = [
            'user management', 'admin panel', 'dashboard', 'authentication',
            'payment', 'notification', 'reporting', 'analytics', 'settings',
            'profile', 'inventory', 'order', 'product', 'customer', 'vendor',
            'cart', 'checkout', 'search', 'catalog', 'content management'
        ]
        
        for keyword in module_keywords:
            if keyword in text.lower():
                modules.add(keyword.title())
        
        return list(modules)[:15]  # Limit to 15 modules
    
    def _determine_complexity(self, text: str, features: List[Dict]) -> Dict:
        """
        Determine overall project complexity.
        """
        complexity_scores = {'high': 0, 'medium': 0, 'low': 0}
        factors = []
        high_complexity_sections = []
        
        # Check complexity indicators in text
        for level, indicators in COMPLEXITY_INDICATORS.items():
            for indicator in indicators:
                if indicator in text:
                    complexity_scores[level] += 1
                    if level == 'high':
                        factors.append(indicator)
                        # Find the sentence containing this indicator
                        for sentence in self.nlp.tokenize_sentences(text):
                            if indicator in sentence.lower():
                                high_complexity_sections.append(sentence[:150])
                                break
        
        # Factor in feature complexity
        for feature in features:
            complexity_scores[feature.get('complexity', 'low')] += 1
        
        # Factor in number of features
        feature_count = len(features)
        if feature_count > 30:
            complexity_scores['high'] += 5
            factors.append(f"Large number of features ({feature_count})")
        elif feature_count > 15:
            complexity_scores['medium'] += 3
        
        # Calculate weighted score
        total_score = (
            complexity_scores['high'] * 3 +
            complexity_scores['medium'] * 2 +
            complexity_scores['low'] * 1
        )
        
        # Normalize score to 0-100
        max_possible = (len(COMPLEXITY_INDICATORS['high']) * 3 +
                        len(COMPLEXITY_INDICATORS['medium']) * 2 +
                        len(features) * 3 + 5)
        normalized_score = min(100, (total_score / max_possible) * 100) if max_possible > 0 else 50
        
        # Determine level
        if normalized_score >= 70:
            level = 'very_high'
        elif normalized_score >= 50:
            level = 'high'
        elif normalized_score >= 30:
            level = 'medium'
        else:
            level = 'low'
        
        return {
            'level': level,
            'score': normalized_score,
            'factors': factors[:10],
            'high_complexity_sections': high_complexity_sections[:5]
        }
    
    def _detect_platform(self, text: str) -> Dict:
        """
        Detect target platform(s) from text.
        """
        platform_scores = {}
        platform_matches = {}
        
        for platform, keywords in PLATFORM_KEYWORDS.items():
            score = 0
            matches = []
            for keyword in keywords:
                if keyword in text:
                    score += 1
                    matches.append(keyword)
            if score > 0:
                platform_scores[platform] = score
                platform_matches[platform] = matches
        
        # Determine primary platform
        if not platform_scores:
            return {'platform': 'web', 'confidence': 0.5}
        
        # Check for multi-platform
        has_web = any(p in platform_scores for p in ['web'])
        has_mobile = any(p in platform_scores for p in ['mobile_android', 'mobile_ios', 'mobile_both'])
        
        if has_web and has_mobile:
            platform = 'web_and_mobile'
        elif 'mobile_both' in platform_scores:
            platform = 'mobile_both'
        else:
            platform = max(platform_scores, key=platform_scores.get)
        
        return {
            'platform': platform,
            'scores': platform_scores,
            'matches': platform_matches,
            'confidence': min(1.0, max(platform_scores.values()) / 5)
        }
    
    def _determine_ui_complexity(self, text: str) -> Dict:
        """
        Determine UI complexity from text.
        """
        ui_scores = {}
        details = []
        
        for level, keywords in UI_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    ui_scores[level] = ui_scores.get(level, 0) + 1
                    details.append(keyword)
        
        if not ui_scores:
            return {'level': 'standard', 'details': []}
        
        # Determine level based on highest scoring
        level = max(ui_scores, key=ui_scores.get)
        
        return {
            'level': level,
            'scores': ui_scores,
            'details': details[:10]
        }
    
    def _extract_integrations(self, text: str) -> Dict[str, List[str]]:
        """
        Extract required integrations from text.
        """
        integrations = {}
        
        for integration_type, keywords in INTEGRATION_KEYWORDS.items():
            matches = []
            for keyword in keywords:
                if keyword in text:
                    matches.append(keyword)
            
            if matches:
                integrations[integration_type] = matches
        
        return integrations
    
    def _estimate_scope(self, result: ExtractedFeatures) -> str:
        """
        Estimate overall project scope.
        """
        feature_count = len(result.features)
        module_count = len(result.modules)
        integration_count = len(result.integrations)
        
        scope_score = (
            feature_count * 2 +
            module_count * 3 +
            integration_count * 4
        )
        
        if scope_score > 100:
            return 'enterprise'
        elif scope_score > 50:
            return 'large'
        elif scope_score > 25:
            return 'medium'
        else:
            return 'small'
    
    def _extract_technologies(self, text: str) -> List[str]:
        """
        Extract mentioned technologies from text.
        """
        technologies = []
        tech_keywords = [
            'python', 'java', 'javascript', 'typescript', 'node.js', 'react',
            'angular', 'vue', 'django', 'flask', 'spring', 'aws', 'azure',
            'gcp', 'docker', 'kubernetes', 'mongodb', 'postgresql', 'mysql',
            'redis', 'elasticsearch', 'graphql', 'rest api', 'microservices'
        ]
        
        for tech in tech_keywords:
            if tech in text:
                technologies.append(tech.title())
        
        return technologies
    
    def _extract_user_roles(self, text: str) -> List[str]:
        """
        Extract user roles from text.
        """
        roles = set()
        role_patterns = [
            r'(?i)(?:as\s+an?\s+)(\w+(?:\s+\w+)?)\s*,?\s*(?:i|user)',
            r'(?i)(\w+)\s+user',
            r'(?i)(\w+)\s+role',
            r'(?i)(\w+)\s+admin(?:istrator)?',
        ]
        
        for pattern in role_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                role = match.strip().title()
                if len(role) > 2 and len(role) < 30:
                    roles.add(role)
        
        # Common roles
        common_roles = ['admin', 'user', 'customer', 'vendor', 'manager', 'staff']
        for role in common_roles:
            if role in text.lower():
                roles.add(role.title())
        
        return list(roles)[:10]
    
    def _extract_security_requirements(self, text: str) -> List[str]:
        """
        Extract security-related requirements.
        """
        security_keywords = [
            'authentication', 'authorization', 'encryption', 'ssl', 'https',
            'gdpr', 'hipaa', 'pci', 'compliance', 'audit', 'logging',
            'two-factor', '2fa', 'mfa', 'oauth', 'jwt', 'rbac', 'acl'
        ]
        
        requirements = []
        sentences = self.nlp.tokenize_sentences(text)
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(kw in sentence_lower for kw in security_keywords):
                requirements.append(sentence[:150])
        
        return requirements[:10]
    
    def _extract_performance_requirements(self, text: str) -> List[str]:
        """
        Extract performance-related requirements.
        """
        perf_keywords = [
            'performance', 'response time', 'latency', 'throughput',
            'concurrent users', 'scalability', 'load', 'availability',
            'uptime', 'sla', 'milliseconds', 'seconds'
        ]
        
        requirements = []
        sentences = self.nlp.tokenize_sentences(text)
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(kw in sentence_lower for kw in perf_keywords):
                requirements.append(sentence[:150])
        
        return requirements[:10]
    
    def _calculate_confidence(self, result: ExtractedFeatures, 
                             parsed_doc: ParsedDocument) -> float:
        """
        Calculate confidence score for the extraction.
        """
        scores = []
        
        # Factor 1: Document length
        if parsed_doc.word_count > 1000:
            scores.append(1.0)
        elif parsed_doc.word_count > 500:
            scores.append(0.8)
        elif parsed_doc.word_count > 100:
            scores.append(0.5)
        else:
            scores.append(0.3)
        
        # Factor 2: Number of features extracted
        feature_count = len(result.features)
        if feature_count > 10:
            scores.append(1.0)
        elif feature_count > 5:
            scores.append(0.7)
        else:
            scores.append(0.4)
        
        # Factor 3: Sections identified
        section_count = len(parsed_doc.sections)
        if section_count > 5:
            scores.append(1.0)
        elif section_count > 2:
            scores.append(0.7)
        else:
            scores.append(0.4)
        
        return sum(scores) / len(scores)


def extract_features(parsed_doc: ParsedDocument) -> ExtractedFeatures:
    """
    Convenience function for extracting features from a parsed document.
    """
    extractor = FeatureExtractor()
    return extractor.extract(parsed_doc)