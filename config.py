"""
Configuration and Constants for SRS Analyzer
Contains all multipliers, keywords, and configuration parameters
"""

# =============================================================================
# COST CONFIGURATION (All amounts in INR)
# =============================================================================

BASE_COST_PER_FEATURE = 10000  # Base cost per feature in INR

# Complexity Multipliers
COMPLEXITY_MULTIPLIERS = {
    'low': 1.0,
    'medium': 1.5,
    'high': 2.5,
    'very_high': 3.5
}

# Platform Multipliers
PLATFORM_MULTIPLIERS = {
    'web': 1.0,
    'mobile_android': 1.2,
    'mobile_ios': 1.3,
    'mobile_both': 1.8,
    'web_and_mobile': 2.2,
    'desktop': 1.1,
    'cross_platform': 2.5
}

# UI Complexity Multipliers
UI_COMPLEXITY_MULTIPLIERS = {
    'basic': 1.0,
    'standard': 1.2,
    'advanced': 1.5,
    'premium': 2.0,
    'custom': 2.5
}

# Integration Costs (Fixed costs in INR)
INTEGRATION_COSTS = {
    'payment_gateway': 50000,
    'sms_gateway': 15000,
    'email_service': 10000,
    'push_notifications': 20000,
    'social_login': 25000,
    'maps_integration': 30000,
    'analytics': 15000,
    'cloud_storage': 25000,
    'video_streaming': 75000,
    'chat_realtime': 60000,
    'ai_ml_integration': 100000,
    'blockchain': 150000,
    'iot_integration': 80000,
    'third_party_api': 20000,
    'crm_integration': 40000,
    'erp_integration': 60000,
    'authentication_oauth': 30000,
    'biometric': 45000,
}

# =============================================================================
# KEYWORD DICTIONARIES FOR NLP EXTRACTION
# =============================================================================

# Feature-related keywords
FEATURE_KEYWORDS = [
    'feature', 'functionality', 'capability', 'module', 'component',
    'system shall', 'the system must', 'user can', 'user should',
    'ability to', 'support for', 'enable', 'allow', 'provide',
    'implement', 'integrate', 'manage', 'handle', 'process',
    'display', 'generate', 'create', 'update', 'delete', 'view',
    'search', 'filter', 'sort', 'export', 'import', 'upload', 'download',
    'authenticate', 'authorize', 'validate', 'verify', 'notify',
    'report', 'dashboard', 'analytics', 'track', 'monitor'
]

# Complexity indicators
COMPLEXITY_INDICATORS = {
    'high': [
        'machine learning', 'artificial intelligence', 'ai', 'ml',
        'real-time', 'realtime', 'real time', 'concurrent',
        'distributed', 'microservices', 'blockchain', 'encryption',
        'high availability', 'scalable', 'performance critical',
        'complex algorithm', 'optimization', 'neural network',
        'deep learning', 'natural language processing', 'nlp',
        'computer vision', 'big data', 'data mining', 'predictive',
        'recommendation engine', 'multi-tenant', 'enterprise',
        'high security', 'compliance', 'hipaa', 'pci-dss', 'gdpr'
    ],
    'medium': [
        'integration', 'api', 'rest', 'graphql', 'websocket',
        'notification', 'authentication', 'authorization', 'oauth',
        'payment', 'transaction', 'workflow', 'approval',
        'scheduling', 'calendar', 'mapping', 'geolocation',
        'file management', 'document', 'reporting', 'analytics',
        'dashboard', 'multi-language', 'localization', 'caching',
        'queue', 'background job', 'batch processing'
    ],
    'low': [
        'static', 'simple', 'basic', 'crud', 'form',
        'list', 'view', 'display', 'landing page', 'brochure',
        'contact form', 'about page', 'faq', 'terms', 'privacy'
    ]
}

# Platform detection keywords
PLATFORM_KEYWORDS = {
    'web': [
        'web application', 'website', 'web app', 'browser',
        'responsive', 'spa', 'single page', 'web portal',
        'react', 'angular', 'vue', 'html', 'css', 'javascript'
    ],
    'mobile_android': [
        'android', 'android app', 'google play', 'kotlin', 'java android'
    ],
    'mobile_ios': [
        'ios', 'iphone', 'ipad', 'app store', 'swift', 'objective-c'
    ],
    'mobile_both': [
        'mobile app', 'mobile application', 'react native', 'flutter',
        'cross-platform mobile', 'ionic', 'xamarin'
    ],
    'desktop': [
        'desktop application', 'windows app', 'mac app', 'electron',
        'desktop software'
    ]
}

# UI Complexity keywords
UI_KEYWORDS = {
    'premium': [
        'animation', 'animated', '3d', 'three dimensional',
        'custom design', 'brand guidelines', 'design system',
        'interactive', 'immersive', 'parallax', 'motion design',
        'micro-interactions', 'custom illustrations', 'video background'
    ],
    'advanced': [
        'dashboard', 'data visualization', 'charts', 'graphs',
        'drag and drop', 'drag-and-drop', 'wysiwyg', 'rich text editor',
        'complex forms', 'multi-step', 'wizard', 'dynamic ui'
    ],
    'standard': [
        'responsive', 'mobile friendly', 'user friendly',
        'clean design', 'modern ui', 'material design', 'bootstrap'
    ],
    'basic': [
        'simple ui', 'minimal', 'basic design', 'template based',
        'simple forms', 'basic layout'
    ]
}

