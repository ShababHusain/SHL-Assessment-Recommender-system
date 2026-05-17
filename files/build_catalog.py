"""
Script to build SHL assessment catalog.
In production, this would scrape the actual SHL catalog.
This version uses realistic sample data for development.
"""

import json
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sample SHL assessment catalog data
# In production, this would be scraped from https://www.shl.com/en/
SAMPLE_CATALOG = [
    {
        "name": "Verify G+",
        "description": "Ability test assessing general mental ability, verbal reasoning, and numerical reasoning for entry-level roles.",
        "url": "https://www.shl.com/en/solutions/assessments/verify/",
        "duration_minutes": 12,
        "category": "Ability",
        "test_type": "Cognitive Ability"
    },
    {
        "name": "Verify G+ Interactive",
        "description": "Interactive version of Verify G+ with real-world scenarios for graduate and professional roles.",
        "url": "https://www.shl.com/en/solutions/assessments/verify-interactive/",
        "duration_minutes": 25,
        "category": "Ability",
        "test_type": "Cognitive Ability"
    },
    {
        "name": "Cubic Reasoning",
        "description": "Spatial reasoning test assessing ability to visualize and manipulate 3D objects.",
        "url": "https://www.shl.com/en/solutions/assessments/cubic-reasoning/",
        "duration_minutes": 10,
        "category": "Ability",
        "test_type": "Spatial Reasoning"
    },
    {
        "name": "OPQ32i",
        "description": "Personality assessment measuring 32 personality dimensions relevant to work performance and fit.",
        "url": "https://www.shl.com/en/solutions/assessments/opq32i/",
        "duration_minutes": 25,
        "category": "Personality",
        "test_type": "Personality Assessment"
    },
    {
        "name": "OPQ32r+",
        "description": "Revised OPQ32 with real-world scenarios, enhanced clarity, and cultural fairness.",
        "url": "https://www.shl.com/en/solutions/assessments/opq32r/",
        "duration_minutes": 30,
        "category": "Personality",
        "test_type": "Personality Assessment"
    },
    {
        "name": "Motivational Fit",
        "description": "Assessment of work motivation, job satisfaction factors, and organizational fit.",
        "url": "https://www.shl.com/en/solutions/assessments/motivational-fit/",
        "duration_minutes": 20,
        "category": "Motivation",
        "test_type": "Motivation Assessment"
    },
    {
        "name": "General Sales Aptitude (GSA)",
        "description": "Sales-specific cognitive ability assessment measuring skills essential for sales roles.",
        "url": "https://www.shl.com/en/solutions/assessments/general-sales-aptitude/",
        "duration_minutes": 20,
        "category": "Sales",
        "test_type": "Role-Specific Ability"
    },
    {
        "name": "CPQ+ (Customer Service Profile)",
        "description": "Behavioral assessment for customer service roles measuring customer orientation and service mindset.",
        "url": "https://www.shl.com/en/solutions/assessments/cpq-plus/",
        "duration_minutes": 15,
        "category": "Service",
        "test_type": "Behavioral Assessment"
    },
    {
        "name": "Talent Indicator",
        "description": "Measures key competencies for graduate and entry-level recruitment: learning, adaptability, problem-solving.",
        "url": "https://www.shl.com/en/solutions/assessments/talent-indicator/",
        "duration_minutes": 18,
        "category": "Graduate",
        "test_type": "Competency Assessment"
    },
    {
        "name": "Safety Culture Questionnaire (SCQ)",
        "description": "Assesses individual attitudes toward workplace safety and safety culture fit.",
        "url": "https://www.shl.com/en/solutions/assessments/safety-culture-questionnaire/",
        "duration_minutes": 12,
        "category": "Safety",
        "test_type": "Culture Assessment"
    },
    {
        "name": "Papi 3",
        "description": "Personality and preferences inventory for high-level executives and leadership positions.",
        "url": "https://www.shl.com/en/solutions/assessments/papi/",
        "duration_minutes": 45,
        "category": "Executive",
        "test_type": "Executive Assessment"
    },
    {
        "name": "Microsoft Office Skills",
        "description": "Technical skills assessment for Microsoft Office proficiency (Word, Excel, PowerPoint, Outlook).",
        "url": "https://www.shl.com/en/solutions/assessments/microsoft-office/",
        "duration_minutes": 30,
        "category": "Technical",
        "test_type": "Technical Skills"
    },
    {
        "name": "Java Programming",
        "description": "Technical assessment for Java development skills including OOP, design patterns, and best practices.",
        "url": "https://www.shl.com/en/solutions/assessments/java-programming/",
        "duration_minutes": 45,
        "category": "Technical",
        "test_type": "Technical Skills"
    },
    {
        "name": "Python Programming",
        "description": "Technical assessment for Python development skills including data structures and algorithm knowledge.",
        "url": "https://www.shl.com/en/solutions/assessments/python-programming/",
        "duration_minutes": 45,
        "category": "Technical",
        "test_type": "Technical Skills"
    },
    {
        "name": "SQL Database Skills",
        "description": "Technical skills assessment for SQL database design, querying, and optimization.",
        "url": "https://www.shl.com/en/solutions/assessments/sql-database/",
        "duration_minutes": 40,
        "category": "Technical",
        "test_type": "Technical Skills"
    },
    {
        "name": "Project Management Competency",
        "description": "Assessment for project management skills, leadership, and PRINCE2/PMP knowledge.",
        "url": "https://www.shl.com/en/solutions/assessments/project-management/",
        "duration_minutes": 35,
        "category": "Management",
        "test_type": "Competency Assessment"
    },
    {
        "name": "Leadership Potential",
        "description": "Identifies high-potential talent with leadership capabilities and executive presence.",
        "url": "https://www.shl.com/en/solutions/assessments/leadership-potential/",
        "duration_minutes": 40,
        "category": "Leadership",
        "test_type": "Leadership Assessment"
    },
    {
        "name": "Numerical Reasoning",
        "description": "Advanced numerical reasoning test for finance, accounting, and analytical roles.",
        "url": "https://www.shl.com/en/solutions/assessments/numerical-reasoning/",
        "duration_minutes": 18,
        "category": "Ability",
        "test_type": "Cognitive Ability"
    },
    {
        "name": "Verbal Reasoning",
        "description": "Reading comprehension and verbal reasoning for roles requiring language and analysis skills.",
        "url": "https://www.shl.com/en/solutions/assessments/verbal-reasoning/",
        "duration_minutes": 19,
        "category": "Ability",
        "test_type": "Cognitive Ability"
    },
    {
        "name": "Logical Reasoning",
        "description": "Logical and abstract reasoning assessment for analytical and problem-solving roles.",
        "url": "https://www.shl.com/en/solutions/assessments/logical-reasoning/",
        "duration_minutes": 20,
        "category": "Ability",
        "test_type": "Cognitive Ability"
    }
]


def build_catalog(output_path: str = "data/catalog.json"):
    """
    Build and save catalog to JSON file.
    
    Args:
        output_path: Path to save catalog.json
    """
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    
    # Save catalog
    with open(output_path, "w") as f:
        json.dump(SAMPLE_CATALOG, f, indent=2)
    
    logger.info(f"✓ Catalog built: {len(SAMPLE_CATALOG)} assessments saved to {output_path}")
    
    return SAMPLE_CATALOG


def load_catalog(catalog_path: str = "data/catalog.json") -> list:
    """Load catalog from JSON file."""
    if not os.path.exists(catalog_path):
        logger.warning(f"Catalog not found at {catalog_path}, building...")
        return build_catalog(catalog_path)
    
    with open(catalog_path, "r") as f:
        catalog = json.load(f)
    
    logger.info(f"✓ Loaded {len(catalog)} assessments from {catalog_path}")
    return catalog


if __name__ == "__main__":
    build_catalog()