# Integration detection keywords
INTEGRATION_KEYWORDS = {
    'payment_gateway': [
        'payment', 'razorpay', 'stripe', 'paypal', 'paytm',
        'payment gateway', 'online payment', 'card payment',
        'upi', 'wallet', 'checkout', 'billing', 'subscription payment'
    ],
    'sms_gateway': [
        'sms', 'text message', 'otp', 'twilio', 'msg91',
        'sms notification', 'sms verification'
    ],
    'email_service': [
        'email', 'sendgrid', 'mailchimp', 'ses', 'smtp',
        'email notification', 'newsletter', 'email marketing'
    ],
    'push_notifications': [
        'push notification', 'firebase', 'fcm', 'apns',
        'mobile notification', 'in-app notification'
    ],
    'social_login': [
        'social login', 'facebook login', 'google login',
        'twitter login', 'linkedin login', 'social authentication'
    ],
    'maps_integration': [
        'google maps', 'maps', 'location', 'geolocation',
        'gps', 'navigation', 'route', 'mapbox'
    ],
    'analytics': [
        'analytics', 'google analytics', 'mixpanel', 'amplitude',
        'tracking', 'user behavior', 'metrics'
    ],
    'cloud_storage': [
        's3', 'aws', 'cloud storage', 'file storage',
        'azure blob', 'google cloud storage', 'cdn'
    ],
    'video_streaming': [
        'video streaming', 'live streaming', 'video call',
        'webrtc', 'video conference', 'youtube integration'
    ],
    'chat_realtime': [
        'chat', 'messaging', 'real-time chat', 'instant messaging',
        'websocket', 'socket.io', 'chatbot'
    ],
    'ai_ml_integration': [
        'ai', 'ml', 'machine learning', 'artificial intelligence',
        'prediction', 'recommendation', 'nlp', 'computer vision'
    ],
    'blockchain': [
        'blockchain', 'smart contract', 'ethereum', 'web3',
        'cryptocurrency', 'nft', 'decentralized'
    ],
    'authentication_oauth': [
        'oauth', 'sso', 'single sign-on', 'jwt', 'token',
        'authentication', 'auth0', 'okta', 'keycloak'
    ],
    'biometric': [
        'biometric', 'fingerprint', 'face recognition',
        'face id', 'touch id', 'iris scan'
    ]
}

# Module detection patterns
MODULE_PATTERNS = [
    r'module\s*[:\-]?\s*(\w+[\w\s]*)',
    r'(\w+)\s+module',
    r'(\w+)\s+management',
    r'(\w+)\s+system',
    r'(\w+)\s+portal',
    r'(\w+)\s+panel'
]

# =============================================================================
# TEAM ALLOCATION CONFIGURATION
# =============================================================================

TEAM_ROLES = {
    'project_manager': {'rate_per_week': 40000, 'min_features': 10},
    'tech_lead': {'rate_per_week': 50000, 'min_features': 15},
    'senior_developer': {'rate_per_week': 35000, 'features_per_dev': 5},
    'junior_developer': {'rate_per_week': 20000, 'features_per_dev': 3},
    'ui_ux_designer': {'rate_per_week': 30000, 'min_ui_complexity': 'standard'},
    'qa_engineer': {'rate_per_week': 25000, 'ratio_to_dev': 0.5},
    'devops_engineer': {'rate_per_week': 35000, 'min_complexity': 'medium'},
    'business_analyst': {'rate_per_week': 35000, 'min_features': 20}
}

# Development phases with time allocation percentages
DEVELOPMENT_PHASES = {
    'requirement_analysis': 0.10,
    'design': 0.15,
    'development': 0.45,
    'testing': 0.20,
    'deployment': 0.05,
    'buffer': 0.05
}

# =============================================================================
# SUGGESTIONS CONFIGURATION
# =============================================================================

COST_REDUCTION_SUGGESTIONS = [
    {
        'condition': 'platform_both',
        'suggestion': 'Consider using cross-platform frameworks like Flutter or React Native to reduce costs by 20-30%',
        'potential_saving': 0.25
    },
    {
        'condition': 'high_ui_complexity',
        'suggestion': 'Consider using pre-built UI component libraries to reduce design costs',
        'potential_saving': 0.15
    },
    {
        'condition': 'many_integrations',
        'suggestion': 'Evaluate if all integrations are essential for MVP. Consider phased integration approach',
        'potential_saving': 0.20
    },
    {
        'condition': 'high_complexity',
        'suggestion': 'Break down complex features into phases. Implement core features first',
        'potential_saving': 0.30
    }
]

# Risk indicators
RISK_INDICATORS = {
    'high': [
        'no timeline specified', 'unclear requirements', 'multiple platforms',
        'complex integrations', 'ai/ml features', 'real-time requirements'
    ],
    'medium': [
        'third-party dependencies', 'custom design', 'multiple user roles',
        'reporting features'
    ],
    'low': [
        'standard features', 'single platform', 'basic ui'
    ]
}